import csv
import logging
import random
import time

import scrapy
from scrapy.http import HtmlResponse

from selenium import webdriver
from scrapy.utils.project import get_project_settings
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from nine_nine_com_cn.myFirstSpider.items import SpringRainDoctorItem

# 全局变量，记录爬取到的url数量
GLOBAL_COUNT_CRAWLED_URL = 0


def is_next_button_available(driver):
    logging.info("\033[32m=====Entering is_next_button_available=====\n")
    try:
        WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//div[@class='pagebar']/a[@class='next disabled']"))
        )
        return False  # 下一个按钮为禁用
    except TimeoutException:
        return True  # 找到了下一个按钮


def is_doctor_card_available(driver):
    logging.info("\033[32m=====Entering is_doctor_card_available=====\n")


# 切换tab
def switch_to_tab_window(driver, open_tab):
    all_handles = driver.window_handles  # 获取所有窗口句柄
    driver.switch_to.window(all_handles[open_tab])  # 跳转到第二个窗口，即医生信息窗口
    logging.info(f"\033[32m=====Current Url: {driver.current_url}=====\n\033[0m")


# 关闭tab
def close_some_tab_window(driver, close_tab):
    all_handles = driver.window_handles  # 获取所有窗口句柄
    driver.switch_to.window(all_handles[close_tab])
    driver.close()  # TODO SOME PROBLEM
    logging.info(f"\033[32m=====Current Url: {driver.current_url}=====\n\033[0m")


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


