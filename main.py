from scrapy.cmdline import execute
import os
import sys

if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    # scrapy crawl <spider_name> <output: -o result.json>
    execute(['scrapy', 'crawl', '99comcn_crawler', '-o result.csv'])
