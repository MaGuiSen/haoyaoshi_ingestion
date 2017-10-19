# -*- coding: utf-8 -*-
import json

import scrapy

from base_spider import BaseSpider
from trivest_data.dal.StatusDao import StatusDao
from util import EncodeUtil
import requests

from util import TimerUtil


class HaoYaoShiSpider(BaseSpider):
    """
    好药师
    """
    name = 'hao_yao_shi'

    custom_settings = {
        'download_delay': 2.5,
        'ITEM_PIPELINES': {
            'trivest_spider.pipelines.MyImageDownLoad': 40,
            'trivest_spider.pipelines.HaoYaoShiPipeline': 50,
        },
        'handle_httpstatus_list': [204, 206, 301, 302, 400, 403, 404, 500]
    }

    def __init__(self, name=None, **kwargs):
        super(HaoYaoShiSpider, self).__init__(name=None, **kwargs)
        self.statusDao = StatusDao()

    def close(self, reason):
        # 做一些操作
        self.afterClose()

    def start_requests(self):
        # 做一些操作
        self.beforeRequest()

        if not self.wait_utils_env_ok():
            self.logWarn(u'环境不可行，退出当前抓取')
            return

        url = 'http://www.ehaoyao.com/product-%d.html' % 4404
        self.statusDao.updateStatus(4404, 'start_request')
        self.logInfo(u"开始抓取列表：" + url)
        yield scrapy.Request(url=url,
                             meta={
                                 'request_type': self.name + '_detail',
                                 'haoYaoShiId': 4404
                             },
                             callback=self.parseResult, dont_filter=True)

        return
        # 获取从哪一个id开始
        reCatchList = self.statusDao.getReCatchList()
        lastStartId = 0
        for index, item in enumerate(reCatchList):
            haoYaoShiId = item.haoyaoshi_id
            if index == len(reCatchList):
                lastStartId = haoYaoShiId

            # 更新状态
            self.statusDao.updateStatus(haoYaoShiId, 'start_request')

            # 开始请求
            url = 'http://www.ehaoyao.com/product-%d.html' % haoYaoShiId
            yield scrapy.Request(url=url,
                                 meta={
                                     'request_type': self.name + '_detail'
                                 },
                                 callback=self.parseDetail, dont_filter=True)

        maxHaoYaoShiId = 100000
        if lastStartId + 1 > maxHaoYaoShiId:
            return
        for haoYaoShiId in range(lastStartId + 1, maxHaoYaoShiId):
            # 更新状态
            self.statusDao.updateStatus(haoYaoShiId, 'start_request')

            url = 'http://www.ehaoyao.com/product-%d.html' % haoYaoShiId
            self.logInfo(u"开始抓取列表：" + url)
            yield scrapy.Request(url=url,
                                 meta={
                                     'request_type': self.name+'_detail',
                                     'haoYaoShiId': haoYaoShiId
                                 },
                                 callback=self.parseResult, dont_filter=True)

    def parseResult(self, response):
        status = response.status
        haoYaoShiId = response.meta['haoYaoShiId']
        print status
        if status == 404:
            self.statusDao.updateStatus(haoYaoShiId, '404')
            self.logWarn(u'%s :404' % haoYaoShiId)
            return

        if False:
            self.logWarn(u'访问过多被禁止：')
            return
        pass
        # 判断使用哪种解析方式, url是最终的url,重定向之后
        url = response.url
        if 'http://www.ehaoyao.com/product' in url:
            self.parseDetail1(response)
        elif 'http://www.ehaoyao.us/goods.php' in url:
            self.parseDetail2(response)
        else:
            # 更改状态：没有解析方法
            self.statusDao.updateStatus(haoYaoShiId, 'no_parse_method')

    def parseDetail1(self, response):
        pass
        haoYaoShiId = response.meta['haoYaoShiId']
        url = response.url
        if False:
            # 如果某些必要字段没有值：
            self.statusDao.updateStatus(haoYaoShiId, 'no_complete_data')
        else:
            # 继续存
            types = response.xpath('//div[@class="detailTitle"]/a/text()').extract()
            if len(types) >= 2:
                del types[0]
                types.pop()
            else:
                types = []

            title = response.xpath('//*[@class="title micText"]//text()').extract_first('').strip()
            proPrice = response.xpath('//*[@class="proPrice"]//text()').extract()
            proPrice = ''.join(proPrice)
            oldPrice = response.xpath('//*[@class="oldPrice"]//text()').extract()
            oldPrice = ''.join(oldPrice)

            proBaseinfoObj = {}
            proBaseInfos = response.xpath('//*[@class="proInfo"]/li')
            for proBaseInfo in proBaseInfos:
                keys = proBaseInfo.xpath('./b//text()').extract()

                key = ''.join(keys).replace(u'：', '').replace(':', '').replace(' ', '')
                overKeys = [u'数量', u'配送至']
                isOver = False
                for overKey in overKeys:
                    if overKey in key:
                        isOver = True
                        break
                if isOver:
                    continue

                values = proBaseInfo.xpath('./p//text()').extract()
                value = ''.join(values)

                proBaseinfoObj[key] = value
            pass
            proBaseInfo = json.dumps(proBaseinfoObj)
            imageUrls = response.xpath('//*[@id="thumblist"]/li/a/@rel').extract()
            imageUrls = json.dumps(imageUrls)

            # 暂时保留最基础的html
            proDetailInfos = response.xpath('//*[@class="proDetailInfo cf"]/span').extract()
            proDetailInfo = ''.join(proDetailInfos)

            specific = self.downloadSpecific(haoYaoShiId)

            contentItem = {
                'haoyaoshi_id': haoYaoShiId,
                'types': types,
                'source_url': url,
                'title': title,
                'img_urls': imageUrls,
                'pro_price': proPrice,
                'old_price': oldPrice,
                'pd_base_info': proBaseInfo,
                'pd_detail_info': proDetailInfo,
                'pd_specification': specific
            }
            return contentItem

    # 下载说明说
    def downloadSpecific(self, haoYaoShiId):
        count = 0
        while count <= 10:
            # 获取说明书
            specificUrl = 'http://www.ehaoyao.com/meal/%s/specific?_=1508406771571' % haoYaoShiId
            result = requests.get(specificUrl)
            if result.status_code == 200:
                return result.content
            count += 1
            TimerUtil.sleep(10)




    def parseDetail2(self, response):
        pass
        body = EncodeUtil.toUnicode(response.body)
        haoYaoShiId = response.meta['haoYaoShiId']
        if False:
            # 如果某些必要字段没有值：
            self.statusDao.updateStatus(haoYaoShiId, 'no_complete_data')
        else:
            # 继续存
            pass