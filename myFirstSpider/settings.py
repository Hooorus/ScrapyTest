# Scrapy settings for myFirstSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# 项目设置文件

BOT_NAME = "myFirstSpider"

SPIDER_MODULES = ["myFirstSpider.spiders"]
NEWSPIDER_MODULE = "myFirstSpider.spiders"


# 添加爬取时候的用户代理
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"

# Obey robots.txt rules
# 第二处变化，将True改为False，表示访问时不按照君子协议进行数据采集
ROBOTSTXT_OBEY = False

# 日志等级为DEBUG才显示
LOG_LEVEL = 'DEBUG'

# 激活selenium中间件，需要把第一个改成这个项目名称（不是爬虫名称）
DOWNLOADER_MIDDLEWARES = {
   'myFirstSpider.middlewares.SeleniumMiddleware': 543,
}

# 设置最大爬取数量
MAX_CRAWL_DATA_XS = 25
MAX_CRAWL_DATA_S = 50
MAX_CRAWL_DATA_M = 100
MAX_CRAWL_DATA_L = 500
MAX_CRAWL_DATA_XL = 1000
MAX_CRAWL_DATA_2XL = 2000
MAX_CRAWL_DATA_3XL = 3000
MAX_CRAWL_DATA_4XL = 4000
MAX_CRAWL_DATA_5XL = 5000


# 自定义值

# 随机下载延迟在1到3秒之间
# DOWNLOAD_DELAY = (2, 5)
# 启用或禁用对 DOWNLOAD_DELAY 的随机化
# RANDOMIZE_DOWNLOAD_DELAY = True
# 每个域名同时只能进行一个请求
# CONCURRENT_REQUESTS_PER_DOMAIN = 1
# 全局只进行一个请求
# CONCURRENT_REQUESTS = 1

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "myFirstSpider.middlewares.MyfirstspiderSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "myFirstSpider.middlewares.MyfirstspiderDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "myFirstSpider.pipelines.MyfirstspiderPipeline": 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
