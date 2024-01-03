import logging
import random
import time

import scrapy

from selenium import webdriver
from scrapy.utils.project import get_project_settings
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
        self.driver = webdriver.Chrome()

        self.click_time = random.uniform(settings.get("CLICK_TIME")[0], settings.get("CLICK_TIME")[1])  # 设置每次点击按钮的休息时间

    def parse(self, response, **kwargs):
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
                count += 1
                if count > 4:
                    break
                time.sleep(self.click_time)  # 这个地方click的太快了，导致服务器429，需要加个睡眠时间！
                logging.debug(f"\033[34m=====Doctor Cards List: {doctor_cards_list}=====\n\033[0m")
                doctor_detail_link = doctor_card.find_element_by_xpath(
                    "./div[@class='detail']/div[@class='des-item']/a[@class='name-wrap']")
                logging.debug(f"\033[34m=====Current Doctor Card: {doctor_detail_link}=====\n\033[0m")
                doctor_detail_link.click()  # 点击进入当前循环的医生卡片
                logging.info("\033[32m=====Jump Into Doctor=====\n\033[0m")
                # url = response.urljoin(doctor_detail_link.get_attribute("href"))
                # 目前已打开了特定医生的页面，现在我们需要切换到这个医生的页面进行爬取，yield到parse_doctor_page函数
                # yield scrapy.Request(url, callback=self.parse_doctor_page, meta={'driver': self.driver}, dont_filter=True)
                # 这里不要用url进行访问，需要使用窗口句柄进行访问
                # switch_to_tab_window(self.driver, 1)  # 切换页面到医生页面
                logging.info("\033[32m=====Do Parsing parse_doctor_page Function=====\n\033[0m")
                yield from self.parse_doctor_page(response)  # ↓↓↓↓↓↓↓开始迭代↓↓↓↓↓↓↓

    # 2. 处理doctor页面。当前：医生list页面
    def parse_doctor_page(self, response, **kwargs):
        logging.info("\033[32m=====Jump Into parse_doctor_page Function=====\n\033[0m")
        # switch_to_tab_window(self.driver, 0)  # 切换页面到主页面
        logging.info("\033[32m=====Do Parsing parse_issue_page Function=====\n\033[0m")

        # 滚动到页面底部
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.END)
        actions.perform()

        logging.debug("\033[34m=====Do Keys to the END of page=====\n\033[0m")

        yield from self.parse_issue_page(response)  # ↓↓↓↓↓↓↓开始迭代↓↓↓↓↓↓↓

    # 3. 处理issue页面。当前：特定医生页面下面的issue list
    def parse_issue_page(self, response, **kwargs):
        logging.info("\033[32m=====Jump Into parse_issue_page Function=====\n\033[0m")
        issue_list = WebDriverWait(self.driver, 10).until(  # 捕捉到issue list
            expected_conditions.presence_of_all_elements_located((By.XPATH, "//div[@class='hot-qa main-block']/div[@class='hot-qa-item']//a"))
        )
        for issue in issue_list:
            time.sleep(self.click_time)  # 睡一觉
            issue.click()  # 点击进入当前特定医生的特定issue
            logging.info("\033[32m=====Jump Into Issue of Doctor=====\n\033[0m")
            # switch_to_tab_window(self.driver, 2)  # 切换页面到issue页面
            # 处理问诊记录（有可能没有！！！）
            yield from self.parse_issue_archive(response)

    # 4. 处理issue的问诊记录页面。当前：issue list下面的特定issue
    def parse_issue_archive(self, response, **kwargs):
        logging.info("\033[32m=====Jump Into parse_issue_archive Function=====\n\033[0m")
        issue_unit = SpringRainDoctorItem()
        issue_archive_button = WebDriverWait(self.driver, 5).until(  # 捕捉到issue归纳的按钮
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//div[@class='qa-arrangement-header']/span[@class='qa-arrangement-btn']"))
        )
        issue_archive_button.click()  # 点击issue归纳的按钮
        # 处理春雨医生整理的文字
        logging.info("\033[32m=====Parsing archive text=====\n\033[0m")
        issue_archive = WebDriverWait(self.driver, 5).until(  # 捕捉到春雨医生整理的文字
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//div[@class='qa-arrangement-body']"))
        )

        issue_unit['issue_title'] = self.driver.title
        issue_unit['issue_desc'] = issue_archive.find_element_by_xpath("//p[@class='qa-des'][1]/text()")
        issue_unit['answer'] = issue_archive.find_element_by_xpath("//p[@class='qa-des'][2]/text()")
        issue_unit['case_url'] = self.driver.current_url

        self.driver.close()  # 关闭issue页面
