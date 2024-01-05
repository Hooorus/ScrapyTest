import ast
import csv
import logging
import random
import re
import shutil
import time

import scrapy
from scrapy.exceptions import IgnoreRequest

from selenium import webdriver
from scrapy.utils.project import get_project_settings
from selenium.common.exceptions import TimeoutException, NoSuchElementException, JavascriptException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from nine_nine_com_cn.myFirstSpider.items import SpringRainDoctorItem
from nine_nine_com_cn.myFirstSpider.pipelines import MysqlPipeline

# 全局变量，记录爬取到的url数量(step. 1)
GLOBAL_DOCTOR_CRAWLED_URL = 0
# 全局变量，记录issue url的爬取数量(step. 2)
GLOBAL_ISSUE_CRAWLED_URL = 0
# 全局变量，记录issue url的处理数量(step. 3)
GLOBAL_ISSUE_PARSED_URL = 0
# 全局变量，记录分页点击数量
GLOBAL_PAGINATION_BTN_COUNT = 0


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


def write_to_file(raw_data, filename, file_type, write_mode):
    logging.info("\033[32m=====Entering write_to_file=====\n\033[0m")
    global GLOBAL_DOCTOR_CRAWLED_URL
    try:
        with open(filename + '.' + file_type, write_mode, newline='', encoding='utf-8') as csvfile:
            fieldnames = ['URL', 'AlREADY_PARSED']
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writeheader()
            for url_unit in raw_data:
                writer.writerow({"URL": url_unit, "AlREADY_PARSED": "0"})
                GLOBAL_DOCTOR_CRAWLED_URL += 1
            return GLOBAL_DOCTOR_CRAWLED_URL
    except Exception as e:
        print(f"Error: {e}")
        return GLOBAL_DOCTOR_CRAWLED_URL


