# -*- coding: utf-8 -*-
from scrapy import cmdline

# import logging
# logger = logging.getLogger('peewee')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())

spiderName = 'hao_yao_shi'

cmdline.execute(("scrapy crawl " + spiderName + " -s HTTPCACHE_ENABLED=0  ").split())

