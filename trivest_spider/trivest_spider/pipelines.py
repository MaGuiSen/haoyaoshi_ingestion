# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import datetime

from trivest_data.dal import LogDao
from trivest_data.dal.StatusDao import StatusDao
from trivest_data.dal.trivest_spider import getTableByName


class BasePipeline(object):
    def __init__(self):
        self.belong_to = ''

    def logInfo(self, msg, belong_to='', saveInDB=False):
        belong_to = belong_to or self.belong_to
        LogDao.info(msg, belong_to=belong_to, saveInDB=saveInDB)

    def logWarn(self, msg, belong_to='', saveInDB=True):
        belong_to = belong_to or self.belong_to
        LogDao.warn(msg, belong_to=belong_to, saveInDB=saveInDB)

    def process_item_default(self, item, table, logName):
        statusDao = StatusDao()
        try:
            self.logInfo(u'存%s详情：%s' % (logName, item['title']), saveInDB=False)
            # 查重
            results = table.select().where(table.haoyaoshi_id == item.get('haoyaoshi_id')).count()
            if not results:
                item['update_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                table.create(**item)
                self.logInfo(u'存%s详情：%s 成功 haoyaoshi_id：%s' % (logName, item['title'], item['haoyaoshi_id']))
            else:
                self.logInfo(u'%s详情：%s 已经存在 haoyaoshi_id：%s' % (logName, item['title'], item['haoyaoshi_id']))
            statusDao.updateStatus(item.get('haoyaoshi_id'), statusDao.Status_save_success)
        except Exception as e:
            self.logWarn(str(e))  # u'海立股份，地方性混改样本，或现“客大欺店”' 微信这文章有表情(1366, "Incorrect string value: '\\xF0\\x9F\\x91\\x87\\xF0\\x9F...' for column 'content_html' at row 1")
            self.logWarn(u'存%s详情：%s失败' % (logName, item['title']))
            StatusDao().updateStatus(item.get('haoyaoshi_id'), statusDao.Status_save_fail)

        return item


class HaoYaoShiPipeline(BasePipeline):
    def __init__(self):
        self.belong_to = 'haoyaoshi_detail'
        self.logName = u'好药师'
        self.Table = getTableByName('haoyaoshi_detail')
        pass

    def process_item(self, item, spider):
        # 如果存储方式和process_item_default方法的相同，则直接调用父类的process_item_default
        item = self.process_item_default(item, self.Table, self.logName)
        return item

    def close_spider(self, spider):
        pass


