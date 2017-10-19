# -*- coding: utf-8 -*-
from util import EncryptUtil
import LogDao
from trivest_data.dal.trivest_spider import getTableByName
from GlobleConfig import getSpiderDetail


class CheckDao(object):
    def __init__(self, spiderName):
        self.hashList = []  # 代表此次已经存在的hash,防止同一时间得到相同文章进行抓取
        tableName = getSpiderDetail(spiderName).get('table_name', '')
        self.Table = getTableByName(tableName)

    def resetHashList(self):
        # 每次重新抓取的时候清除
        self.hashList = []

    def checkExist(self, source_url):
        """
        存在逻辑判断
        """
        hash_code = self.getHashCode(source_url)
        try:
            results = self.Table.select().where(self.Table.hash_code == hash_code).count()
            if results or self.isInHashList(hash_code):
                return True
            else:
                self.hashList.append(hash_code)
                return False
        except Exception as e:
            LogDao.warn(str(e), belong_to='CheckDao')
            return False

    def checkWxArticleExist(self, title, wx_account, source_id):
        """
        存在逻辑判断
        source_id : 源ID 微信为1
        """
        hash_code = self.getWxArticleHashCode(title, wx_account, source_id)
        try:
            results = self.Table.select().where(self.Table.hash_code == hash_code).count()
            if results or self.isInHashList(hash_code):
                return True
            else:
                self.hashList.append(hash_code)
                return False
        except Exception as e:
            LogDao.warn(str(e), belong_to='CheckDao')
            return False

    def isInHashList(self, hash_code):
        return hash_code in self.hashList

    def getWxArticleHashCode(self, title, wx_account, source_id):
        # 具体逻辑 微信专用，别的请使用getHashCode
        return EncryptUtil.md5(title.encode('utf8')+wx_account.encode('utf8')+str(source_id))

    def getHashCode(self, source_url):
        # 具体逻辑
        return EncryptUtil.md5(source_url)

    def getAllHtml(self):
        return self.Table.select(self.Table.hash_code, self.Table.content_html)

    def update(self, hash_code, styles, content_html):
        self.Table.update(styles=styles, content_html=content_html).where(self.Table.hash_code == hash_code).execute()

    def getHtml(self, pageIndex):
        """
        获取content_html
        """
        return self.Table.select(self.Table.hash_code, self.Table.content_html)\
            .order_by(self.Table.update_time)\
            .paginate(pageIndex, 15)

    def getSubChannel(self, pageIndex):
        """
        获取sub_channel
        """
        return self.Table.select(self.Table.hash_code, self.Table.sub_channel) \
            .order_by(self.Table.update_time) \
            .paginate(pageIndex, 15)

    def updateStyles(self, hash_code, styles):
        self.Table.update(styles=styles).where(self.Table.hash_code == hash_code).execute()

    def updateHtml(self, hash_code, content_html):
        self.Table.update(content_html=content_html).where(self.Table.hash_code == hash_code).execute()

    def updateSubChannel(self, hash_code, sub_channel):
        self.Table.update(sub_channel=sub_channel).where(self.Table.hash_code == hash_code).execute()


if __name__ == '__main__':
    pass