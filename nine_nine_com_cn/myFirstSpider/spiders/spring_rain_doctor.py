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
    driver.close()
    logging.info(f"\033[32m=====Current Url: {driver.current_url}=====\n\033[0m")


class SpringRainDoctorSpider(scrapy.Spider):
    name = "spring_rain_doctor_crawler"
    allowed_domains = ["www.chunyuyisheng.com"]
    start_urls = ["https://www.chunyuyisheng.com/"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        settings = get_project_settings()

        # ------------------------------代理区------------------------------
        self.driver = webdriver.Chrome()
        # self.proxy_url = settings.get("PROXY_POOL_URL")
        # chrome_options = Options()
        # chrome_options.add_argument(f'--proxy-server={self.proxy_url}')
        # self.driver = webdriver.Chrome(options=chrome_options)

        # -----------------------------------------------------------------
        self.cookies = self.driver.get_cookies()

        self.click_time = random.uniform(settings.get("CLICK_TIME")[0], settings.get("CLICK_TIME")[1])  # 设置每次点击按钮的休息时间

    # def start_requests(self):
    #   # 发送请求，设置代理 IP 为空
    # yield scrapy.Request(url='http://ip.chinaz.com/getip.aspx', dont_filter=True)

    def parse(self, response, **kwargs):

        # --------------解析响应，提取IP信息--------------
        # print(response.meta.get('proxy'))

        # ------------------------------------------

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

        while is_next_button_available(self.driver):  # 判断是否还有下一页
            doctor_cards_list = WebDriverWait(self.driver, 5).until(  # 判定当前页面是否存在医生卡片
                expected_conditions.presence_of_all_elements_located(
                    (By.XPATH, "//div[@class='doctor-list']/div[contains(@class, 'doctor-info-item')]"))
            )
            count = 0
            # TODO 点击进入详情，找到疾病list
            for doctor_card in doctor_cards_list:
                # count += 1
                # if count > 4:
                #     break
                time.sleep(self.click_time)  # 这个地方click的太快了，导致服务器429，需要加个睡眠时间！
                logging.debug(f"\033[34m=====Doctor Cards List: {doctor_cards_list}=====\n\033[0m")
                doctor_detail_link = doctor_card.find_element_by_xpath(
                    "./div[@class='detail']/div[@class='des-item']/a[@class='name-wrap']")
                logging.debug(f"\033[34m=====Current Doctor Card: {doctor_detail_link}=====\n\033[0m")
                doctor_detail_link.click()  # 点击进入当前循环的医生卡片
                self.driver.implicitly_wait(2)
                # url = self.driver.current_url
                url = response.urljoin(doctor_detail_link.get_attribute("href"))
                logging.info(f"\033[32m=====Jump Into Doctor:{url}=====\n\033[0m")
                # url = response.urljoin(doctor_detail_link.get_attribute("href"))
                # 目前已打开了特定医生的页面，现在我们需要切换到这个医生的页面进行爬取，yield到parse_doctor_page函数
                # yield scrapy.Request(url, callback=self.parse_doctor_page, meta={'driver': self.driver}, dont_filter=True)
                # 这里不要用url进行访问，需要使用窗口句柄进行访问
                # switch_to_tab_window(self.driver, 1)  # 切换页面到医生页面
                logging.info("\033[32m=====Do Parsing parse_doctor_page Function=====\n\033[0m")
                # self.cookies = self.driver.get_cookies()
                yield from self.parse_doctor_page(response, url)  # ↓↓↓↓↓↓↓开始迭代↓↓↓↓↓↓↓
                # scrapy_response = HtmlResponse(url=url, body=self.driver.page_source, encoding='utf-8')
                # yield scrapy.Request(url=url, callback=self.parse_doctor_page, dont_filter=True)

    # 2. 处理doctor页面。当前：特定医生页面
    def parse_doctor_page(self, response, doctor_url, **kwargs):
        logging.info("\033[32m=====Jump Into parse_doctor_page Function=====\n\033[0m")
        doctor_url = self.driver.get(doctor_url)  # 别删，监听器有问题
        logging.info(f"\033[32m=====parse_doctor_page doctor_url: {doctor_url}=====\n\033[0m")
        # switch_to_tab_window(self.driver, 0)  # 切换页面到主页面
        logging.info("\033[32m=====Do Parsing parse_issue_page Function=====\n\033[0m")

        current_url = self.driver.current_url
        logging.info(f"\033[32m=====parse_doctor_page Current URL: {current_url}=====\n\033[0m")
        issue_list = self.driver.find_elements_by_xpath("//div[@class='hot-qa-item']//a")

        for issue in issue_list:
            time.sleep(self.click_time)  # 睡一觉
            issue.click()  # 点击进入当前特定医生的特定issue
            self.driver.implicitly_wait(2)
            url = response.urljoin(issue.get_attribute("href"))
            logging.info(f"\033[32m=====Jump Into Issue of Doctor: {url}=====\n\033[0m")
            # switch_to_tab_window(self.driver, 2)  # 切换页面到issue页面
            # 处理问诊记录（有可能没有！！！）
            yield from self.parse_issue_archive(response, url)

    # 3. 处理issue页面。当前：特定医生页面下面的issue list

    # 4. 处理issue的问诊记录页面。当前：issue list下面的特定issue
    def parse_issue_archive(self, response, url, **kwargs):
        logging.info("\033[32m=====Jump Into parse_doctor_page Function=====\n\033[0m")
        doctor_issue_url = self.driver.get(url)  # 别删，监听器有问题
        logging.info(f"\033[32m=====parse_doctor_page Current URL: {doctor_issue_url}=====\n\033[0m")
        logging.info("\033[32m=====Jump Into parse_issue_archive Function=====\n\033[0m")
        current_issue_url = self.driver.current_url
        logging.info(f"\033[32m=====parse_issue_archive Current Issue URL: {current_issue_url}=====\n\033[0m")
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

            logging.info(f"\033[32m=====issue_unit: {issue_unit}=====\n\033[0m")

        except Exception as e:
            print(f"ERROR: {e}")
            issue_unit['issue_title'] = self.driver.title
            issue_unit['issue_desc'] = ""
            issue_unit['answer'] = ""
            issue_unit['case_url'] = self.driver.current_url

            logging.info(f"\033[32m=====issue_unit: {issue_unit}=====\n\033[0m")

        self.driver.close()  # TODO 关闭issue页面，现在关闭的是主页，应该关闭第三页
