from scrapy.cmdline import execute
from myFirstSpider.spiders.nine_nine_com_cn import NineNineComCnSpider
import os
import sys

from scrapy.crawler import CrawlerProcess

if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    # scrapy crawl <spider_name> <output: -o result.json>
    execute(['scrapy', 'crawl', 'spring_rain_doctor_crawler', '-o result.csv'])


# 定义要运行的函数
# def run_my_function():
#     # 创建 CrawlerProcess
#     process = CrawlerProcess()
#
#     # 启动爬虫，不需要使用完整的爬虫流程，只需创建爬虫实例即可
#     spider = NineNineComCnSpider()
#     process.crawl(spider)
#
#     # 获取爬虫实例，调用需要运行的函数
#     spider_instance = process.create_crawler(spider)
#     spider_function = getattr(spider_instance.spidercls, 'parse_subpage', None)
#
#     if callable(spider_function):
#         spider_function()
#
#     # 启动 Scrapy 进程
#     process.start()
#
#
# # 运行函数
# run_my_function()
