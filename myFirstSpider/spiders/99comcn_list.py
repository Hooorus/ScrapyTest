import csv
import random

import scrapy
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from myFirstSpider.items import NineNineComCnItem


# ------------------------------is_next_button_disabled：没有下一个按钮返回false，有返回true------------------------------
def is_next_button_available(driver):
    # Use Selenium to check if the next button is disabled
    try:
        next_button = WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//div[@id='layui-laypage-1']/a[@class='layui-laypage-next layui-disabled']"))
        )
        # 找到了
        return False
    except TimeoutException:
        # 找不到
        return True


# ------------------------------write_to_file：写入文件模块------------------------------
def write_to_file(raw_data, filename, file_type, write_mode, is_first_use):
    try:
        with open(filename + '.' + file_type, write_mode, newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[''])
            writer.writeheader()
            for url_unit in raw_data:
                writer.writerow({"": url_unit})
            #
            # if not is_first_use:
            #     # TODO 去除行头的url这一行
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False


class SeleniumTencentMedSpider(scrapy.Spider):
    name = "99comcn_list_crawler"
    allowed_domains = ["99.com.cn/"]
    start_urls = ["https://www.99.com.cn/wenda/"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()
        # ------------------------------自定义变量------------------------------
        self.allocations = []  # 装载所有url爬取到的内容
        self.is_first_in_parse = True  # 检验是否第一次进入网页
        self.url_container = []  # 装载所有爬取到的页面url

    # ------------------------------开始加载根页面------------------------------
    def parse(self, response, **kwargs):
        # 得到响应的url
        self.driver.get(response.url)
        self.log(f"-------------response.url------------\n{response.url}")
        self.is_first_in_parse = False
        # ------------------------------第一部分：第一次进入此网站---------------------------------
        first_link_elements = WebDriverWait(self.driver, 10).until(
            # presence_of_all_elements_located: 获取所有匹配此xpath的元素
            expected_conditions.presence_of_all_elements_located(
                (By.XPATH, "//div[@class='isue-list']//a[@class='isue-bt']"))
        )

        # 接下来会有小于等于5个的链接，我需要遍历他们，当然这个parse只做第一层目录的链接搜索，等到搜集完大部分的url后，再发给parse_subpage来处理响应
        for first_link_element in first_link_elements:
            # 获取链接的href属性值
            first_link_element_href = first_link_element.get_attribute("href")
            # 得到拼接的url，并装载到url_container内
            url = response.urljoin(first_link_element_href)
            # 收集到一个页面urls，写入文件
            self.url_container.append(url)
        # 收集到一个页面urls，写入文件
        write_to_file(self.url_container, "result", "csv", "a", True)
        # 写完清空
        self.url_container.clear()

        # ------------------------------第二部分：爬取下一个分页，疯狂循环，直到没有按钮了！！！---------------------------------
        while True:
            # 检查是否有更多的按钮，如果有，那么继续处理
            if is_next_button_available(self.driver):
                # TODO 注意延时（1-5秒随机）
                self.driver.implicitly_wait(random.uniform(1, 5))
                # 调用xhr_to_next_page处理下一个分页
                self.log("-------------start xhr_to_next_page-------------\n")
                # 找到并点击按钮
                next_page_button = self.driver.find_element_by_xpath(
                    "//div[@id='layui-laypage-1']/a[@class='layui-laypage-next']")
                next_page_button.click()
                # TODO 注意延时（1-5秒随机）
                self.driver.implicitly_wait(random.uniform(1, 5))
                self.log(f"-------------next_page_button-------------\n{next_page_button}")
                # 获取渲染后的页面内容
                rendered_html = self.driver.page_source
                # rendered_response = HtmlResponse(url=response.url, body=rendered_html, encoding='utf-8')
                # 从渲染后的响应对象中
                # 创建 Selector----------------------------我他妈直接传给你文本看你收不收吧！！！----------------------------
                re_selectors = scrapy.Selector(text=str(rendered_html))
                # 将渲染后的HTML内容传递给HtmlResponse对象
                re_elements = re_selectors.xpath("//div[@class='isue-list']//a[@class='isue-bt']").extract()
                self.log(f"-------------re_elements-------------\n{re_elements}")

                # ----------------------------开始解析其中的5个超链接元素----------------------------
                # 接下来会有小于等于5个的链接，我需要遍历他们，当然这个parse只做第一层目录的链接搜索，等到搜集完大部分的url后，再发给parse_subpage来处理响应
                for re_element in re_elements:
                    # 获取链接的href属性值
                    re_element_href = scrapy.Selector(text=re_element).xpath("//a/@href").extract_first()
                    self.log(f"-------------re_element_href-------------\n{re_element_href}")
                    # 得到拼接的url，并装载到url_container内
                    url = response.urljoin(re_element_href)
                    self.url_container.append(url)
                    self.log(f"-------------url_container-------------\n{self.url_container}")
                # 收集到一个页面urls，写入文件
                write_to_file(self.url_container, "result", "csv", "a", False)
                # 写完清空
                self.url_container.clear()
            else:
                # write_to_file(self.url_container, "result", "csv", "a")
                # 执行完成所有任务，没有剩余页面了
                self.log("-------------system finished-------------\n")
                break

    # ------------------------------加载与爬取子页面的信息------------------------------
    def parse_subpage(self, response, **kwargs):
        self.log("-------------parse_subpage url-------------\n%s" % response.url)

        # 在新页面等待特定元素加载完成
        self.driver.get(response.url)
        first_link_meta_element = WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH, "//div[@class='dtl-left']"))
        )
        self.log("-------------first_link_meta_element-------------\n%s" % first_link_meta_element)

        # ------------------------------在子页面爬取数据------------------------------
        # 新建NineNineComCnItem类型的bean
        issue = NineNineComCnItem()

        issue_title = first_link_meta_element.find_element_by_xpath(
            "./div[@class='dtl-wrap']/div[@class='dtl-top']/h1").text
        issue_desc = first_link_meta_element.find_element_by_xpath(
            "./div[@class='dtl-wrap']//div[@class='atcle-ms']/p").text
        issue_date = first_link_meta_element.find_element_by_xpath(
            "./div[@class='dtl-wrap']/div[@class='dtl-top']//div[@class='dtl-info']/span[1]").text
        answer_doctor = (str(first_link_meta_element.find_element_by_xpath("//dl[@class='dtl-ys']/dd/b").text) +
                         str(first_link_meta_element.find_element_by_xpath("//dl[@class='dtl-ys']/dd/p").text))
        # TODO 把病情分析和处理意见给我搞掉
        answer_analyze = first_link_meta_element.find_element_by_xpath("//div[@class='dtl-reply']/p").text
        answer_opinion = first_link_meta_element.find_element_by_xpath("//div[@class='dtl-reply']/p[2]").text
        answer_date = first_link_meta_element.find_element_by_xpath(
            "./div[@class='dtl-wrap2']/div[@class='dtl-list']/div[@class='dtl-time']/span").text

        issue['issue_title'] = issue_title
        issue['issue_desc'] = issue_desc
        issue['issue_date'] = issue_date
        issue['answer_doctor'] = answer_doctor
        issue['answer_analyze'] = answer_analyze
        issue['answer_opinion'] = answer_opinion
        issue['answer_date'] = answer_date

        self.log("-------------issue-------------\n%s" % issue)

        yield issue
