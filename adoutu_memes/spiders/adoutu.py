# -*- coding: utf-8 -*-
"""
爱斗图（www.adoutu.com）表情包爬虫

页面结构（2026-10-30 实测）：
- 列表页 /picture/list/{listId} 是 Next.js SSR，40 张 <img src="https://img.adoutu.com/picture/xxx.jpg"> 直出
- 翻页 = listId 递增/递减（页面里的「上一页/下一页」链接）
- 图片 CDN（img.adoutu.com）校验 Referer，必须带 http://www.adoutu.com/ 前缀，否则 403
- robots.txt：Allow: /，仅 Disallow: /api/（列表页允许抓取）

用法：
    scrapy crawl adoutu -a pages=5                      # 从默认起点各往后翻 5 页
    scrapy crawl adoutu -a pages=10 -a ids=2757,57,58   # 自定义起点
    scrapy crawl adoutu -a ids=2757 -a pages=3 -a out=D:/memes
"""

import csv
import os
import re

import scrapy

IMG_RE = re.compile(r"^https?://img\.adoutu\.com/picture/[A-Za-z0-9._-]+$")
LIST_RE = re.compile(r"/picture/list/(\d+)")
DEFAULT_START_IDS = ["2757", "57", "58"]  # 截图里的三个栏目


class AdoutuSpider(scrapy.Spider):
    name = "adoutu"

    custom_settings = {
        # 图片下载请求必须带的头（CDN 校验 Referer）
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "http://www.adoutu.com/",
        },
    }

    def __init__(self, pages="3", ids=None, out=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 每个起点往两边各翻多少页（listId 连续，一页 40 张，别贪多）
        self.max_pages = max(1, int(pages))
        self.start_ids = [i.strip() for i in ids.split(",")] if ids else list(DEFAULT_START_IDS)
        self.out_dir = os.path.abspath(out) if out else os.path.join(os.getcwd(), "memes")
        os.makedirs(self.out_dir, exist_ok=True)
        self.visited_lists = set()
        self.parsed_lists = set()
        self.seen_images = set()
        # 记录：文件名, 标题, 来源栏目
        self.index_path = os.path.join(self.out_dir, "index.csv")
        self._csv = csv.writer(open(self.index_path, "w", newline="", encoding="utf-8-sig"))
        self._csv.writerow(["file", "title", "source_list"])

    async def start(self):  # Scrapy 2.13+ 用 start() 取代 start_requests()
        for lid in self.start_ids:
            url = "http://www.adoutu.com/picture/list/%s" % lid
            yield scrapy.Request(url, callback=self.parse, cb_kwargs={"list_id": lid})

    def parse(self, response, list_id, page_no=1):
        # 已解析过的栏目直接跳过（请求级去重由 Scrapy dupefilter 负责）
        if list_id in self.parsed_lists:
            return
        self.parsed_lists.add(list_id)

        # 1) 抽本页 40 张表情直链
        urls = response.xpath(
            '//img[contains(@src, "img.adoutu.com/picture/")]/@src'
        ).getall()
        n = 0
        for u in urls:
            u = u.strip()
            if not IMG_RE.match(u) or u in self.seen_images:
                continue
            self.seen_images.add(u)
            title = (response.xpath(
                '//img[@src="%s"]/@alt' % u
            ).get() or "").strip()
            n += 1
            yield scrapy.Request(
                u,
                callback=self.save_image,
                cb_kwargs={"title": title, "list_id": list_id},
                priority=10,
            )
        self.logger.info("list %s: %d 张新图", list_id, n)

        # 2) 跟「下一页」往 listId 增大的方向翻，最多 max_pages 页
        if page_no >= self.max_pages:
            return
        next_href = response.xpath(
            '//a[text()="下一页"]/@href'
        ).get()
        m = LIST_RE.match(next_href or "")
        if m and m.group(1) not in self.parsed_lists:
            yield scrapy.Request(
                response.urljoin(next_href),
                callback=self.parse,
                cb_kwargs={"list_id": m.group(1), "page_no": page_no + 1},
            )

    def save_image(self, response, title="", list_id=""):
        # 注意：cb_kwargs 会作为关键字参数传进来，签名必须接住
        fname = response.url.rsplit("/", 1)[-1]
        path = os.path.join(self.out_dir, fname)
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(response.body)
        self._csv.writerow([fname, title, list_id])
