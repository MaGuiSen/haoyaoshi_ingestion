#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from logging import FileHandler

__author__ = 'linbingduan'


def construct_json_logger(name, filepath):
    _logger = logging.getLogger(name)
    _logger.propagate = False
    handler = FileHandler(filepath, encoding='utf8')
    handler.setLevel(logging.INFO)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    return _logger


def bas_file_logger(name, filepath):
    _logger = logging.getLogger(name)
    _logger.propagate = False
    handler = FileHandler(filepath, encoding='utf8')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    return _logger


def bas_console_logger(name):
    _logger = logging.getLogger(name)
    _logger.propagate = False
    if not _logger.handlers:
        _ch = logging.StreamHandler()
        _formatter = logging.Formatter('%(asctime)s-%(filename)s line:%(lineno)d : %(message)s')
        _ch.setFormatter(_formatter)
        _logger.addHandler(_ch)
    return _logger


# if __name__ == '__main__':
#     logging.basicConfig(level=logging.INFO)
#     logger = construct_json_logger('test', 'C:/Users/Brandon/git/chatrob/Temp/test.log')
#     logger.info(json.dumps({'name_': 'Brandon', 'age': 23, 'desc': '此处出來是內容'}, ensure_ascii=False, encoding='utf8'))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = bas_console_logger('test')
    logger.info('log content')
    logger.info('log content1')
    logger.info('log content2')
