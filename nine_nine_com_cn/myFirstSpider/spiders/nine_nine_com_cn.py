import csv
import logging
import random
import re
import time
import asyncio

import scrapy
from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from nine_nine_com_cn.myFirstSpider.items import NineNineComCnItem

# 全局变量，记录爬取到的url数量
GLOBAL_COUNT_CRAWLED_URL = 0
# log等级定义
# Debug (调试) - 蓝色 logging.debug("\033[34mDebug message\033[0m")
# Info (信息) - 绿色 logging.info("\033[32mInfo message\033[0m")
# Warning (警告) - 黄色 logging.warning("\033[33mWarning message\033[0m")
# Error (错误) - 红色 logging.error("\033[31mError message\033[0m")
# Critical (严重) - 紫红色 logging.critical("\033[35mCritical message\033[0m")


# ------------------------------is_next_button_disabled：没有下一个按钮返回false，有返回true------------------------------
def is_next_button_available(driver):
    logging.info("\033[32m=====Entering is_next_button_available=====\n")
    try:
        WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//div[@id='layui-laypage-1']/a[@class='layui-laypage-next layui-disabled']"))
        )
        return False  # 找到了下一个按钮
    except TimeoutException:
        return True  # 找不到下一个按钮

# mode: r 只读; w （自动新建）覆盖; a （自动新建）追加; b 二进制，如rb wb; x （独占创建）FileExistsError; + 读写，如r+ w+; t 文本，如rt wt
# ------------------------------write_to_file：写入文件模块------------------------------
# raw_data: List, filename: String, file_type: String, write_mode: String
def write_to_file(raw_data, filename, file_type, write_mode):
    logging.info("\033[32m=====Entering write_to_file=====\n\033[0m")
    global GLOBAL_COUNT_CRAWLED_URL
    try:
        with open(filename + '.' + file_type, write_mode, newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[''])
            writer.writeheader()
            for url_unit in raw_data:
                writer.writerow({"": url_unit})
                GLOBAL_COUNT_CRAWLED_URL += 1
            return GLOBAL_COUNT_CRAWLED_URL
    except Exception as e:
        print(f"Error: {e}")
        return GLOBAL_COUNT_CRAWLED_URL


# ------------------------------read_from_file：读取文件模块------------------------------
def read_from_file(target_list_container: list, filename: str, file_type: str, read_mode: str):
    logging.info("\033[32m=====Entering read_from_file=====\n\033[0m")
    try:
        with open(f"{filename}.{file_type}", read_mode, newline='') as csvfile:
            logging.info(f"\033[34m=====Opened {filename}.{file_type} by {read_mode}=====\n\033[0m")
            reader = csv.reader(csvfile)
            url_pattern = re.compile(r'https?://\S+')  # url正则匹配
            for row in reader:  # 读取每行
                if url_pattern.match(row[0]):  # 如果匹配的话
                    target_list_container.append(row[0])  # 装到一个list中
                    logging.debug(f"\033[34m=====Regex one row & appended to {target_list_container}=====\n\033[0m")
            logging.info(f"\033[32m=====Finished loading {filename}.{file_type} to {target_list_container}=====\n\033[0m")
            return target_list_container
    except Exception as e:
        logging.error(
            f"\033[91m=====Error in read_from_file occurred when reading {filename}.{file_type} by {read_mode}: {e}=====\n\033[0m")
        return target_list_container


