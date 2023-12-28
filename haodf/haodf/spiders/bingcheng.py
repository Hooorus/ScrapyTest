#!/usr/bin/env python4

import scrapy

import re
import os
from time import sleep

from haodf.items import AnswerItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def line_str(str, cnt = 20, add = True):
    str = re.sub(r'^[\n\s]*', '', str)
    str = re.sub(r'[\n\s]*$', '', str)
    if add:
        return "=" * cnt  + ' ' + str + ' ' + "=" * cnt
    else:
        return str

def cookeis_check(func):
    def wrapper(self, *args, **kwargs):
        if self.cookies is None:
            self.driver = self.get_driver()
            self.log(line_str(f"calling {func}", 10))
            self.driver.get("https://passport.haodf.com/nusercenter/showlogin")
            #
            normal_login = self.driver.find_element(By.XPATH, "//*[text()='普通登录']")
            normal_login.click()
            sleep(0.5)

            user_name = self.driver.find_element(By.XPATH, r'//*/input[@placeholder="用户名/手机号/邮箱"]')
            user_name.click()
            user_name.send_keys('15355049749')
            sleep(0.5)

            password = self.driver.find_element(By.XPATH, r'//*/input[@placeholder="请输入密码"]')
            password.click()
            password.send_keys('Ingru2023')
            sleep(0.5)

            box = self.driver.find_element(By.XPATH, r'//*/div[@class="status_icon unselected"]')
            box.click()
            sleep(0.5)

            submit = self.driver.find_element(By.XPATH, r'//*/button[@class="submit"]')
            submit.click()
            sleep(0.5)
            self.cookies = self.driver.get_cookies()
        return func(self, *args, **kwargs)
    return wrapper

def get_current_dir():
    def fake():
        pass
    return os.path.abspath(os.path.dirname(fake.__code__.co_filename))


