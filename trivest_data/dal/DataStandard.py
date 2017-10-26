# -*- coding: utf-8 -*-
import json

import datetime

from scrapy import Selector

from trivest_spider import getTableByName


def getDetailList(pageIndex):
    table = getTableByName('haoyaoshi_detail')
    return table.select().order_by(table.haoyaoshi_id.asc()).paginate(pageIndex, 15)


def circleRun(operate):
    pageIndex = 1
    while True:
        if operate(pageIndex):
            print 'end', pageIndex
            break
        print 'pageIndex', pageIndex
        pageIndex += 1


def operate(pageIndex):
    dataList = getDetailList(pageIndex)
    if not dataList:
        return True
    for item in dataList:
        # 得到type
        typeListStr = item.types

        # 已经处理了
        # operateType(haoyaoshiId, typeListStr)

        targetObj = {}
        # 已经处理了
        # operateProp(item)
        # resetPrice(haoyaoshiId, item.pro_price, item.old_price, targetObj)
        getMainProp(targetObj, item)
        targetObj['title'] = item.title
        targetObj['update_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        targetObj['img_urls'] = item.img_urls
        targetObj['remark'] = item.remark
        pass


# 将属性提取出来，存入到属性表中
def operateProp(item):
    haoyaoshiId = item.haoyaoshi_id
    # 已经处理了
    # reParseDetailInfo(haoyaoshiId, item.pd_detail_info)
    operateBaseInfo(haoyaoshiId, item.pd_base_info)
    operateDetailInfo(haoyaoshiId, item.pd_detail_info_parsed)
    operateSpecification(haoyaoshiId, item.pd_specification)


# 获取关键字段
def getMainProp(targetObj, item):
    # 商品规格，规格
    # 货号
    # 生产企业，生产厂家
    # 通用名称，通用名
    pass
    baseInfoStr = item.pd_base_info or '{}'
    detailInfoStr = item.pd_detail_info_parsed or '{}'
    specificationStr = item.pd_specification or '[]'

    # 规格
    baseInfoObj = json.loads(baseInfoStr)
    detailInfoObj = json.loads(detailInfoStr)
    specificationObj = json.loads(specificationStr)

    # baseInfoObj = {u"商品规格": u"10只"}
    # detailInfoObj = {u"货号": u"货号2", u"商品规格": "22222", u'生产厂家': 'das'}
    #
    # specificationObj = [{"propertyName": u"货号", "propertyValue": u"货号3"}, {"propertyName": u"通用名", "propertyValue": "11111"}]

    specificationObjNew = {}
    for obj in specificationObj:
        key = obj.get('propertyName', '')
        specificationObjNew[key] = obj.get('propertyValue', '')
    specificationObj = specificationObjNew

    def getValue(keyList):
        def run(obj):
            value = ''
            for key in keyList:
                value = obj.get(key)
                if value:
                    break
            return value

        value = ''
        for obj in [baseInfoObj, detailInfoObj, specificationObj]:
            value = run(obj)
            if value:
                break
        return value

    guige = getValue([u'规格', u'商品规格'])
    huohao = getValue([u'货号'])
    create_factory = getValue([u'生产企业', u'生产厂家'])
    common_name = getValue([u'通用名称', u'通用名'])

    # 得到新的对象，不包含对应属性的对象
    def delKey(obj, delKeyList):
        newObj = {}
        for key in obj:
            isDel = False
            for keyDel in delKeyList:
                if keyDel == key:
                    isDel = True
                    break
            if not isDel:
                newObj[key] = obj[key]
                print key, obj[key]
        return newObj

    delKeyList = [u'规格', u'商品规格', u'货号', u'生产企业', u'生产厂家', u'通用名称', u'通用名']
    baseInfoObj = delKey(baseInfoObj, delKeyList)
    detailInfoObj = delKey(detailInfoObj, delKeyList)
    specificationObj = delKey(specificationObj, delKeyList)
    print guige, huohao, create_factory, common_name
    targetObj['guige'] = guige
    targetObj['huohao'] = huohao
    targetObj['create_factory'] = create_factory
    targetObj['common_name'] = common_name

# 处理说明书
def operateSpecification(haoyaoshiId, objStr):
    if not objStr:
        return
    propObj = json.loads(objStr)
    for obj in propObj:
        key = obj.get('propertyName', '')
        savePropKey(haoyaoshiId, key)


# 重新处理详细信息部分的解析
def reParseDetailInfo(haoyaoshiId, pd_detail_info):
    if not pd_detail_info:
        return
    pass
    table = getTableByName('haoyaoshi_detail')
    selector = Selector(text=pd_detail_info)
    proDetailInfoParsed = {}
    proDetailInfos = selector.xpath('//span')
    for proDetailInfo in proDetailInfos:
        key = proDetailInfo.xpath('./text()').extract_first('')
        value = proDetailInfo.xpath('./@title').extract_first('')
        value = value.strip()
        key = key.replace(value, '').replace(':', '').replace(u'：', '').strip()

        if key and value:
            proDetailInfoParsed[key] = value
    proDetailInfoParsed = json.dumps(proDetailInfoParsed, ensure_ascii=False)
    print u'更新'
    table.update(pd_detail_info_parsed=proDetailInfoParsed).where(table.haoyaoshi_id == haoyaoshiId).execute()
    print u'更新完成'


# 处理基本信息
def operateBaseInfo(haoyaoshiId, propObjStr):
    if not propObjStr:
        return

    propObj = json.loads(propObjStr)
    for name in propObj:
        savePropKey(haoyaoshiId, name)


# 处理详情
def operateDetailInfo(haoyaoshiId, propObjStr):
    if not propObjStr:
        return

    propObj = json.loads(propObjStr)
    for name in propObj:
        savePropKey(haoyaoshiId, name)


def savePropKey(haoyaoshiId, name):
    if not name:
        return
    print haoyaoshiId, name
    table = getTableByName('haoyaoshi_prop_key')
    results = table.select().where(table.name == name)
    if not results:
        print u'新的：', haoyaoshiId, name
        table.create(
            name=name
        )


def resetPrice(haoyaoshiId, proPriceShow, oloPriceShow, targetObj):
    def getPriceNum(priceShow):
        priceShow = priceShow.replace(u'￥', '')
        if priceShow:
            return float(priceShow)
        else:
            return -1
    proPriceShow = proPriceShow.replace(' ', '').strip()
    oldPriceShow = oloPriceShow.replace(' ', '').strip()
    proPrice = getPriceNum(proPriceShow)
    oldPrice = getPriceNum(oldPriceShow)

    targetObj['pro_price'] = proPrice
    targetObj['old_price'] = oldPrice
    targetObj['pro_price_show'] = proPriceShow
    targetObj['old_price_show'] = oldPriceShow
    print haoyaoshiId, proPrice, oldPrice, proPriceShow, oldPriceShow


def saveType(name, parentId):
    table = getTableByName('haoyaoshi_type')
    results = table.select().where(table.name == name)
    if results:
        # 存在则返回id
        table.update(parent_id=parentId).where(table.name == name).execute()
        return results[0].id
    else:
        return table.create(
            name=name,
            parent_id=parentId
        ).id


def saveTypeLink(haoyaoshiId, typeId):
    table = getTableByName('haoyaoshi_type_link')
    results = table.select().where(table.haoyaoshi_id == haoyaoshiId, table.type_id == typeId)
    if not results:
        table.create(
            haoyaoshi_id=haoyaoshiId,
            type_id=typeId
        )


# 处理类型，将类型存入类型表，并建立关联
def operateType(haoyaoshiId, typeListStr):
    print typeListStr
    typeList = json.loads(typeListStr)
    parentId = -1
    for typeItem in typeList:
        # 存数据库
        # 得到那条id
        currId = saveType(typeItem, parentId)
        # 存关联
        saveTypeLink(haoyaoshiId, currId)
        parentId = currId


if __name__ == '__main__':
    # circleRun(operate)
    baseInfoObj = {u"商品规格": u"10只"}
    detailInfoObj = {u"货号": u"货号2", u"商品规格": "22222", u'生产厂家': 'das'}

    specificationObj = [{"propertyName": u"货号", "propertyValue": u"货号3"}, {"propertyName": u"通用名", "propertyValue": "11111"}]

    def delKey(obj, delKeyList):
        newObj = {}
        for key in obj:
            isDel = False
            for keyDel in delKeyList:
                if keyDel == key:
                    isDel = True
                    break
            if not isDel:
                newObj[key] = obj[key]
                print key, obj[key]
        return newObj


    # delKey(detailInfoObj, [u'货号', u'生产厂家'])