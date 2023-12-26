import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from myFirstSpider.items import TencentMedItem


class SeleniumTencentMedSpider(scrapy.Spider):
    name = "selenium_tencent_med_crawler"
    allowed_domains = [
        "www.xywy.com",
        "h5.baike.qq.com",
        "baidu.com"
    ]
    start_urls = ["https://h5.baike.qq.com/mobile/home.html?VNK=bde7672d"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def parse(self, response, **kwargs):
        response_xpath = "//div[@class='feed-item']/div[@class='feed-item-card']/div[@class='card-article']"
        img_xpath = "//div[@class='img-wrap']/img[@class='img']"
        title_xpath = "//div[@class='feed-doc-info']/div[@class='title']/span[@class='txt']"
        content_xpath = ""
        publisher_xpath = "//div[@class='feed-doc-info']/div[@class='source-wrap']/span"

        # 存放爬取结果
        # allocations = set()

        # 得到响应的url
        self.driver.get(response.url)
        self.log("-------------response.url------------\n%s" % response.url)

        try:
            # 使用显式等待，等待元素加载完成，10秒钟
            elements = WebDriverWait(self.driver, 10).until(
                # presence_of_all_elements_located: 获取所有匹配此xpath的元素
                expected_conditions.presence_of_all_elements_located((By.XPATH, response_xpath))
            )

            self.log("-------------element-------------\n%s" % elements)

            # 暂存区
            allocation = TencentMedItem()

            # 遍历所有找到的元素
            for meta_element in elements:

                print("len of elements: ", len(elements))

                title_container = []
                img_container = []
                publisher_container = []


                # 取title
                title_elements = meta_element.find_elements(By.XPATH, title_xpath)
                self.log("-------------title_elements-------------\n%s" % title_elements)
                # 取img
                img_elements = meta_element.find_elements(By.XPATH, img_xpath)
                self.log("-------------img_elements-------------\n%s" % img_elements)
                # 取publisher
                publisher_elements = meta_element.find_elements(By.XPATH, publisher_xpath)
                self.log("-------------publisher_elements-------------\n%s" % publisher_elements)

                # 遍历title
                for title_element in title_elements:
                    self.log("-------------title_element.text-------------\n%s" % title_element.text)
                    title_container.append(title_element.text)

                # 遍历img
                for img_element in img_elements:
                    self.log("-------------img_element.get_attribute('src')-------------\n%s" % img_element.get_attribute("src"))
                    img_container.append(img_element.get_attribute("src"))

                # 遍历publisher
                for publisher_element in publisher_elements:
                    self.log("-------------publisher_element.text-------------\n%s" % publisher_element.text)
                    publisher_container.append(publisher_element.text)

                print("title_container: \n", title_container)
                print("img_container: \n", img_container)
                print("publisher_container: \n", publisher_container)


                # self.log("-------------element get_attribute('src')-------------\n%s" % meta_element.get_attribute("src"))
                # allocation['img'] = meta_element.get_attribute("src")

                allocation['title'] = title_container
                allocation['img'] = img_container
                allocation['publisher'] = publisher_container

            return allocation

        except Exception as e:
            print(f"Error: {e}")
