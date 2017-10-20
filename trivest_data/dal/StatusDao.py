# -*- coding: utf-8 -*-
import datetime

from trivest_data.dal import LogDao
from trivest_data.dal.trivest_spider import getTableByName


class StatusDao(object):
    Status_start_request = 'start_request'
    Status_save_success = 'save_success'
    Status_save_fail = 'save_fail'
    Status_no_source = '404'
    Status_no_complete_data = 'no_complete_data'
    Status_no_parse_method = 'no_parse_method'
    Status_dont_need_parse = 'dont_need_parse'

    def __init__(self):
        self.Table = getTableByName('haoyaoshi_status')

    def updateStatus(self, haoyaoshiId, status):
        """
        存在更改，不存在则新增
        :param status: start_request, save_success, save_fail, 404, no_complete_data, no_parse_method, dont_need_parse
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
            existStatus = [self.Status_save_success,
                           self.Status_no_source,
                           self.Status_dont_need_parse,
                           self.Status_no_complete_data,
                           self.Status_no_parse_method,
                           ]
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
            existStatus = [self.Status_save_success,
                           self.Status_no_source,
                           self.Status_dont_need_parse,
                           self.Status_no_complete_data,
                           self.Status_no_parse_method,
                           ]
            results = self.Table.select().where(~(self.Table.status << existStatus)).order_by(self.Table.haoyaoshi_id.asc())
            if len(results):
                return results[0].haoyaoshi_id
            else:
                return -1
        except Exception as e:
            print str(e)
            LogDao.warn(str(e), belong_to='getMinStartId')
            return -1

    def getReCatchList(self, pageIndex):
        try:
            existStatus = [self.Status_save_success,
                           self.Status_no_source,
                           self.Status_dont_need_parse,
                           self.Status_no_complete_data,
                           self.Status_no_parse_method,
                           ]
            results = self.Table.select().where(~(self.Table.status << existStatus))\
                .order_by(self.Table.haoyaoshi_id.asc())\
                .paginate(pageIndex, 15)
            return results
        except Exception as e:
            print str(e)
            LogDao.warn(str(e), belong_to='getReCatchList')
            return []

if __name__ == '__main__':
    pass