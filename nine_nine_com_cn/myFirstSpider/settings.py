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

# 添加爬取时候的用户代理，下面是单个agent和agent list，如果要使用agent list，需要去中间件注册
# USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
USER_AGENT_LIST = [
    # Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    # Firefox
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
    # Edge
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.37',
    # Safari
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    # Opera
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.254',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/76.0.4017.177',
]

# Obey robots.txt rules
# 第二处变化，将True改为False，表示访问时不按照君子协议进行数据采集
ROBOTSTXT_OBEY = False

# 日志等级为DEBUG才显示
LOG_LEVEL = 'DEBUG'

# 激活selenium中间件，需要把第一个改成这个项目名称（不是爬虫名称）
DOWNLOADER_MIDDLEWARES = {
    'myFirstSpider.middlewares.SeleniumMiddleware': 543,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # 禁用默认的Agent（启用Agent List）
    'myFirstSpider.middlewares.RandomUserAgentMiddleware': 400,  # 处理下载中间件时的优先级, 数字越小越高 400>500（默认）
    # 'myFirstSpider.middlewares.RandomProxyMiddleware': 543,  # 处理下载中间件时的优先级, 数字越小越高 400>500（默认）
}

# 启用 MySQL 存储管道
ITEM_PIPELINES = {
    'myFirstSpider.pipelines.MysqlPipeline': 301,  # 300 是处理的优先级，可以根据需要调整
}

PROXY_POOL_URLS = [
    'http://202.182.127.64:3128',
    # 'http://localhost',
    # 'http://proxy3.example.com',
    # 'http://proxy4.example.com',
    # 'http://proxy5.example.com',
]

PROXY_POOL_URL = 'http://leoatchina.duia.us:3128'
# PROXY_POOL_URL = 'http://127.0.0.1:80'

# 99健康网 设置最大爬取数量
MAX_CRAWL_DATA = 10

# 春雨医生 最大爬取医生量(20个一页)
MAX_CRAWL_DOCTOR = 20
# 初始分页位置，建议，从上次爬完的位置（0开始计算）
PAGINATION_BTN_START = 1
# 爬取指定分页数，建议：1，不然很容易404
PAGINATION_BTN_SIZE = 1
# 置scrapy模式，1:断点续传，其他:正常模式，每次全部存储完毕需要清空result.csv
SCRAPY_MODE = 0

# 设置每次休息时间区间
SLEEP_TIME = (3, 8)
CLICK_TIME = (2, 4)

# 随机下载延迟在1到3秒之间
DOWNLOAD_DELAY = 5

# 输出结果格式
FEEDS = {
    'result.csv': {
        'format': 'csv',
        'overwrite': True,
    },
}

# ------------------------DataBase------------------------
MYSQL_HOST = '192.168.1.204'  # IP地址
MYSQL_PORT = 3308  # 端口号，端口号必须为一个数字
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'  # 密码
MYSQL_DB = 'spider01'  # 数据库名

# 启用或禁用对 DOWNLOAD_DELAY 的随机化
# RANDOMIZE_DOWNLOAD_DELAY = True
# 每个域名同时只能进行一个请求
# CONCURRENT_REQUESTS_PER_DOMAIN = 1
# 全局只进行一个请求
# CONCURRENT_REQUESTS = 1

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "myFirstSpider.middlewares.MyfirstspiderSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "myFirstSpider.middlewares.MyfirstspiderDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    "myFirstSpider.pipelines.MyfirstspiderPipeline": 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