class SpringRainDoctorSpider(scrapy.Spider):
    name = "spring_rain_doctor_crawler"
    allowed_domains = ["www.chunyuyisheng.com"]
    start_urls = ["https://www.chunyuyisheng.com/"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        settings = get_project_settings()
        self.allocations = []  # 装载所有url爬取到的内容
        self.url_container = []
        self.url_container_file_name = "url_container"
        self.url_container_file_type = "csv"
        self.result_file_name = "result"
        self.result_file_type = "csv"
        self.max_crawl_data = settings.get("MAX_CRAWL_DATA")  # 设置最大爬取数量

        # ------------------------------代理区------------------------------
        # self.driver = webdriver.Chrome()
        self.proxy_url = settings.get("PROXY_POOL_URL")
        chrome_options = Options()
        chrome_options.add_argument(f'--proxy-server={self.proxy_url}')
        self.driver = webdriver.Chrome(options=chrome_options)

        # -----------------------------------------------------------------
        # self.cookies = self.driver.get_cookies()

        self.click_time = random.uniform(settings.get("CLICK_TIME")[0], settings.get("CLICK_TIME")[1])  # 设置每次点击按钮的休息时间
        logging.debug(f"\033[34m=====Start Url Count: {GLOBAL_COUNT_CRAWLED_URL}\033[0m")

    def parse(self, response, **kwargs):
        global GLOBAL_COUNT_CRAWLED_URL
        self.driver.get(response.url)
        logging.debug(f"\033[34m=====response.url=====\n{response.url}\033[0m")

        find_doctor_button = WebDriverWait(self.driver, 5).until(  # 找到“找医生”按钮
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//li[@class='find-doc nav-item']/a[@id='click_btn']"))
        )
        actions = ActionChains(self.driver)  # 创建鼠标悬停动作链
        actions.move_to_element(find_doctor_button)  # 创建move动作
        actions.perform()  # 执行鼠标悬停动作
        # 进入“按科室寻找医生”界面
        find_dep_doctor_button = WebDriverWait(self.driver, 5).until(  # 找到“按科室找医生”按钮
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//li[@class='nav-item nav-recommend no-back-g']/a"))
        )
        logging.debug("\033[34m=====Click 找医生 Button=====\n\033[0m")
        find_dep_doctor_button.click()  # 点击按钮
        logging.info("\033[32m=====找医生 Button Clicked=====\n\033[0m")
        # 进入医生列表界面，操作一级科室
        find_in_med_button = WebDriverWait(self.driver, 5).until(  # 找到“内科”按钮
            expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "//div[@class='ui-grid ui-main clearfix']//li[@class='tab-item ']/a[@href='/pc/doctors/0-0-3/']"))
        )
        logging.debug("\033[34m=====Click 内科 Button=====\n\033[0m")
        find_in_med_button.click()  # 点击按钮
        logging.info("\033[32m=====内科 Button Clicked=====\n\033[0m")
        # 操作二级科室
        find_heart_in_med_button = WebDriverWait(self.driver, 5).until(  # 找到“心血管内科”按钮
            expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "//div[@class='sider-wrap dropdown-wrap']//li[@class='tab-item ']/a[@href='/pc/doctors/0-0-ab/']"))
        )
        logging.debug("\033[34m=====Click 心血管内科 Button=====\n\033[0m")
        find_heart_in_med_button.click()  # 点击按钮
        logging.info("\033[32m=====心血管内科 Button Clicked=====\n\033[0m")
        # 操作“仅显示可咨询医生”按钮
        doctor_available_button = WebDriverWait(self.driver, 5).until(  # 找到“仅显示可咨询医生”按钮
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//div[@id='clinicTitle']/a/label[@class='available-switch']"))
        )
        logging.debug("\033[34m=====Click 仅显示可咨询医生 Button=====\n\033[0m")
        doctor_available_button.click()  # 点击按钮
        logging.info("\033[32m=====仅显示可咨询医生 Button Clicked=====\n\033[0m")

        # -------------------至此，按年进入需要爬取的页面完成，接下来是对医生名片的操作（第二级）-------------------

        while is_next_button_available(self.driver) and GLOBAL_COUNT_CRAWLED_URL < self.max_crawl_data:  # 判断是否还有下一页
            next_page_btn = WebDriverWait(self.driver, 5).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, "//div[@class='pagebar']/a[@class='next']"))
            )
            next_page_btn.click()

            doctor_cards_list = WebDriverWait(self.driver, 5).until(  # 判定当前页面是否存在医生卡片
                expected_conditions.presence_of_all_elements_located(
                    (By.XPATH, "//div[@class='doctor-list']/div[contains(@class, 'doctor-info-item')]"))
            )
            # 点击进入详情，找到疾病list
            for doctor_card in doctor_cards_list:
                time.sleep(self.click_time)  # 这个地方click的太快了，导致服务器429，需要加个睡眠时间！
                logging.debug(f"\033[34m=====Doctor Cards List: {doctor_cards_list}\n\033[0m")
                doctor_detail_link = doctor_card.find_element_by_xpath(
                    "./div[@class='detail']/div[@class='des-item']/a[@class='name-wrap']")
                logging.debug(f"\033[34m=====Current Doctor Card: {doctor_detail_link}\n\033[0m")
                # doctor_detail_link.click()  # 点击进入当前循环的医生卡片 FIXME tab重复
                self.driver.implicitly_wait(2)
                # url = self.driver.current_url
                incoming_url = response.urljoin(doctor_detail_link.get_attribute("href"))
                logging.info(f"\033[32m=====Jump Into Doctor:{incoming_url}\n\033[0m")
                logging.info("\033[32m=====Do Parsing parse_doctor_page Function=====\n\033[0m")

                # self.url_container.append(incoming_url)
                # GLOBAL_COUNT_CRAWLED_URL += 1

                yield scrapy.Request(incoming_url, callback=self.parse_doctor_page,
                                     meta={'incoming_url': incoming_url}, dont_filter=True)
                # FIXME 先截断吧，收集各个医生的url，放入文件中，给下面的函数独立处理
        # write_to_file(self.url_container, self.url_container_file_name, self.url_container_file_type, "a")
        # logging.info(f"\033[32m=====URL CONTAINER: {self.url_container}\n\033[0m")

    # 2. 独立处理doctor页面。当前：特定医生页面
    def parse_doctor_page(self, response, **kwargs):
        doctor_url = response.meta.get('incoming_url')
        logging.info(f"\033[32m=====Jump Into parse_doctor_page Function: {doctor_url}\n\033[0m")
        self.driver.get(doctor_url)

        # FIXME selenium和scrapy的API要制定使用+规范，否则会出现奇奇怪怪的bug
        # switch_to_tab_window(self.driver, 0)  # 切换页面到主页面
        logging.info("\033[32m=====Do Parsing parse_issue_page Function=====\n\033[0m")

        current_url = self.driver.current_url
        logging.info(f"\033[32m=====parse_doctor_page Current URL: {current_url}\n\033[0m")
        issue_list = self.driver.find_elements_by_xpath("//div[@class='hot-qa-item']//a")  # FIXME 问题部分：找不到元素

        for issue in issue_list:
            time.sleep(self.click_time)  # 睡一觉
            # issue.click()  # 点击进入当前特定医生的特定issue
            incoming_url = response.urljoin(issue.get_attribute("href"))
            logging.info(f"\033[32m=====Jump Into Issue of Doctor: {incoming_url}\n\033[0m")
            # 处理问诊记录（有可能没有！！！）
            yield scrapy.Request(url=incoming_url, callback=self.parse_issue_archive,
                                 meta={'incoming_url': incoming_url}, dont_filter=True)

    # 3. 处理issue页面。当前：特定医生页面下面的issue list

    # 4. 处理issue的问诊记录页面。当前：issue list下面的特定issue
    def parse_issue_archive(self, response, **kwargs):
        logging.info("\033[32m=====Jump Into parse_doctor_page Function=====\n\033[0m")
        doctor_issue_url = response.meta.get('incoming_url')  # 别删，监听器有问题
        self.driver.get(doctor_issue_url)
        logging.info(f"\033[32m=====parse_issue_archive Current URL: {doctor_issue_url}\n\033[0m")
        logging.info("\033[32m=====Jump Into parse_issue_archive Function\n\033[0m")
        current_issue_url = self.driver.current_url
        logging.info(f"\033[32m=====parse_issue_archive Current Issue URL: {current_issue_url}\n\033[0m")
        issue_unit = SpringRainDoctorItem()
        # 捕捉到issue归纳的按钮
        # issue_archive_button = self.driver.find_element_by_xpath(
        #     "//div[@class='qa-arrangement-header']/span[@class='qa-arrangement-btn']")
        # issue_archive_button.click()  # 点击issue归纳的按钮
        # 处理春雨医生整理的文字
        logging.info("\033[32m=====Parsing archive text=====\n\033[0m")
        try:
            issue_archive_button = self.driver.find_element_by_xpath(
                "//div[@class='qa-arrangement-header']/span[@class='qa-arrangement-btn']")
            issue_archive_button.click()  # 点击issue归纳的按钮

            issue_archive = WebDriverWait(self.driver, 5).until(  # 捕捉到春雨医生整理的文字
                expected_conditions.presence_of_element_located(
                    (By.XPATH, "//div[@class='qa-arrangement-body']"))
            )

            issue_unit['issue_title'] = self.driver.title
            issue_unit['issue_desc'] = issue_archive.find_element_by_xpath("//p[@class='qa-des'][1]/text()")
            issue_unit['answer'] = issue_archive.find_element_by_xpath("//p[@class='qa-des'][2]/text()")
            issue_unit['case_url'] = self.driver.current_url

            logging.info(f"\033[32m=====issue_unit: {issue_unit}\n\033[0m")

        except Exception as e:
            print(f"ERROR: {e}")
            issue_unit['issue_title'] = self.driver.title
            issue_unit['issue_desc'] = ""
            issue_unit['answer'] = ""
            issue_unit['case_url'] = self.driver.current_url

            logging.info(f"\033[32m=====issue_unit: {issue_unit}\n\033[0m")
