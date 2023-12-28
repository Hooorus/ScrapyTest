#!/usr/bin/env python3
import scrapy

# Note: 对应入口，不需要record；
class BingchengItem(scrapy.Item):
    disease = scrapy.Field()
    disease_href = scrapy.Field()

# Note: 对应每个疾病，包括其翻页，不需要record；
class DiseaseItem(scrapy.Item):
    disease = scrapy.Field()
    answer_href = scrapy.Field()

# Note: 对应每个回答页面，需要录制
class AnswerItem(scrapy.Item):
    url = scrapy.Field()
    disease = scrapy.Field()
    diseaseinfo = scrapy.Field()
    suggestions = scrapy.Field()
