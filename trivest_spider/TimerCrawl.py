# -*- coding: utf-8 -*-

import datetime
import subprocess

from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from StatusCache import clearAllStatus, getSpiderStatus

import logging

# 为了处理：No handlers could be found for logger “apscheduler.scheduler”
# logging.basicConfig(level=logging.DEBUG)  # 不设置，就不打印


logging.basicConfig()


def heartBeat():
    pass


def startSpider(spiderName):
    print '执行', spiderName
    if getSpiderStatus(spiderName) != 'running':
        command = "scrapy crawl " + spiderName
        out_bytes = subprocess.check_output(command, shell=True)
    else:
        print(spiderName + u' 还在抓取，跳过这轮start')


def hao_yao_shi():
    startSpider('hao_yao_shi')


def start():
    # 当项目重新启动，清除所有状态
    clearAllStatus()

    def add_job(func, timeSpace, delaySeconds=0):
        # 先马上开始执行
        # scheduler.add_job(func, 'date',misfire_grace_time=120) #misfire_grace_time=120,
        # 后再抓取之后的某个时间段开始间隔执行
        # next_run_time:设置下一轮开始时间
        # max_instances：如 1：表示当前方法正在执行还没有执行完，则不能再次启动这个方法，需等待完成，同理其他数
        # misfire_grace_time:120代表2分钟，当一个任务missing之后，在两分钟内会被重试
        scheduler.add_job(func, 'interval', seconds=timeSpace, misfire_grace_time=120,
                          next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=delaySeconds),
                          start_date=datetime.datetime.now() + datetime.timedelta(seconds=timeSpace), max_instances=1)

    timeSpace = 10 * 60
    heartTime = 1 * 60  # 心跳跳动时间间隔
    # executors不设置，就会出现只能默认有5个线程
    executors = {
        'default': ThreadPoolExecutor(1),  # 根据任务数来定，每增加一个任务，就需要增加这个数量
        'processpool': ProcessPoolExecutor(1)
    }
    scheduler = BlockingScheduler(daemonic=False, executors=executors)
    # 心跳
    add_job(heartBeat, heartTime)

    add_job(hao_yao_shi, timeSpace)

    scheduler.start()


if __name__ == '__main__':
    start()
