import scrapy
from myFirstSpider.items import ItcastItem

class ItcastSpider(scrapy.Spider):
    # 爬虫的名称，必须唯一
    name = "itcast_crawler"
    # 允许搜索的域名
    allowed_domains = ["itcast.cn"]
    # allowed_domains = ["chinaz.com"]
    # 爬取的url列表，从这里开始抓取数据，其他urls会从这起始url中继承生成
    start_urls = ["http://www.itcast.cn/channel/teacher.shtml"]
    # 使用response.follow实现翻页

    # 解析方法，当每个url下载完成后将被调用，唯一参数为response对象，
    # 负责解析网页数据，提取结构化数据(生成item)
    def parse(self, response):
        # filename = "teacher.json"
        # open(filename, 'wb+').write(response.body)

        # 存放老师信息的集合
        items = []

        for teacher in response.xpath("//div[@class='li_txt']"):

            # new一个ItcastItem对象
            item = ItcastItem()

            # extract -> unicode string
            name = teacher.xpath("h3/text()").extract()
            title = teacher.xpath("h4/text()").extract()
            info = teacher.xpath("p/text()").extract()

            # xpath返回的是一个包含元素的列表
            item['name'] = name[0]
            item['title'] = title[0]
            item['info'] = info[0]

            items.append(item)
            # yield item

        # 直接返回最后数据
        return items
