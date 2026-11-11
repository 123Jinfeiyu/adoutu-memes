# adoutu-memes · 爱斗图表情包爬虫（Scrapy）

爬取 www.adoutu.com 的表情包（图片直链 + 标题 + 来源栏目），零登录、零 JS 渲染。

## 快速开始

```bash
# 用系统 Python（Scrapy 2.19 已装好）
cd C:\Users\Administrator\WorkBuddy\Spider\adoutu-memes
C:\Users\Administrator\AppData\Local\Programs\Python\Python313\python.exe -m scrapy crawl adoutu -a pages=5
```

产出在 `./memes/`：图片按原始文件名保存，`index.csv`（UTF-8 BOM，Excel 直接开）记录 `文件名, 标题, 来源栏目`。

## 参数

| 参数 | 默认 | 说明 |
|---|---|---|
| `ids` | `2757,57,58` | 起始栏目页（`/picture/list/{id}` 的 id），逗号分隔 |
| `pages` | `3` | 每个起点沿「下一页」连抓多少页（每页 40 张） |
| `out` | `./memes` | 输出目录 |

示例：

```bash
# 从 2757 往后抓 20 页（约 800 张）
python -m scrapy crawl adoutu -a ids=2757 -a pages=20

# 输出到 D 盘
python -m scrapy crawl adoutu -a pages=5 -a out=D:/memes
```

## 站点结构（2026-10-30 实测）

- 列表页 `http://www.adoutu.com/picture/list/{id}` 是 Next.js SSR，40 张 `<img src="https://img.adoutu.com/picture/*.jpg">` 直出
- 翻页 = 栏目 id 递增/递减（页面「上一页/下一页」链接），`?page=` 无效
- 图片 CDN 校验 Referer：请求必须带 `Referer: http://www.adoutu.com/`，否则 403（已在 settings 配好）
- robots.txt：`Allow: /`，仅禁 `/api/` —— 列表页与图片都在允许范围

## 已适配的坑

1. **Scrapy 2.13+ 移除了 `start_requests`** —— 用 `async def start(self)`
2. **cb_kwargs 会作为关键字参数传给回调** —— `save_image(self, response, title="", list_id="")` 必须接住
3. **图片 CDN Referer 校验** —— `DEFAULT_REQUEST_HEADERS` 里带 Referer

## 礼貌设置

`DOWNLOAD_DELAY=0.5`、并发 4、AutoThrottle 开启、遵守 robots.txt。这是个人小站，别调大并发把它打挂。
