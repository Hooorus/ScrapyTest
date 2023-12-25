import scrapy


class chinaz(scrapy.Spider):
    name = "chinaz_crawler"
    allowed_domains = ['chinaz.com']
    # 翻页操作
    start_urls = ["https://sc.chinaz.com/tupian/siwameinvtupian.html"]

    # def parse(self, response):
    #     print("response: ")
    #     print(response)
    #
    #     next_page = "https://sc.chinaz.com/tupian/" + response.xpath("//*[@class='nextpage']/@href").extract_first()
    #     print("next_page", next_page)
    #
    #     yield response.follow(url=next_page, callback=self.parse)

    page = 1

    def parse(self, response):
        next_page = "https://sc.chinaz.com/tupian/" + response.xpath("//*[@class='nextpage']/@href").extract_first()

        if self.page < 3:
            self.page += 1

        yield scrapy.Request(url=next_page, callback=self.parse)
