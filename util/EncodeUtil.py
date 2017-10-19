# -*- coding: utf-8 -*-


def getCoding(strInput):
    """
    获取编码格式
    """
    if isinstance(strInput, unicode):
        return "unicode"
    try:
        strInput.decode("utf8")
        return 'utf8'
    except:
        pass
    try:
        strInput.decode("gbk")
        return 'gbk'
    except:
        pass


def toUnicode(strInput):
    """
    得到unicode
    :return:
    """
    strCodingFmt = getCoding(strInput)
    if strCodingFmt == "utf8":
        return strInput.decode('utf8')
    elif strCodingFmt == "unicode":
        return strInput
    elif strCodingFmt == "gbk":
        return strInput.decode("gbk")


def tran2UTF8(strInput):
    """
    转化为utf8格式
    """
    strCodingFmt = getCoding(strInput)
    if strCodingFmt == "utf8":
        return strInput
    elif strCodingFmt == "unicode":
        return strInput.encode("utf8")
    elif strCodingFmt == "gbk":
        return strInput.decode("gbk").encode("utf8")


def tran2GBK(strInput):
    """
    转化为gbk格式
    """
    strCodingFmt = getCoding(strInput)
    if strCodingFmt == "gbk":
        return strInput
    elif strCodingFmt == "unicode":
        return strInput.encode("gbk")
    elif strCodingFmt == "utf8":
        return strInput.decode("utf8").encode("gbk")
