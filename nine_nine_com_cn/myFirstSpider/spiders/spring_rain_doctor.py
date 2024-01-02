import logging
import random

import scrapy

from selenium import webdriver
from scrapy.utils.project import get_project_settings
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


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


class SpringRainDoctorSpider(scrapy.Spider):
    name = "spring_rain_doctor_crawler"
    allowed_domains = ["www.chunyuyisheng.com"]
    start_urls = ["https://www.chunyuyisheng.com/"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        settings = get_project_settings()
        self.driver = webdriver.Chrome()

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
                (By.XPATH, "//div[@class='ui-grid ui-main clearfix']//li[@class='tab-item ']/a[@href='/pc/doctors/0-0-3/']"))
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
            # TODO 点击进入详情，找到疾病list
            for doctor_card in doctor_cards_list:
                doctor_card.get_attribute()
                