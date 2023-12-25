# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

# 项目的目标文件，用来保存爬取到的数据，像dict

import scrapy


class ItcastItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    title = scrapy.Field()
    info = scrapy.Field()


class TencentMedItem(scrapy.Item):
    name = scrapy.Field()
    title = scrapy.Field()
    img = scrapy.Field()
    content = scrapy.Field()
    publisher = scrapy.Field()
