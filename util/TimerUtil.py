# -*- coding: utf-8 -*-
import time


def sleep(second=1):
    """
    自定义睡眠，防止线程关闭
    """
    startSeconds = int(time.time())
    while True:
        endSeconds = int(time.time())
        if (endSeconds - startSeconds) >= second:
            break
