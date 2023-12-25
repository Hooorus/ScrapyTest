# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

# 项目管道文件

from itemadapter import ItemAdapter


class MyfirstspiderPipeline:
    def process_item(self, item, spider):
        return item
