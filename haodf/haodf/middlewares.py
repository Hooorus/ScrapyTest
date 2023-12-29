# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
# import scrapy

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

# class BingchengCookiesMiddleware(scrapy.downloadermiddlewares.cookies.CookiesMiddleware):
#     def process_request(self, request, spider):
#         if request.meta.get("dont_merge_cookies", False):
#             return
#         cookiejarkey = request.meta.get("cookiejar")
#         jar = self.jars[cookiejarkey]
#         # cookies = self._get_request_cookies(jar, request)
#         cookies = spider.get_cookies()
#         self._process_cookies(cookies, jar=jar, request=request)

#         # set Cookie header
#         request.headers.pop("Cookie", None)
#         jar.add_cookie_header(request)
#         self._debug_cookie(request, spider)

class BingchengMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class BingchengDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        # cookies = spider.get_cookies()
        # request.cookeis = cookies

        return None
        # return request

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        cookies_request = request.cookies
        cookies_response = response.headers.get('Set-Cookie', False)
        cookies_compare = cookies_request == cookies_response

        UA_requset = request.headers.get('User-Agent')
        UA_reponse = response.headers.get('User-Agent')

        UA_compare = UA_requset == UA_reponse

        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