# ------------------------------read_from_file：读取文件模块------------------------------
def read_from_file(target_list_container: list, filename: str, file_type: str, enable_regex: int):
    logging.info("\033[32m=====Entering read_from_file=====\n\033[0m")
    try:
        with open(f"{filename}.{file_type}", "r+", newline='', encoding='utf-8') as csvfile:
            logging.info(f"\033[34m=====Opened {filename}.{file_type}=====\n\033[0m")
            reader = csv.DictReader(csvfile)
            rows_to_write = []  # 用于存储将要写回文件的行

            if enable_regex == 1:
                url_pattern = re.compile(r'https?://\S+')  # url正则匹配
            elif enable_regex == 0:
                url_pattern = re.compile(r'^(?!URL).*')
            for row in reader:  # 读取每行
                logging.debug(f"\033[34m====={row}=====\n\033[0m")
                if url_pattern.match(row['URL']) and row['AlREADY_PARSED'] == "0":  # 如果匹配的话
                    row['AlREADY_PARSED'] = "1"
                    target_list_container.append(row['URL'])  # 装到一个list中
                    logging.debug(f"\033[34m=====Regex one row & appended to {target_list_container}=====\n\033[0m")
                # 将修改后的行添加到列表中
                rows_to_write.append(row)
            # 将修改后的行写回文件
            with open(f"{filename}.{file_type}", 'w', newline='', encoding='utf-8') as csvfile_write:
                writer = csv.DictWriter(csvfile_write, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows(rows_to_write)

            logging.info(
                f"\033[32m=====Finished loading {filename}.{file_type} to {target_list_container}=====\n\033[0m")
            return target_list_container
    except Exception as e:
        logging.error(
            f"\033[91m=====Error in read_from_file occurred when reading {filename}.{file_type}: {e}=====\n\033[0m")
        return target_list_container


# ------------------------------csv数据清洗模块------------------------------
def data_clean_from_file(filename: str, file_type: str):
    logging.info("\033[32m=====Entering data_clean_from_file=====\n\033[0m")
    try:
        # Create a temporary file
        temp_filename = f"_{filename}.{file_type}"
        with open(f"{filename}.{file_type}", "r", newline='', encoding='utf-8') as csvfile, \
                open(temp_filename, "w", newline='', encoding='utf-8') as temp_csvfile:
            reader = csv.reader(csvfile)
            writer = csv.writer(temp_csvfile)
            trash_pattern = re.compile(r'^\s*{}?\s*$')
            for row in reader:
                if not trash_pattern.match(row[0]):
                    writer.writerow(row)
        shutil.move(temp_filename, f"{filename}.{file_type}")
        logging.info(f"\033[32m=====Data cleaned in {filename}.{file_type}=====\n\033[0m")

    except Exception as e:
        logging.warning(f"\033[33m=====Error during data cleaning: {e}\n\033[0m")


class SpringRainDoctorSpider(scrapy.Spider):
    name = "spring_rain_doctor_crawler"
    allowed_domains = ["www.chunyuyisheng.com"]
    start_urls = ["https://www.chunyuyisheng.com/"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        settings = get_project_settings()
        self.allocations = []  # 装载所有url爬取到的内容

        self.doctor_url_container = []
        self.doctor_url_container_file_name = "doctor_url_container"
        self.doctor_url_container_file_type = "csv"

        self.issue_url_container = []
        self.issue_url_container_file_name = "issue_url_container"
        self.issue_url_container_file_type = "csv"

        self.result_file_name = "result"
        self.result_file_type = "csv"

        self.pipline_list_container = []

        self.max_crawl_doctors = settings.get("MAX_CRAWL_DOCTOR")  # 设置最大爬取数量

        # ------------------------------PROXY AREA------------------------------
        self.driver = webdriver.Chrome()
        # self.proxy_url = settings.get("PROXY_POOL_URL")
        # chrome_options = Options()
        # chrome_options.add_argument(f'--proxy-server={self.proxy_url}')
        # self.driver = webdriver.Chrome(options=chrome_options)
        # -----------------------------------------------------------------

        # ------------------------------DATABASE AREA------------------------------
        self.mysql_pipeline = MysqlPipeline
        # -----------------------------------------------------------------

        self.click_time = random.uniform(settings.get("CLICK_TIME")[0], settings.get("CLICK_TIME")[1])  # 设置每次点击按钮的休息时间
        self.sleep_time = random.uniform(settings.get("SLEEP_TIME")[0], settings.get("SLEEP_TIME")[1])  # 设置每次睡觉休息时间
        logging.debug(f"\033[34m=====Start Url Count: {GLOBAL_DOCTOR_CRAWLED_URL}\033[0m")

    def parse(self, response, **kwargs):
        global GLOBAL_DOCTOR_CRAWLED_URL
        global GLOBAL_PAGINATION_BTN_COUNT

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

        # -------------------至此，按年进入需要爬取的页面完成，接下来是对医生名片的操作（第二级）-------------------

        while (is_next_button_available(self.driver)
               and GLOBAL_DOCTOR_CRAWLED_URL < self.max_crawl_doctors
               and GLOBAL_PAGINATION_BTN_COUNT < 9):  # 判断是否还有下一页
            next_page_btn = WebDriverWait(self.driver, 5).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, "//div[@class='pagebar']/a[@class='next']"))
            )
            next_page_btn.click()
            GLOBAL_PAGINATION_BTN_COUNT += 1  # 分页点击次数+1
            doctor_cards_list = WebDriverWait(self.driver, 5).until(  # 判定当前页面是否存在医生卡片
                expected_conditions.presence_of_all_elements_located(
                    (By.XPATH, "//div[@class='doctor-list']/div[contains(@class, 'doctor-info-item')]"))
            )
            # 点击进入详情，找到疾病list
            for doctor_card in doctor_cards_list:
                # ----------------------------------
                if GLOBAL_DOCTOR_CRAWLED_URL >= self.max_crawl_doctors:
                    logging.info(f"\033[32m=====doctor number:{GLOBAL_DOCTOR_CRAWLED_URL}, exit loop\n\033[0m")
                    break
                # ----------------------------------
                time.sleep(self.sleep_time)  # 这个地方click的太快了，导致服务器429，需要加个睡眠时间！
                logging.debug(f"\033[34m=====Doctor Cards List: {doctor_cards_list}\n\033[0m")
                doctor_detail_link = doctor_card.find_element_by_xpath(
                    "./div[@class='detail']/div[@class='des-item']/a[@class='name-wrap']")
                logging.debug(f"\033[34m=====Current Doctor Card: {doctor_detail_link}\n\033[0m")
                self.driver.implicitly_wait(2)
                incoming_url = response.urljoin(doctor_detail_link.get_attribute("href"))
                logging.info(f"\033[32m=====Jump Into Doctor:{incoming_url}\n\033[0m")
                self.doctor_url_container.append(incoming_url)
                GLOBAL_DOCTOR_CRAWLED_URL += 1
                logging.info(f"\033[32m=====GLOBAL_DOCTOR_CRAWLED_URL : {GLOBAL_DOCTOR_CRAWLED_URL}\n\033[0m")
                # 先截断吧，收集各个医生的url，放入文件中，给下面的函数独立处理
        write_to_file(self.doctor_url_container, self.doctor_url_container_file_name,
                      self.doctor_url_container_file_type, "a")
        self.doctor_url_container.clear()  # 写完清空
        logging.info(f"\033[32m=====DOCTOR URL CONTAINER: {self.doctor_url_container}\n\033[0m")
        # 着手处理url_container.csv
        try:
            yield from self.parse_doctor_page(response)
            logging.info(f"\033[32m=====parse_doctor_page Finished=====\n{GLOBAL_DOCTOR_CRAWLED_URL}\033[0m")
        except Exception as e:
            logging.error(f"\033[31mParse_doctor_page Error Occurred: {e}\033[0m")

    # 2. 独立处理doctor页面。当前：特定医生页面，需要将医生下的所有link整合到一个csv里面
    def parse_doctor_page(self, response, **kwargs):
        global GLOBAL_ISSUE_CRAWLED_URL
        # 读取文件，然后把所有urls装入handled_result_container
        handled_result_container = read_from_file(self.doctor_url_container, self.doctor_url_container_file_name,
                                                  self.doctor_url_container_file_type, 1)
        for url_unit in handled_result_container:  # 循环处理url_container里的每一个url
            self.driver.get(url_unit)  # 得到每个好评问题的url进行访问
            time.sleep(self.sleep_time)  # 注意休息
            # 这个地方会出现医生页面没有issue（异常：空），或者春雨医生拒绝访问（异常：404），
            try:
                qa_links = WebDriverWait(self.driver, 10).until(
                    expected_conditions.presence_of_all_elements_located((By.XPATH, "//div[@class='hot-qa-item']//a"))
                )
                for qa_link in qa_links:
                    qa_link_url = response.urljoin(qa_link.get_attribute("href"))
                    self.issue_url_container.append(qa_link_url)
                    GLOBAL_ISSUE_CRAWLED_URL += 1
                    logging.info(f"\033[32m=====GLOBAL_ISSUE_CRAWLED_URL : {GLOBAL_ISSUE_CRAWLED_URL}\n\033[0m")
                write_to_file(self.issue_url_container, self.issue_url_container_file_name,
                              self.issue_url_container_file_type, "a")
                self.issue_url_container.clear()  # 写完清空
            except TimeoutException as te:  # 春雨医生拒绝访问404
                write_to_file(self.issue_url_container, self.issue_url_container_file_name,
                              self.issue_url_container_file_type, "a")
                self.issue_url_container.clear()  # 写完清空
                logging.warning(f"\033[33m=====TimeoutException: 页面加载超时: \n{te}\n\033[0m")
                break
            except NoSuchElementException as ne:  # 医生页面没有issue
                logging.warning(f"\033[33m=====NoSuchElementException: 找不到issue元素: \n{ne}\n\033[0m")
            except KeyboardInterrupt as ki:  # 用户中断操作
                write_to_file(self.issue_url_container, self.issue_url_container_file_name,
                              self.issue_url_container_file_type, "a")
                self.issue_url_container.clear()  # 写完清空
                logging.warning(f"\033[33m=====KeyboardInterrupt: 用户中断操作: \n{ki}\n\033[0m")
                break
            except SystemExit as se:  # 程序自动退出，需要将当前容器内容导入文件
                write_to_file(self.issue_url_container, self.issue_url_container_file_name,
                              self.issue_url_container_file_type, "a")
                self.issue_url_container.clear()  # 写完清空
                logging.warning(f"\033[33m=====SystemExit: 程序自动退出: \n{se}\n\033[0m")
                break
            except Exception as e:  # 其他异常
                write_to_file(self.issue_url_container, self.issue_url_container_file_name,
                              self.issue_url_container_file_type, "a")
                self.issue_url_container.clear()  # 写完清空
                logging.warning(f"\033[33m=====Other Exception: 其他异常: \n{e}\n\033[0m")
        logging.info(f"\033[32m=====ISSUE URL CONTAINER: {self.issue_url_container}\n\033[0m")
        # 下一步，处理第三级issue
        try:
            yield from self.parse_issue_archive(response)
            logging.info(f"\033[32m=====parse_issue_archive Finished=====\n{GLOBAL_DOCTOR_CRAWLED_URL}\033[0m")
        except Exception as e:
            logging.error(f"\033[31mParse_issue_archive Error Occurred: {e}\033[0m")

    # 3. 处理issue的问诊记录页面。当前：issue list下面的特定issue
    def parse_issue_archive(self, response, **kwargs):
        global GLOBAL_ISSUE_PARSED_URL
        logging.info("\033[32m=====Jump Into parse_doctor_page Function=====\n\033[0m")
        handled_issue_container = read_from_file(self.issue_url_container, self.issue_url_container_file_name,
                                                 self.issue_url_container_file_type, 1)
        for issue_unit in handled_issue_container:
            self.driver.get(issue_unit)  # 得到每个好评问题的url进行访问
            time.sleep(self.sleep_time)  # 注意休息
            logging.info(f"\033[32m=====parse_issue_archive Current URL: {issue_unit}\n\033[0m")
            issue_unit = SpringRainDoctorItem()
            GLOBAL_ISSUE_PARSED_URL += 1
            logging.info(f"\033[32m=====GLOBAL_ISSUE_PARSED_URL: {GLOBAL_ISSUE_PARSED_URL}=====\n\033[0m")
            # 处理春雨医生整理的文字
            try:
                # 执行 JavaScript 代码
                script = """
                        document.querySelector(".qa-arrangement-btn").click();
                    """
                self.driver.execute_script(script)

                issue_archive = WebDriverWait(self.driver, 10).until(  # 捕捉到春雨医生整理的文字
                    expected_conditions.presence_of_element_located(
                        (By.XPATH, "//div[@class='qa-arrangement-body']"))
                )
                logging.debug(f"\033[34m=====current issue_archive: \n{issue_archive}\n\033[0m")

                issue_unit['issue_title'] = re.sub(r'-真实医生回答-春雨医生', '', self.driver.title)
                issue_unit['issue_desc'] = issue_archive.find_element_by_xpath("//p[@class='qa-des'][1]").text
                issue_unit['answer'] = issue_archive.find_element_by_xpath("//p[@class='qa-des'][2]").text
                issue_unit['case_url'] = self.driver.current_url

                logging.info(f"\033[32m=====issue_unit: \n{issue_unit}\n\033[0m")

            except (TimeoutException, IgnoreRequest) as te:  # 春雨医生拒绝访问404
                write_to_file(self.allocations, self.result_file_name, self.result_file_type, "a")
                self.allocations.clear()  # 写完清空
                logging.warning(f"\033[33m=====TimeoutException / IgnoreRequest: 页面加载超时/404: \n{te}\n\033[0m")
                break
            except NoSuchElementException as ne:  # 疾病页面没有问诊记录
                issue_unit['issue_title'] = self.driver.title
                issue_unit['issue_desc'] = ""
                issue_unit['answer'] = ""
                issue_unit['case_url'] = self.driver.current_url
                logging.info(f"\033[32m=====NoSuchElementException issue_unit: \n{issue_unit}\n\033[0m")
                logging.warning(f"\033[33m=====NoSuchElementException: 找不到issue元素: \n{ne}\n\033[0m")
            except KeyboardInterrupt as ki:  # 用户中断操作
                write_to_file(self.allocations, self.result_file_name, self.result_file_type, "a")
                self.allocations.clear()  # 写完清空
                logging.warning(f"\033[33m=====KeyboardInterrupt: 用户中断操作: \n{ki}\n\033[0m")
                break
            except SystemExit as se:  # 程序自动退出，需要将当前容器内容导入文件
                write_to_file(self.allocations, self.result_file_name, self.result_file_type, "a")
                self.allocations.clear()  # 写完清空
                logging.warning(f"\033[33m=====SystemExit: 程序自动退出: \n{se}\n\033[0m")
                break
            except JavascriptException as ae:  # js脚本找不到动态click的css，有可能是此issue没有问诊记录
                write_to_file(self.allocations, self.result_file_name, self.result_file_type, "a")
                self.allocations.clear()  # 写完清空
                logging.warning(f"\033[33m=====JavascriptException: js找不到issue元素: \n{ae}\n\033[0m")
            except Exception as e:
                issue_unit['issue_title'] = re.sub(r'-真实医生回答-春雨医生', '', self.driver.title)
                issue_unit['issue_desc'] = ""
                issue_unit['answer'] = ""
                issue_unit['case_url'] = self.driver.current_url
                logging.info(f"\033[32m=====Other Exception issue_unit: \n{issue_unit}\n\033[0m")
                logging.warning(f"\033[33m=====Other Exception: 其他异常: \n{e}\n\033[0m")
                write_to_file(self.allocations, self.result_file_name, self.result_file_type, "a")
                self.allocations.clear()  # 写完清空
                break
            self.allocations.append(issue_unit)
        write_to_file(self.allocations, self.result_file_name, self.result_file_type, "a")
        self.allocations.clear()  # 写完清空

        # -------------对结果进行数据清洗----------------
        data_clean_from_file(self.result_file_name, self.result_file_type)

        # -------------TODO 将result.csv导入数据库----------------
        self.write_result_to_mysql(self, self.result_file_name, self.result_file_type, self.pipline_list_container)

    # ------------------------------数据写入mysql模块------------------------------
    def write_result_to_mysql(self, filename: str, file_type: str, to_container: list):
        logging.info("\033[32m=====Entering write_result_to_mysql=====\n\033[0m")
        result_pipeline_container = read_from_file(to_container, filename, file_type, 0)
        for result_pipeline_unit in result_pipeline_container:
            logging.debug(f"\033[34m=====result_pipline_unit: {result_pipeline_unit}=====\n\033[0m")
            # bean转换
            dict_result = ast.literal_eval(result_pipeline_unit)
            logging.debug(f"\033[34m=====result_pipline_unit: {dict_result}=====\n\033[0m")
            item_instance = SpringRainDoctorItem(
                issue_title=dict_result.get('issue_title', ''),
                issue_desc=dict_result.get('issue_desc', ''),
                answer=dict_result.get('answer', ''),
                case_url=dict_result.get('case_url', '')
            )
            try:
                self.mysql_pipeline.process_item(self, item_instance)
            except Exception as e:
                logging.warning(f"\033[33m=====Exception in write_result_to_mysql: \n{e}\n\033[0m")
