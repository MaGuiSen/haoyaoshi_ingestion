# -*- coding: utf-8 -*-
import time

import scrapy

from trivest_data.dal import LogDao
from util import NetworkUtil
from util import TimerUtil


# 封装基础方法
class BaseSpider(scrapy.Spider):
    def afterClose(self):
        self.logInfo(u'抓取结束-----------------' + self.name)
        pass

    def beforeRequest(self):
        pass

    def logInfo(self, msg, belong_to='', saveInDB=False):
        belong_to = belong_to or self.name
        LogDao.info(msg, belong_to=belong_to, saveInDB=saveInDB)

    def logWarn(self, msg, belong_to='', saveInDB=False):
        belong_to = belong_to or self.name
        LogDao.warn(msg, belong_to=belong_to, saveInDB=saveInDB)

    def wait_utils_env_ok(self):
        # 检测网络
        while not NetworkUtil.checkNetWork():
            # 20s检测一次
            TimerUtil.sleep(20)
            self.logWarn(u'检测网络不可行')
            # continue

        # 检测服务器
        while not NetworkUtil.checkService():
            # 20s检测一次
            TimerUtil.sleep(20)
            self.logWarn(u'检测服务器不可行')
            # continue
        return True

    def dateFormat(self, dateStr='', targetFormat=''):
        if not dateStr:
            return ''
        dateStr = dateStr\
            .replace('\r\n', '')\
            .replace('\n', '')\
            .strip(' ')\
            .replace(u'年', '-')\
            .replace(u'月', '-')\
            .replace(u'日', ' ')
        needFormats = [
                '%Y-%m-%d',
                '%Y/%m/%d',
                '%m/%d/%Y',
                '%m/%d/%Y %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d %H:%M',
                '%Y/%m/%d %H:%M:%S'
        ]
        targetFormat = targetFormat or '%Y-%m-%d %H:%M:%S'
        for needFormat in needFormats:
            try:
                return time.strftime(targetFormat, time.strptime(dateStr, needFormat))
            except Exception as e:
                print str(e)
                continue
        return ''
