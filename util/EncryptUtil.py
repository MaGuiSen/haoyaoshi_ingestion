# -*- coding: utf-8 -*-
import hashlib


# 加密工具
def md5(value):
    m2 = hashlib.md5()
    m2.update(value)
    return m2.hexdigest()
