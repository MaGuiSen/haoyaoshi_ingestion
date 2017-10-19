#!/usr/bin/env python
# -*- coding: utf-8 -*-

__mtime__ = '2017/1/20'

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from configparser import ConfigParser


def read_db_config(filename='db_config.ini', section='mysql'):
    """
    read database configuration file a return a dict object
    :param filename:  name of config file
    :param section:  section of the database configuration
    :return:  a dictionary ofg database parameter
    """
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    # sections = parser.sections()
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))
    return db


def read_config(file_name):
    parser = ConfigParser()
    parser.read(file_name)
    result = {}
    for sec in parser.sections():
        items = parser.items(sec)

        item_dict = {}
        for item in items:
            item_dict[item[0]] = item[1]
        result[sec] = item_dict
    return result
