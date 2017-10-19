# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import datetime
import os

from trivest_data.dal import LogDao
from trivest_data.dal.StatusDao import StatusDao

from util import EncryptUtil
from util import FileUtil
from util import TimerUtil
from util.FileUtil import UploadUtil, ImageCompressUtil
import requests

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
        try:
            self.logInfo(u'存%s详情：%s' % (logName, item['title']), saveInDB=False)
            # 查重
            results = table.select().where(table.haoyaoshi_id == item.get('haoyaoshi_id')).count()
            if not results:
                item['update_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                table.create(**item)
                self.logInfo(u'存%s详情：%s 成功 post_date：%s' % (logName, item['title'], item['post_date']))
            else:
                self.logInfo(u'%s详情：%s 已经存在 post_date：%s' % (logName, item['title'], item['post_date']))
            StatusDao().updateStatus(item.get('haoyaoshi_id'), 'save_success')
        except Exception as e:
            self.logWarn(str(e))  # u'海立股份，地方性混改样本，或现“客大欺店”' 微信这文章有表情(1366, "Incorrect string value: '\\xF0\\x9F\\x91\\x87\\xF0\\x9F...' for column 'content_html' at row 1")
            self.logWarn(u'存%s详情：%s失败' % (logName, item['title']))
            StatusDao().updateStatus(item.get('haoyaoshi_id'), 'save_fail')

        return item


class MyImageDownLoad(BasePipeline):
    @classmethod
    def from_settings(cls, settings):
        botName = settings['BOT_NAME']
        return cls(botName)  # 相当于dbpool付给了这个类，self中可以得到

    def __init__(self, botName):
        self.belong_to = 'ImageDownLoad'
        self.botName = botName
        self.savePath = os.getcwd()
        self.fileUtil = UploadUtil(u'/news/' + botName + u'/image/', self.savePath + u'\\')

    def process_item(self, item, spider):
        image_urls = []
        for image_url in item['image_urls']:
            url = image_url.get('url')
            urlHash = EncryptUtil.md5(url)
            path = 'image\\' + str(urlHash) + '.jpg'
            detailPath = self.savePath + '\\' + path
            # 创建目录
            saveDir = self.savePath + '\\image'
            if not FileUtil.dirIsExist(saveDir):
                FileUtil.createDir(saveDir)

            if FileUtil.fileIsExist(detailPath):
                self.logInfo(u'图片已经存在本地:' + url)
                image_url_new = {
                    'ok': True,
                    'x': {
                        'url': url,
                        'path': path
                    }
                }
            else:
                try:
                    fileResponse = requests.get(url, timeout=10)
                    req_code = fileResponse.status_code
                    req_msg = fileResponse.reason
                    if req_code == 200:
                        open(detailPath, 'wb').write(fileResponse.content)
                        # 判断大小是否大于100kb 压缩到600， 质量为80
                        if len(fileResponse.content) > 100 * 1024:
                            # 目标图片大小
                            dst_w = 600
                            dst_h = 600
                            # 保存的图片质量
                            save_q = 80
                            ImageCompressUtil().resizeImg(
                                        ori_img=detailPath,
                                        dst_img=detailPath,
                                        dst_w=dst_w,
                                        dst_h=dst_h,
                                        save_q=save_q
                            )
                        image_url_new = {
                            'ok': True,
                            'x': {
                                'url': url,
                                'path': path
                            }
                        }
                        # http://p0.ifengimg.com/pmop/2017/1010/E66C2599CE9403A670AD405F4CCAB271B366D7DC_size415_w1290_h692.png
                        self.logInfo(u'图片成功下载,大小:' + str(len(fileResponse.content) / 1024) + 'kb ' + url)
                        self.logWarn(u'最终存储图片,大小:' + str(os.path.getsize(detailPath) / 1024) + 'kb ' + url)
                    else:
                        self.logWarn(u'下载图片失败:' + url)
                        image_url_new = {
                            'ok': False,
                            'x': {
                                'url': url,
                            }
                        }
                except Exception, e:
                    self.logWarn(u'下载图片失败:' + url)
                    image_url_new = {
                        'ok': False,
                        'x': {
                            'url': url,
                        }
                    }
            image_urls.append(image_url_new)
            # 空转2s
            TimerUtil.sleep(2)

        for image_url in image_urls:
            ok = image_url.get('ok', False)
            if ok:
                x = image_url.get('x', {})
                url = x['url']
                path = x['path']
                # 上传照片
                imgUrl = self.fileUtil.upload(path)
                if imgUrl:
                    # 拿出内容，然后替换路径为url
                    item['content_html'] = item['content_html'].replace('&amp;', '&').replace(url, imgUrl)
                    self.logWarn(u'上传图片成功:  ' + str(os.path.getsize(path) / 1024) + 'kb ' + imgUrl)
        item['image_urls'] = image_urls
        return item


class HaoYaoShiPipeline(BasePipeline):
    """
    雪球 详情
    """
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


