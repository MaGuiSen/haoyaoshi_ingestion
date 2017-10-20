# -*- coding: utf-8 -*-


# Created by Brandon on 2017/9/25
import os

from util.loggerutils import bas_console_logger
from util.configutils import read_config

__logger = bas_console_logger("app")

env = 'dev_inner'  # dev_local dev_inner
abs_path = os.path.dirname(__file__) + os.sep + 'config_' + env + '.ini'

config = read_config(abs_path)
