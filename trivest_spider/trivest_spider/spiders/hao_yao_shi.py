# -*- coding: utf-8 -*-
import json

import requests
import scrapy

from base_spider import BaseSpider
from trivest_data.dal.StatusDao import StatusDao
from util import TimerUtil


class HaoYaoShiSpider(BaseSpider):
    """
    好药师
    """
    # download_delay = 2.5
    handle_httpstatus_list = [204, 206, 301, 400, 403, 404, 500] # 错误码中302是处理重定向的，可以不写，因为写了可能导致404无法回掉，写在外部
    name = 'hao_yao_shi'
    custom_settings = {
        'ITEM_PIPELINES': {
            'trivest_spider.pipelines.HaoYaoShiPipeline': 50,
        },
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
        # # 404:27 重定向：32532
        # url = 'http://www.ehaoyao.com/product-%d.html' % 188
        # self.statusDao.updateStatus(188, self.statusDao.Status_start_request)
        # self.logInfo(u"开始抓取列表：" + url)
        # yield scrapy.Request(url=url,
        #                      meta={
        #                          'request_type': self.name + '_detail',
        #                          'haoYaoShiId': 188
        #                      },
        #                      callback=self.parseResult, dont_filter=True)
        # return
        pageIndex = 1
        while True:
            reCatchList = self.statusDao.getReCatchList(pageIndex)
            if not len(reCatchList):
                print 'end'
                break
            print 'pageIndex', pageIndex
            for index, item in enumerate(reCatchList):
                haoYaoShiId = item.haoyaoshi_id
                # 更新状态
                self.statusDao.updateStatus(haoYaoShiId, self.statusDao.Status_start_request)

                # 开始请求
                url = 'http://www.ehaoyao.com/product-%d.html' % haoYaoShiId
                self.logInfo(u"开始抓取旧的：" + url)
                yield scrapy.Request(url=url,
                                     meta={
                                         'request_type': self.name + '_detail',
                                         'haoYaoShiId': haoYaoShiId
                                     },
                                     callback=self.parseResult, dont_filter=True)

            pageIndex += 1

        # 获取从哪一个id开始
        lastStartId = self.statusDao.getStartCatchId()
        maxHaoYaoShiId = 100000
        if lastStartId > maxHaoYaoShiId:
            return

        for haoYaoShiId in range(lastStartId, maxHaoYaoShiId):
            # 更新状态
            self.statusDao.updateStatus(haoYaoShiId, self.statusDao.Status_start_request)

            url = 'http://www.ehaoyao.com/product-%d.html' % haoYaoShiId
            self.logInfo(u"开始抓取新的：" + url)
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
            self.statusDao.updateStatus(haoYaoShiId, self.statusDao.Status_no_source)
            self.logWarn(u'好药师id:%s :404' % haoYaoShiId)
            return
        if status == 403:
            self.statusDao.updateStatus(haoYaoShiId, self.statusDao.Status_be_forbid)
            self.logWarn(u'访问过多被禁止%s :' % haoYaoShiId)
            return
        # 判断使用哪种解析方式, url是最终的url,重定向之后
        url = response.url
        if 'http://www.ehaoyao.com/product' in url:
            contentItem = self.parseDetail1(response)
            if contentItem:
                return contentItem
        elif 'http://www.ehaoyao.us/goods.php' in url:
            # 更改状态：不需要处理
            self.statusDao.updateStatus(haoYaoShiId, self.statusDao.Status_dont_need_parse)
        else:
            # 更改状态：没有解析方法
            self.statusDao.updateStatus(haoYaoShiId, self.statusDao.Status_no_parse_method)

    def parseDetail1(self, response):
        haoYaoShiId = response.meta['haoYaoShiId']
        url = response.url
        if False:
            # 如果某些必要字段没有值：
            self.statusDao.updateStatus(haoYaoShiId, self.statusDao.Status_no_complete_data)
            return None
        else:
            # 继续存
            types = response.xpath('//div[@class="detailTitle"]/a/text()').extract()
            if len(types) >= 2:
                del types[0]
                types.pop()
            else:
                types = []
            types = json.dumps(types, ensure_ascii=False)

            title = response.xpath('//*[@class="title micText"]//text()').extract()
            title = ''.join(title).strip()

            if not title:
                self.statusDao.updateStatus(haoYaoShiId, self.statusDao.Status_no_complete_data)
                return

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

                if key and value:
                    proBaseinfoObj[key] = value

            proBaseInfo = json.dumps(proBaseinfoObj, ensure_ascii=False)
            imageUrls = response.xpath('//*[@id="thumblist"]/li/a/@rel').extract()
            imageUrls = json.dumps(imageUrls, ensure_ascii=False)

            # 暂时保留最基础的html,和转换后的
            proDetailInfoParsed = {}
            proDetailInfos = response.xpath('//*[@class="proDetailInfo cf"]/span')
            for proDetailInfo in proDetailInfos:
                key = proDetailInfo.xpath('./text()').extract_first('')
                value = proDetailInfo.xpath('./@title').extract_first('')
                value = value.strip()
                key = key.replace(':', '').replace(u'：', '').replace(value, '').strip()

                if key and value:
                    proDetailInfoParsed[key] = value

            proDetailInfoParsed = json.dumps(proDetailInfoParsed, ensure_ascii=False)
            proDetailInfo = ''.join(proDetailInfos.extract())



            remark = response.xpath('//*[@class="cut-rate micText"]/text()').extract_first('')
            remark = remark.strip()

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
                'pd_detail_info_parsed': proDetailInfoParsed,
                'pd_specification': specific,
                'remark': remark
            }
            return contentItem

    # 下载说明说
    def downloadSpecific(self, haoYaoShiId):
        count = 0
        while count <= 10:
            # 获取说明书
            try:
                specificUrl = 'http://www.ehaoyao.com/meal/%s/specific?_=1508406771571' % haoYaoShiId
                result = requests.get(specificUrl)
                if result.status_code == 200:
                        content = json.loads(result.content)
                        if content.get('code') == 1:
                            return json.dumps(json.loads(result.content).get('data', {}).get('specificInfo', ''), ensure_ascii=False)
                        return ''
            except Exception as e:
                self.logWarn('downloadSpecific:' + str(e))
                return ''

            count += 1
            TimerUtil.sleep(15)