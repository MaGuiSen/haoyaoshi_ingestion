# -*- coding: utf-8 -*-
import os
from PIL import Image as image
from qcloud_cos import CosClient
from qcloud_cos import UploadFileRequest
from util import TimerUtil
from trivest_data.dal import LogDao


def fileIsExist(pathAndName):
    return os.path.exists(pathAndName)


def dirIsExist(path):
    return os.path.isdir(path)


def createDir(path):
    if not os.path.isdir(path):
        os.mkdir(path)


class ImageCompressUtil(object):
    # 等比例压缩
    def resizeImg(self, **args):
        try:
            args_key = {'ori_img': '', 'dst_img': '', 'dst_w': '', 'dst_h': '', 'save_q': 100}
            arg = {}
            for key in args_key:
                if key in args:
                    arg[key] = args[key]

            im = image.open(arg['ori_img'])
            if im.format in ['gif', 'GIF', 'Gif']:
                return
            ori_w, ori_h = im.size
            widthRatio = heightRatio = None
            ratio = 1
            if (ori_w and ori_w > arg['dst_w']) or (ori_h and ori_h > arg['dst_h']):
                if arg['dst_w'] and ori_w > arg['dst_w']:
                    widthRatio = float(arg['dst_w']) / ori_w  # 正确获取小数的方式
                if arg['dst_h'] and ori_h > arg['dst_h']:
                    heightRatio = float(arg['dst_h']) / ori_h

                if widthRatio and heightRatio:
                    if widthRatio < heightRatio:
                        ratio = widthRatio
                    else:
                        ratio = heightRatio

                if widthRatio and not heightRatio:
                    ratio = widthRatio
                if heightRatio and not widthRatio:
                    ratio = heightRatio

                newWidth = int(ori_w * ratio)
                newHeight = int(ori_h * ratio)
            else:
                newWidth = ori_w
                newHeight = ori_h

            if len(im.split()) == 4:
                # prevent IOError: cannot write mode RGBA as BMP
                r, g, b, a = im.split()
                im = image.merge("RGB", (r, g, b))

            im.resize((newWidth, newHeight), image.ANTIALIAS).save(arg['dst_img'], quality=arg['save_q'])

        except Exception as e:
            LogDao.warn(u'压缩失败' + str(e), belong_to='resizeImg')
            pass


class UploadUtil(object):
    def __init__(self, cos_path, local_path):
        appid = 1251316472  # 替换为用户的appid
        secret_id = u'AKID3atJdSnNR1Bwf1l4HnnYaSMzpBArC4A5'  # 替换为用户的secret_id
        secret_key = u'I2J7ho6wpQRRUpdX8K6KISBJCYSlm1hq'  # 替换为用户的secret_key
        region_info = "sh"  # 替换为用户的region，例如 sh 表示华东园区, gz 表示华南园区, tj 表示华北园区
        self.cos_client = CosClient(appid, secret_id, secret_key, region=region_info)
        self.cos_path = cos_path
        self.local_path = local_path

    def upload(self, path):
        """
            cos_path:/news/jiemian/image/
        :param path
        :return:
        """
        counter = 0
        url = ''
        while counter != 10:
            try:
                # 得到hash
                uploadName = path.replace('image\\', '')
                request = UploadFileRequest(u"crawler", self.cos_path + uploadName,
                                            self.local_path + path,
                                            insert_only=0)
                upload_file_ret = self.cos_client.upload_file(request)
                if upload_file_ret['code'] == 0:
                    data = upload_file_ret['data'] or {}
                    url = data['source_url']
                    print u'上传成功 ' + url
                else:
                    print u'上传图片失败', upload_file_ret
                break
            except Exception as e:
                counter += 1
                TimerUtil.sleep(10)
        return url

# print UploadUtil('','').upload('')

