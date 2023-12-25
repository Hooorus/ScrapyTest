import scrapy
from myFirstSpider.items import TencentMedItem


class TencentMedSpider(scrapy.Spider):
    name = "tencent_med_crawler"

    allowed_domains = [
        "www.xywy.com",
        "baike.qq.com",
        "baidu.com"
    ]

    # start_urls = ["https://h5.baike.qq.com/mobile/home.html?VNK=bde7672d"]
    # start_urls = ["https://www.xywy.com/"]
    start_urls = ["https://www.baidu.com/"]

    def parse(self, response):
        # filename = "tencent_med.json"
        # open(filename, 'wb+').write(response.body)

        # 存放爬取结果
        allocations = []

        # 各类xpath
        # response_xpath = ""

        #
        # response_xpath = "//ul[@class='art-left']/li/a/div[@class='txt']//text()"
        response_xpath = "//ul"

        # 百度
        response_xpath = "//ul[@class='s-hotsearch-content']/li/a/span[@class='title-content-title']/text()"

        # response_xpath = "//div[@class='disease-list']"
        # response_xpath = "//ul[@class='art-left']"
        # name_xpath = "//a[@class='one']"
        # 弹窗会搞坏搜索目录
        for unit in response.xpath(response_xpath):
            print("-------------")
            print(unit)
            # 暂存区
            allocation = TencentMedItem()

            # 提取相应内容到指定bean内
            name = unit.extract()
            # title = unit.xpath(title_xpath).extract()
            # img = unit.xpath(img_xpath).extract()
            # content = unit.xpath(name_xpath).extract()
            # publisher = unit.xpath(publisher_xpath).extract()

            # xpath返回的是一个包含元素的列表
            allocation['name'] = name[0]
            # allocation['title'] = title[0]
            # allocation['img'] = img[0]
            # allocation['content'] = content[0]
            # allocation['publisher'] = publisher[0]

            allocations.append(allocation)

        return allocations
