# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
# useful for handling different item types with a single interface

# 项目管道文件

from itemadapter import ItemAdapter
from scrapy.utils.project import get_project_settings


class MyfirstspiderPipeline:
    def process_item(self, item, spider):
        return item


class MysqlPipeline(object):

    def __init__(self):
        settings = get_project_settings()
        self.host = settings['MYSQL_HOST']
        self.port = settings['MYSQL_PORT']
        self.user = settings['MYSQL_USER']
        self.password = settings['MYSQL_PASSWORD']
        self.database = settings['MYSQL_DB']
        self.connect()

    def connect(self):
        self.conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.database)
        # 通过cursor才能执行sql
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    # -------------------这里写SQL和API名------------------
    def process_item(self, item, spider):
        # 向scrapy_sprain_doc的数据表中插入变量名为title，与url的数据
        sql = ('INSERT INTO scrapy_sprain_doc (issue_title, issue_desc, answer, case_url, already_parsed)'
               ' VALUES ("{}","{}","{}","{}","{}")'
               .format(item['issue_title'], item['issue_desc'],
                       item['answer'], item['case_url'], item['already_parsed']))
        # values = (item['issue_title'], item['issue_desc'], item['answer'], item['case_url'], item['already_parsed'])
        # 执行sql语句
        self.cursor.execute(sql)
        # 提交
        self.conn.commit()
        return item
