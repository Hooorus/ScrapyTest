import scrapy
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from nine_nine_com_cn.myFirstSpider.items import NineNineComCnItem


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


# ------------------------------is_next_button_disabled：没有下一个按钮返回false，有返回true------------------------------

class SeleniumTencentMedSpider(scrapy.Spider):
    name = "99comcn_crawler"
    allowed_domains = [
        "99.com.cn/"
    ]
    start_urls = ["https://www.99.com.cn/wenda/"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()
        # ------------------------------自定义变量------------------------------
        # 收集所有爬取到的数据
        self.allocations = []
        self.is_first_in_parse = True

    # ------------------------------开始加载根页面------------------------------
    def parse(self, response, **kwargs):
        # 得到响应的url
        self.driver.get(response.url)
        self.log(f"-------------response.url------------\n{response.url}")

        first_link_elements = []
        while True:
            # ------------------------------第三部分：多进入此网站---------------------------------
            # 在parse中获得重渲染后的响应对象
            if not self.is_first_in_parse:
                # TODO 小心meta
                rendered_response = response.text
                self.log(f"-------------rendered_response------------\n{rendered_response}")
                # 从渲染后的响应对象中创建 Selector
                re_selector = scrapy.Selector(text=str(rendered_response))
                re_selector.xpath("//div[@class='isue-list']//a[@class='isue-bt']")
                self.log(f"-------------re_selector-------------\n{re_selector}")
            else:
                self.is_first_in_parse = False
                # ------------------------------第一部分：第一次进入此网站---------------------------------
                first_link_elements = WebDriverWait(self.driver, 10).until(
                    # presence_of_all_elements_located: 获取所有匹配此xpath的元素
                    expected_conditions.presence_of_all_elements_located(
                        (By.XPATH, "//div[@class='isue-list']//a[@class='isue-bt']"))
                )
                # self.log("-------------first_link_elements-------------\n%s" % first_link_elements)

            # 接下来会有小于等于5个的链接，我需要遍历他们，当然这个parse只做第一层目录的链接搜索，第二层交给parse_subpage
            for first_link_element in first_link_elements:
                # self.log("-------------first_link_element-------------\n%s" % first_link_element)

                # 获取链接的href属性值
                first_link_element_href = first_link_element.get_attribute("href")
                # 得到拼接的url
                url = response.urljoin(first_link_element_href)
                self.log(f"-------------url-------------\n{url}")

                # 使用Request对象发起请求，并指定回调函数为parse_subpage，跳转到parse_subpage函数
                yield scrapy.Request(url, callback=self.parse_subpage, meta={'driver': self.driver}, dont_filter=True)

            # ------------------------------第二部分：爬取下一个分页---------------------------------

            # 检查是否有更多的按钮，如果有，那么继续处理
            if is_next_button_available(self.driver):
                # 调用xhr_to_next_page处理下一个分页

                self.log("-------------start xhr_to_next_page-------------\n")
                yield self.xhr_to_next_page(response)
                self.log("-------------finish xhr_to_next_page-------------\n")

                # 另一种解决办法
                # next_page_button = self.driver.find_element_by_xpath(
                #     "//div[@id='layui-laypage-1']/a[@class='layui-laypage-next']")
                # next_page_button.click()
                # TODO 小心时间
                # self.driver.implicitly_wait(3)
                # rendered_html = self.driver.page_source
                # rendered_response = HtmlResponse(url=response.url, body=rendered_html, encoding='utf-8')
                # self.parse(rendered_response)

                # self.log(f"-------------{result}-------------\n")
            else:
                # 执行完成所有任务，没有剩余页面了
                self.log("-------------system finished-------------\n")
                break

        # yield scrapy.Request()
        # ------------------------------第一部分：第一次进入此网站结束---------------------------------

        # ------------------------------加载根页面结束------------------------------

    # ------------------------------发送xhr请求去调用下一个页面------------------------------
    def xhr_to_next_page(self, response, **kwargs):
        # 抓取第一个页面的5个数据，需要点进页面再出来
        # self.driver.find_element_by_xpath("//div[@class='layui-laypage-em']")

        self.log("-------------start xhr_to_next_page-------------\n")

        # 找到并点击按钮
        next_page_button = self.driver.find_element_by_xpath(
            "//div[@id='layui-laypage-1']/a[@class='layui-laypage-next']")
        next_page_button.click()
        self.log(f"-------------next_page_button-------------\n{next_page_button}")

        # 等待页面加载完成，可以根据实际情况调整等待时间
        # self.driver.implicitly_wait(5)

        # 获取下一页的URL
        # next_page_url = self.driver.current_url
        # self.log(f"-------------next_page_url------------\n%s" % next_page_url)

        # 等待页面加载完成，可以根据实际情况调整等待时间
        # self.driver.implicitly_wait(5)

        # 获取渲染后的页面内容
        rendered_html = self.driver.page_source
        self.log(f"-------------rendered_html------------\n{rendered_html}")
        # 将渲染后的HTML内容传递给HtmlResponse对象
        rendered_response = HtmlResponse(url=response.url, body=rendered_html, encoding='utf-8')
        self.log(f"-------------rendered_response in xhr_to_next_page------------\n{rendered_response}")

        # 回调给parse函数
        # yield response.follow(url=next_page_url, callback=self.parse, meta={'rendered_response': rendered_response})
        yield rendered_response

        # --------------------------------------------------------------------------------------------------------

        # 发xhr请求https://www.99.com.cn/wenda/asklist?page=2&limit=5
        # 执行JS来触发XHR请求
        # 设置查询参数的值
        # page = 2
        # limit = 5
        # next_page_url = "https://www.99.com.cn/wenda/asklist?page=" + str(page) + "&limit=" + str(limit)

        # yield scrapy.Request(next_page_url, callback=self.parse, dont_filter=True)
        # # 使用字符串格式化将值填入 URL 模板
        # query_url = next_page_url.format(page=page, limit=limit)
        # self.log("-------------query_url-------------\n%s" % query_url)
        #
        # # 打开此js文件
        # with open("./xhr/selenium_99comcn.js", "r", encoding='utf-8') as js_file:
        #     xhr_script = js_file.read()
        #
        # # 发送脚本
        # xhr_script_result = self.driver.execute_script(xhr_script)
        # self.log("-------------xhr_script_result-------------\n%s" % xhr_script_result)

        # TODO 验证是否到了下一页
        # element = WebDriverWait(self.driver, 10).until(
        #     expected_conditions.presence_of_element_located(
        #         (By.XPATH, "//body"))
        # )
        #
        # self.log("-------------element-------------\n%s" % element)

        # TODO 操作下一页，相当于回到parse
        # new_page_content = self.driver.page_source
        # self.log("-------------new_page_content-------------\n%s" % new_page_content)
        # yield scrapy.Request(query_url, callback=self.parse, dont_filter=True)

    # ------------------------------调用下一个页面结束------------------------------

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
        # ------------------------------在子页面爬取数据结束，迭代到parse函数------------------------------

    # ------------------------------加载子页面结束------------------------------
