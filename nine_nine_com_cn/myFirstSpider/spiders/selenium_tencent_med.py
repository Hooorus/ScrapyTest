import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from nine_nine_com_cn.myFirstSpider.items import TencentMedItem


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
        # 父path
        response_xpath = "//div[@class='feed-item']/div[@class='feed-item-card']/div[@class='card-article']"
        # 子path，以./开头，为相对位置
        img_xpath = "./div[@class='img-wrap']/img[@class='img']"
        title_xpath = "./div[@class='feed-doc-info']/div[@class='title']/span[@class='txt']"
        publisher_xpath = "./div[@class='feed-doc-info']/div[@class='source-wrap']/span"

        # 得到响应的url
        self.driver.get(response.url)
        self.log("-------------response.url------------\n%s" % response.url)

        try:
            # 使用显式等待，等待元素加载完成，10秒钟
            elements = WebDriverWait(self.driver, 5).until(
                # presence_of_all_elements_located: 获取所有匹配此xpath的元素
                expected_conditions.presence_of_all_elements_located((By.XPATH, response_xpath))
            )

            self.log("-------------elements-------------\n%s" % elements)

            # 暂存区
            allocation = TencentMedItem()

            # 遍历所有找到的元素，这里meta_element是几个不同的数据，输出就输出len(elements)个数据
            for meta_element in elements:

                print("meta_element: ", type(meta_element))
                print("elements: ", type(elements))

                print("len of elements: ", len(elements))

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
                    allocation['title'] = title_element.text

                # 遍历img
                for img_element in img_elements:
                    self.log(
                        "-------------img_element.get_attribute('src')-------------\n%s" % img_element.get_attribute(
                            "data-src"))
                    allocation['img'] = img_element.get_attribute("data-src")

                # 遍历publisher
                for publisher_element in publisher_elements:
                    self.log("-------------publisher_element.text-------------\n%s" % publisher_element.text)
                    allocation['publisher'] = publisher_element.text

                print("allocation: ", allocation)

                yield allocation

        except Exception as e:
            print(f"Error: {e}")
