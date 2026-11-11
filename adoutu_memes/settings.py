# -*- coding: utf-8 -*-

BOT_NAME = "adoutu_memes"

SPIDER_MODULES = ["adoutu_memes.spiders"]
NEWSPIDER_MODULE = "adoutu_memes.spiders"

# 礼貌设置：慢一点，别把人家小站打挂
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 4
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 10.0
RETRY_TIMES = 3

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

# 图片 CDN 校验 Referer（ spiders/adoutu.py 的 custom_settings 里也配了一份）
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "http://www.adoutu.com/",
}

# 超时与失败容错
DOWNLOAD_TIMEOUT = 30
HTTPERROR_ALLOWED_CODES = []

LOG_LEVEL = "INFO"

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
