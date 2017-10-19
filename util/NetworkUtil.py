# -*- coding: utf-8 -*-
import urllib


def openWebbrowser(url):
    """
    打开浏览器
    :param url:
    :return:
    """
    pass
    # webbrowser.open(url)


def checkNetWork():
    """
        检测网络
    :return:boolean
    """
    try:
        response = urllib.urlopen('https://www.baidu.com')
        return response.code == 200
    except Exception:
        return False


def checkService():
    """
        检测服务器
    :return:boolean
    """
    return True


def getNewIp():
    """
    重新获取IP
    :return:
    """
    try:
        response = urllib.urlopen(
            'http://localhost:9090/redial?token=qeelyn123!&from=localhost&app=TestRedialHttpServer&ver=1')
        return response.code == 200
    except Exception:
        return False
