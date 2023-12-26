import scrapy
import time
from myFirstSpider.items import TencentMedItem


class TencentMedSpider(scrapy.Spider):
    name = "tencent_med_crawler"

    allowed_domains = [
        "www.xywy.com",
        "h5.baike.qq.com",
        "baidu.com"
    ]

    start_urls = ["https://h5.baike.qq.com/mobile/home.html?VNK=bde7672d"]

    def parse(self, response):

        time.sleep(5)  # 休息5秒钟

        # filename = "tencent_med.json"
        # open(filename, 'wb+').write(response.body)

        # 存放爬取结果
        allocations = []

        print("-------response------")
        print(response)

        # print("-------response.text------")
        # print(response.text)

        # response_xpath = "//div[@class='feed-item']/div[@class='feed-item-card']/div[@class='card-article']/div[@class='img-wrap']/img[@class='img']/@src"
        # response_xpath = "//div[@class='feed-item']/div[@class='feed-item-card']/div[@class='card-article']/div[@class='feed-doc-info']/div[@class='title']/span/text()"
        response_xpath = "//div[@class='feed-item']"

        print("-------response.xpath(response_xpath)------")
        print(response.xpath(response_xpath))


        for unit in response.xpath(response_xpath):
            print("-------unit------")
            print(unit)
            # 暂存区
            allocation = TencentMedItem()

            # 提取相应内容到指定bean内
            name = unit.extract()
            print("-------name------")
            print(name)
            # img = unit.xpath("//div[@class='img-wrap']/img[@class='img']/@src").extract()
            # content = unit.extract()
            # publisher = unit.extract()

            # title = unit.xpath(title_xpath).extract()
            # img = unit.xpath(img_xpath).extract()
            # content = unit.xpath(name_xpath).extract()
            # publisher = unit.xpath(publisher_xpath).extract()

            # xpath返回的是一个包含元素的列表
            allocation['name'] = name
            # allocation['img'] = img
            # allocation['content'] = content
            # allocation['publisher'] = publisher

            allocations.append(allocation)

        return allocations
