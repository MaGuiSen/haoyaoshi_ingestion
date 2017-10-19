# -*- coding: utf-8 -*-
# 项目唯一标识，分布式，不同的项目思考(规则：项目名称!@项目部署位置!@部署时间!@ 1000-9999的随机数）
projectIdentify = 'hao_yao_shi_spider!@xiamen!@2017-10-19 13:52!@2211'

# key为spider的名称 此配置和数据库：spider_monitor字段一致
spiderDetails = {
    'hao_yao_shi': {
        'table_name': 'haoyaoshi_detail',
        'table_name_zh': u'好药师详情',
        'spider_name': 'hao_yao_shi',
        'spider_name_zh': u'好药师_要品'
    }
}


def getSpiderDetail(spiderName):
    return spiderDetails.get(spiderName, {})