class NineNineComCnSpider(scrapy.Spider):
    name = "nine_nine_com_cn_crawler"
    allowed_domains = ["99.com.cn/"]
    start_urls = ["https://www.99.com.cn/wenda/"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        settings = get_project_settings()
        self.driver = webdriver.Chrome()
        # ------------------------------自定义变量------------------------------
        self.url_container_file_name = "url_container"
        self.url_container_file_type = "csv"
        self.result_file_name = "result"
        self.result_file_type = "csv"
        self.allocations = []  # 装载所有url爬取到的内容
        self.url_container = []  # 装载所有爬取到的页面url
        self.max_crawl_data = settings.get("MAX_CRAWL_DATA")  # 设置最大爬取数量
        self.sleep_time = settings.get("SLEEP_TIME")  # 设置每次geturl的休息时间
        # self.async_queue = asyncio.Queue()  # 设置处理爬取到url时候的初始化队列进行异步输出结果，而不是一次性
        # self.proxy_pool_urls = self.settings.get('PROXY_POOL_URLS')  # 在初始化中获取代理池的配置信息

        # self.proxy_url = settings.get("PROXY_POOL_URL")
        # chrome_options = Options()
        # chrome_options.add_argument(f'--proxy-server={self.proxy_url}')

        # ------------------------------带参加入------------------------------
        # self.driver = webdriver.Chrome(options=chrome_options)

        logging.debug(f"\033[34m=====max_crawl_data=====\n{self.max_crawl_data}\033[0m")
        logging.debug(f"\033[34m=====GLOBAL_COUNT_CRAWLED_URL init 1=====\n{GLOBAL_COUNT_CRAWLED_URL}\033[0m")

    # ------------------------------开始加载根页面------------------------------
    def parse(self, response, **kwargs):
        self.driver.get(response.url)
        logging.debug(f"\033[34m=====response.url=====\n{response.url}\033[0m")
        # ------------------------------第二部分：爬取下一个分页，疯狂循环---------------------------------
        # 当计数器还没达到最大爬取值时（必须<，不然会多5个） + 检查是否有“下一个”按钮
        while (GLOBAL_COUNT_CRAWLED_URL < self.max_crawl_data) and is_next_button_available(self.driver):
            # 调用xhr_to_next_page处理下一个分页
            logging.debug(f"\033[34m=====GLOBAL_COUNT_CRAWLED_URL parse while 1=====\n{GLOBAL_COUNT_CRAWLED_URL}\033[0m")
            next_page_button = WebDriverWait(self.driver, 10).until(  # 找到并点击按钮
                expected_conditions.presence_of_element_located(
                    (By.XPATH, "//div[@id='layui-laypage-1']/a[@class='layui-laypage-next']"))
            )
            next_page_button.click()
            logging.debug(f"\033[34m=====GLOBAL_COUNT_CRAWLED_URL parse while 2=====\n{GLOBAL_COUNT_CRAWLED_URL}\033[0m")
            # 注意延时（1-5秒随机）
            self.driver.implicitly_wait(random.uniform(1, 3))
            logging.debug(f"\033[34m=====next_page_button=====\n{next_page_button}\033[0m")
            # 获取渲染后的页面内容
            rendered_html = self.driver.page_source
            # rendered_response = HtmlResponse(url=response.url, body=rendered_html, encoding='utf-8')
            # 从渲染后的响应对象中
            # 创建 Selector----------------------------我他妈直接传给你文本看你收不收吧！！！----------------------------
            re_selectors = scrapy.Selector(text=str(rendered_html))
            # 将渲染后的HTML内容传递给HtmlResponse对象
            re_elements = re_selectors.xpath("//div[@class='isue-list']//a[@class='isue-bt']").extract()
            logging.debug(f"\033[34m=====re_elements=====\n{re_elements}\033[0m")
            logging.debug(f"\033[34m=====GLOBAL_COUNT_CRAWLED_URL parse while 3=====\n{GLOBAL_COUNT_CRAWLED_URL}\033[0m")
            # ----------------------------开始解析其中的5个超链接元素----------------------------
            # 接下来会有小于等于5个的链接，我需要遍历他们，当然这个parse只做第一层目录的链接搜索，等到搜集完大部分的url后，再发给parse_subpage来处理响应
            for re_element in re_elements:
                time.sleep(random.uniform(1, 3))  # 注意休息
                re_element_href = scrapy.Selector(text=re_element).xpath("//a/@href").extract_first()  # 获取链接的href属性值
                logging.debug(f"\033[34m=====re_element_href=====\n{re_element_href}\033[0m")
                url = response.urljoin(re_element_href)  # 得到拼接的url，并装载到url_container内
                self.url_container.append(url)
                logging.debug(f"\033[34m=====url_container=====\n{self.url_container}\033[0m")
            # 收集到一个页面urls，写入文件
            logging.debug(f"\033[34m=====GLOBAL_COUNT_CRAWLED_URL parse while 4=====\n{GLOBAL_COUNT_CRAWLED_URL}\033[0m")
            write_to_file(self.url_container, self.url_container_file_name, self.url_container_file_type, "a")
            logging.debug(f"\033[34m=====GLOBAL_COUNT_CRAWLED_URL parse while 5=====\n{GLOBAL_COUNT_CRAWLED_URL}\033[0m")
            # 写完清空
            self.url_container.clear()

        # write_to_file(self.url_container, "result", "csv", "a")
        # 执行完成所有任务，没有剩余页面了
        logging.info("\033[32m=====Crawler System Finished=====\n\033[0m")
        logging.debug(f"\033[34m=====self.url_container=====\n{self.url_container}\033[0m")
        logging.debug(f"\033[34m=====GLOBAL_COUNT_CRAWLED_URL parse 5=====\n{GLOBAL_COUNT_CRAWLED_URL}\033[0m")
        # 调用parse_subpage来处理已写入container的url列表
        try:
            logging.debug(f"\033[34m=====GLOBAL_COUNT_CRAWLED_URL parse 6=====\n{GLOBAL_COUNT_CRAWLED_URL}\033[0m")
            yield from self.parse_subpage(response)

            # await asyncio.gather(
            #     self.parse_subpage(response),
            #     self.async_parse_crawled_url()
            # )

            # self.async_queue.join()  # 关闭异步队列
            logging.info(
                f"\033[32m=====Async Queue System Finished=====\n{GLOBAL_COUNT_CRAWLED_URL}\033[0m")
        except Exception as e:
            logging.error(f"\033[31mParse_subpage Error Occurred: {e}\033[0m")

    # ------------------------------加载与爬取子页面的信息------------------------------
    def parse_subpage(self, response, **kwargs):
        # self.driver.get(response.url)
        logging.info(f"\033[32m=====Entering parse_subpage function, url: {response.url}=====\n\033[0m")
        # 读取文件，然后把所有urls装入handled_result_container
        handled_result_container = read_from_file(self.url_container, self.url_container_file_name,
                                                  self.url_container_file_type, "r")
        logging.debug(f"\033[34m=====handled_result_container=====\n{handled_result_container}\033[0m")
        logging.debug(f"\033[34m=====GLOBAL_COUNT_CRAWLED_URL parse_subpage 1=====\n{GLOBAL_COUNT_CRAWLED_URL}\033[0m")

        for url_unit in handled_result_container:  # 循环处理url_container里的每一个url
            self.driver.get(url_unit)
            time.sleep(random.uniform(self.sleep_time[0], self.sleep_time[1]))  # 注意休息
            first_link_meta_element = WebDriverWait(self.driver, random.uniform(8, 12)).until(
                expected_conditions.presence_of_element_located((By.XPATH, "//div[@class='dtl-left']"))
            )
            # ------------------------------在子页面爬取数据------------------------------
            # 新建NineNineComCnItem类型的bean
            issue = NineNineComCnItem()

            issue_title = first_link_meta_element.find_element_by_xpath(
                "./div[@class='dtl-wrap']/div[@class='dtl-top']/h1").text
            issue_desc = first_link_meta_element.find_element_by_xpath(
                "./div[@class='dtl-wrap']//div[@class='atcle-ms']/p").text
            answer_analyze = first_link_meta_element.find_element_by_xpath("//div[@class='dtl-reply']/p").text
            answer_opinion = first_link_meta_element.find_element_by_xpath("//div[@class='dtl-reply']/p[2]").text
            case_url = url_unit

            issue['issue_title'] = issue_title
            issue['issue_desc'] = issue_desc
            issue['answer_analyze'] = answer_analyze
            issue['answer_opinion'] = answer_opinion
            issue['case_url'] = case_url

            logging.info(f"\033[32m=====issue=====\n{issue}\033[0m")
            # 添加异步增量写入，防止宕机数据一起丢失
            # asyncio.ensure_future(self.async_queue.put(issue))
            yield issue

    # ------------------------------异步执行url输出最终结果------------------------------
    # TODO 异步调用需要解决
    # async def async_parse_crawled_url(self):
    #     logging.info("\033[32m=====Entering async_parse_crawled_url=====\n\033[0m")
    #     while True:
    #         issue = await self.async_queue.get()
    #         # 写入到文件
    #         with open('result.csv', 'a', encoding='utf-8') as csvfile:
    #             writer = csv.DictWriter(csvfile, fieldnames=[''])
    #             writer.writeheader()
    #             for url_unit in raw_data:
    #                 writer.writerow({"": url_unit})
    #             csvfile.write(str(issue) + '\n')
    #         self.async_queue.task_done()
