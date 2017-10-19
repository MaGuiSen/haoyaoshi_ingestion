# -*- coding: utf-8 -*-
import datetime

from trivest_data.dal import LogDao
from trivest_data.dal.trivest_spider import getTableByName


class StatusDao(object):
    def __init__(self):
        self.Table = getTableByName('haoyaoshi_status')

    def updateStatus(self, haoyaoshiId, status):
        """
        存在更改，不存在则新增
        :param status: start_request, save_success, save_fail, 404, no_complete_data, no_parse_method
        :return:
        """
        pass
        try:
            results = self.Table.select().where(self.Table.haoyaoshi_id == haoyaoshiId)
            if len(results):
                for result in results:
                    result.status = status
                    result.save()
            else:
                table = getTableByName('haoyaoshi_status')
                table.create(haoyaoshi_id=haoyaoshiId,
                             status=status,
                             update_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                             )
        except Exception as e:
            print str(e)
            LogDao.warn(str(e), belong_to='updateStatus')

    def needCatch(self, haoyaoshiId):
        try:
            existStatus = ['success', '404']
            count = self.Table.select()\
                .where(self.Table.haoyaoshi_id == haoyaoshiId, ~(self.Table.status << existStatus))\
                .count()
            return count
        except Exception as e:
            print str(e)
            LogDao.warn(str(e), belong_to='needCatch')
            return False

    def getMinStartId(self):
        try:
            existStatus = ['success', '404']
            results = self.Table.select().where(~(self.Table.status << existStatus)).order_by(self.Table.haoyaoshi_id.asc())
            if len(results):
                return results[0].haoyaoshi_id
            else:
                return -1
        except Exception as e:
            print str(e)
            LogDao.warn(str(e), belong_to='getMinStartId')
            return -1

    def getReCatchList(self):
        try:
            existStatus = ['success', '404']
            results = self.Table.select().where(~(self.Table.status << existStatus)).order_by(self.Table.haoyaoshi_id.asc())
            return results
        except Exception as e:
            print str(e)
            LogDao.warn(str(e), belong_to='getReCatchList')
            return []

if __name__ == '__main__':
    pass
    a={}
    a['11'] = 1
    print a