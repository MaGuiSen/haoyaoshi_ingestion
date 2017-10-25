# -*- coding: utf-8 -*-
import json

import datetime

from trivest_spider import getTableByName


def getDetailList(pageIndex):
    table = getTableByName('haoyaoshi_detail')
    return table.select().order_by(table.haoyaoshi_id.asc()).paginate(pageIndex, 100)


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
        haoyaoshiId = item.haoyaoshi_id
        # operateType(haoyaoshiId, typeListStr)

        targetObj = {}
        resetPrice(haoyaoshiId, item.pro_price, item.old_price, targetObj)

        # 处理属性,说明书
        # 提取主要几个属性
        # 看是否需要更改属性，和说明书
        # 得到属性key 映射到新表
        targetObj['title'] = item.title
        targetObj['update_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        targetObj['img_urls'] = item.img_urls
        targetObj['remark'] = item.remark
        pass


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


def operateType(haoyaoshiId, typeListStr):
    print typeListStr
    typeList = json.loads(typeListStr)
    parentId = -1
    for typeItem in typeList:
        # 存数据库
        # 得到那条id
        currId = saveType(typeItem, parentId)
        # 存链接
        saveTypeLink(haoyaoshiId, currId)
        parentId = currId


if __name__ == '__main__':
    circleRun(operate)