class BingchengSpider(scrapy.Spider):
    name = "bingcheng"
    allowed_domains = ["www.haodf.com"]
    start_urls = [
        "https://www.haodf.com/bingcheng/list.html",
    ]

    cookies = None
    cookies_file = "d:/tests/cookies-haodf-com.txt"
    store_csv = "d:/test/bingcheng.csv"
    store_json = "d:/test/bingcheng.json"
    body_file = "d:/test/body.json"
    handle_httpstatus_list = [301, 302]
    visited_diseases = []
    visited_answers = []

    # dir but driver .ETC
    bin_dir = os.path.abspath(os.path.join(get_current_dir(), "../../bin"))
    chrome = "C:/Scoop/apps/chrome-dev-portable/current/chrome.exe"
    stealthjs = os.path.join(bin_dir, "stealth.min.js").replace("\\", "/")
    chromedriver = os.path.join(bin_dir, "chromedriver.exe").replace("\\", "/")


    def __init__(self, *args, **kwargs):
        if not os.path.isfile(self.chrome):
            raise Exception(f"{self.chrome} not exists.")
        if not os.path.isfile(self.stealthjs):
            raise Exception(f"{self.stealthjs} not exists.")
        if not os.path.isfile(self.chromedriver):
            raise Exception(f"{self.chromedriver} not exists.")

        if os.path.exists(self.store_csv):
            os.remove(self.store_csv)
        if os.path.exists(self.store_json):
            os.remove(self.store_json)

        super().__init__(*args, **kwargs)

    # 用于得到模拟登陆用的driver
    def get_driver(self):
        options = Options()
        options.binary_location = self.chrome
        options.add_argument("start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--ssl-protocol=any')
        options.add_argument('--headless')

        service = Service(executable_path=self.chromedriver)
        driver = webdriver.Chrome(options=options, service=service)
        with open(self.stealthjs) as j:
            js = j.read()
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": js
        })
        return driver

    @cookeis_check
    def parse(self, response):
        """
        入口页面，在左侧栏有所有疾病的入口
        """
        disease_xpath = "//*/li[@class='izixun-department-list']/*/a"
        pattern = re.compile(r"http[s]?://(?!/)")
        url = response.url
        for each in response.xpath(disease_xpath):
            href = "https:" + each.xpath(".//@href").extract_first()
            # 加入了 https 检测
            if not re.match(pattern, href):
                self.log(f'====== warn {href} is is not correct ====')

            disease = each.xpath(".//text()").extract_first()
            self.log(line_str(disease))
            self.log(line_str(href))
            # 下面这行是来自chatgpt的回答
            # yield response.follow(href, self.parse_disease)
            # https://docs.scrapy.org/en/latest/topics/debug.html?highlight=scrapy.request#debugging-spiders
            yield scrapy.Request(url=href,
                           callback=self.parse_disease,
                           meta=dict(disease=disease, incoming_url=url))

    @cookeis_check
    def parse_disease(self, response):
        """
        疾病的回答列表页面，没有要record的记录, 但是要处理翻页
        """
        answer_xpath = "//*/li[@class='clearfix']/span[@class='fl']/a"
        url = response.url
        if url in self.visited_diseases:
            return
        meta = response.meta
        try:
            disease = meta['disease']
            incoming_url = meta['incoming_url']
        except Exception:
            disease = None
            incoming_url = None

        if not disease:
            self.log(line_str(url + " is not right for disease"))
            return
        if not incoming_url:
            self.log(line_str(url + " is not right for incoming_url"))
            return

        self.log(line_str(disease + " from " + incoming_url))

        for each in response.xpath(answer_xpath):
            href = each.xpath(".//@href").extract_first()
            yield scrapy.Request(
                    url=href,
                    callback=self.parse_answer,
                    errback=lambda err: self.log("===== Error ====", err),
                    meta=dict(disease=disease, incoming_url=url))

        pnum1_xpath = "//*/div[@class='p_bar']/a[@class='p_num'][1]"
        pnum3_xpath = "//*/div[@class='p_bar']/a[@class='p_num'][3]"

        pnum1_res = response.xpath(pnum1_xpath)
        pnum3_res = response.xpath(pnum3_xpath)
        href = None

        # 如果是3， 说明是有  首页 上一页  下一页  末页
        if pnum3_res:
            href = pnum3_res.xpath(".//@href").extract_first()
        # 如果是1，说明有 下一页 末页， 或者   首页 上一页
        elif pnum1_res:
            txt = pnum1_res.xpath(".//text()").extract_first()
            if txt.strip() == '下一页':
                href = pnum1_res.xpath(".//@href").extract_first()

        if href is not None:
            if href.startswith("/"):
                href = "https://www.haodf.com" + href

            yield scrapy.Request(
                    url=href,
                    callback=self.parse_disease,
                    errback=lambda err: self.log("===== Error ====", err),
                    meta=dict(disease=disease, incoming_url=url))
        self.visited_diseases.append(url)


    # https://blog.csdn.net/hans99812345/article/details/122916860
    # https://www.haodf.com/bingcheng/8898027056.html
    # https://www.haodf.com/bingcheng/8898021335.html
    # https://www.haodf.com/bingcheng/8898019356.html
    @cookeis_check
    def parse_answer(self, response):
        """
        最终的回答页面， 从这里生成AnwserItem, 录入数据库
        """
        url = response.url
        if url in self.visited_answers:
            return

        if response.status == 302:
            with open("d:/tests/body.html", 'wb') as f:
                f.write(response.body)
            with open("d:/tests/body.txt", 'w') as f:
                f.write(response.text)
            self.log('======= Saved response body for 302 redirect to login ===========')
            return

        try:
            meta = response.meta
            disease = meta['disease']
            incoming_url = meta['incoming_url']
        except Exception:
            disease = 'Test'
            incoming_url = 'https://wwww.haodf.com'

        self.log(line_str(disease + " from " + incoming_url))

        diseaseinfo_xpath = "//p[@class='diseaseinfo']//span"
        suggestions_xpath = "//section[@class='suggestions marginLeft0']//span"
        diseaseinfo = response.xpath(diseaseinfo_xpath).xpath(".//text()").extract()
        suggestions = response.xpath(suggestions_xpath).xpath(".//text()").extract()

        item = AnswerItem()
        item['url'] = url
        item['disease'] = disease
        item['diseaseinfo'] = diseaseinfo
        item['suggestions'] = suggestions
        if not diseaseinfo:
            response.body
        self.log(item)
        self.visited_answers.append(url)
        yield item
