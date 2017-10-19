# coding=utf-8
# Code generated by:
# python -m pwiz -e mysql -H 192.168.0.20 -p 3306 -u root -i -P trivest_spider
# Date: September 25, 2017 09:29AM
# Database: trivest_spider
# Peewee version: 2.9.2

from peewee import *
from trivest_data.config.app import config
from playhouse.shortcuts import RetryOperationalError
import codecs

codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None)

__mysql_config = config['mysql']


class MyRetryDB(RetryOperationalError, MySQLDatabase):
    pass


database = MyRetryDB(__mysql_config['database'],
                     **{'host': __mysql_config['host'], 'password': __mysql_config['password'],
                        'port': int(__mysql_config['port']), 'user': __mysql_config['user'], 'charset': 'utf8'})

database.execute_sql("SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;")


# TODO...新增一个表的对象，就在此处添加一个键值对，指定数据库名称和类的对应关系
def getTableByName(tableName):
    Tables = {
        'haoyaoshi_status': HaoYaoShiStatus,
        'haoyaoshi_detail': HaoYaoShiDetail,
    }
    return Tables[tableName]


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database


class HaoYaoShiStatus(BaseModel):
    haoyaoshi_id = IntegerField(null=True)
    status = CharField(null=True)
    update_time = DateTimeField(null=True)

    class Meta:
        db_table = 'haoyaoshi_status'


class HaoYaoShiDetail(BaseModel):
    haoyaoshi_id = IntegerField(null=True)
    types = CharField(null=True)
    source_url = CharField(null=True)
    title = CharField(null=True)
    update_time = DateTimeField(null=True)
    img_urls = CharField(null=True)
    pro_price = CharField(null=True)
    old_price = CharField(null=True)
    pd_base_info = CharField(null=True)
    pd_detail_info = CharField(null=True)
    pd_specification = CharField(null=True)

    class Meta:
        db_table = 'haoyaoshi_detail'



