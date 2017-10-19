# -*- coding: utf-8 -*-
import re
import requests
from csscompressor import compress
from util import EncodeUtil


def downLoad(url):
    try:
        result = requests.get(url, timeout=20)
        if result.status_code == 200:
            return EncodeUtil.toUnicode(result.content)
        else:
            return ''
    except:
        return ''


def compressCss(listCss):
    listCss = ''.join(listCss or [])
    return compress(listCss)


def clearBackgroundColor(value, colorList):
    for color in colorList:
        # background:#f3f3f3;
        pAll = re.compile('background\s*:\s*' + color + ';?')
        matches = pAll.findall(value)
        if len(matches):
            for match in matches:
                value = value.replace(match, '')
        # background-color:#f3f3f3;
        pAll = re.compile('background-color\s*:\s*' + color + ';?')
        matches = pAll.findall(value)
        if len(matches):
            for match in matches:
                value = value.replace(match, '')
    return value


def clearUrl(value):
    # 替换样式里面的链接
    # url\(\s *\"?http.*?\"?\s*\)
    # url(http://storage.fedev.sina.com.cn/components/floatBarRight/40b6e9494c042dc1cb8682aac0e174d0.png)
    # url( "http://mat1.gtimg.com/www/images/channel_logo/tech_logo.png "  )
    # url(data:image/png;base64,iVBORw0KGgo)
    pAll = re.compile('url\(.*?\)')
    matchUrls = pAll.findall(value)
    if len(matchUrls):
        for matchUrl in matchUrls:
            value = value.replace(matchUrl, 'url("")')

    # ngMethod=scale,src=http://www.sinaimg.cn/IT/deco/2014/0619/index/playIconH.png)}
    # # (src="https://mat1.gtimg.com/news/base2011/img/trs.png"
    pAll = re.compile('src=\".*\"|src=.*?\)')
    matchUrls = pAll.findall(value)
    if len(matchUrls):
        for matchUrl in matchUrls:
            value = value.replace(matchUrl, 'src="")')
    return value
