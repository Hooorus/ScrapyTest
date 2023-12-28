#!/usr/bin/env python4

import scrapy

import re
import os


from haodf.items import AnswerItem, DiseaseItem


def line_str(str, cnt = 20, add = True):
    str = re.sub(r'^[\n\s]*', '', str)
    str = re.sub(r'[\n\s]*$', '', str)
    if add:
        return "=" * cnt  + ' ' + str + ' ' + "=" * cnt
    else:
        return str

def cookeis_check(func):
    def wrapper(self, *args, **kwargs):
        if self.cookies == {}:
            print(line_str(f"calling {func}", 10))
            with open(self.cookies_file, 'r') as f:
                lines = f.read().split('\n')
                for line in lines:
                    if not re.match(r'^#', line):
                        lineFields = line.strip().split('\t')
                        if len(lineFields) == 7:
                            self.cookies[lineFields[5]] = lineFields[6]
            print(line_str('cookies loaded'))
            # NOTE: 下面这个不要yield
            scrapy.Request(self.start_urls[0], cookies=self.cookies)
        return func(self, *args, **kwargs)
    return wrapper

class BingchengSpider(scrapy.Spider):
    name = "bingcheng"
    allowed_domains = ["www.haodf.com"]
    start_urls = [
        "https://www.haodf.com/bingcheng/list.html",
    ]
    cookies = {}
    cookies_file = "d:/tests/cookies-haodf-com.txt"
    store_csv = "d:/test/bingcheng.csv"
    store_json = "d:/test/bingcheng.json"
    body_file = "d:/test/body.json"
    handle_httpstatus_list = [301, 302]
    visited_diseases = []
    visited_answers = []

    def __init__(self, *args, **kwargs):
        if os.path.exists(self.store_csv):
            os.remove(self.store_csv)
        if os.path.exists(self.store_json):
            os.remove(self.store_json)
        super().__init__(*args, **kwargs)


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
                print(f'====== warn {href} is is not correct ====')

            disease = each.xpath(".//text()").extract_first()
            print(line_str(disease))
            print(line_str(href))
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
            print(line_str(url + " is not right for disease"))
            return
        if not incoming_url:
            print(line_str(url + " is not right for incoming_url"))
            return

        print(line_str(disease + " from " + incoming_url))

        for each in response.xpath(answer_xpath):
            href = each.xpath(".//@href").extract_first()
            yield scrapy.Request(
                    url=href,
                    callback=self.parse_answer,
                    errback=lambda err: print("===== Error ====", err),
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
                    errback=lambda err: print("===== Error ====", err),
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
        meta = response.meta
        try:
            disease = meta['disease']
            incoming_url = meta['incoming_url']
        except Exception:
            disease = 'Test'
            incoming_url = 'https://wwww.haodf.com'

        print(line_str(disease + " from " + incoming_url))

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
        print(item)

        self.visited_answers.append(url)
        yield item