"""
@Time    : 2019/10/5 13:53
@Author  : Tsangkam
@File    : SystemLogWriter.py
"""

from threading import current_thread
from multiprocessing import current_process, Queue
from time import time
from datetime import datetime
import os

LOG_QUEUE = Queue()
LOG_PATH = 'log/'


def log_writer(*args, end='\n', sep=' '):
    log_path = LOG_PATH + current_process().name + '/' + \
               current_thread().getName() + '/'
    current_time = datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')
    log = '[' + current_time + ' ' + current_process().name + '.' + current_thread().getName() + '] '
    for s in args:
        log += str(s) + ' '
    print(log, end=end, sep=sep)
    if not os.path.isdir(log_path):
        os.makedirs(log_path)
    log_path += datetime.fromtimestamp(time()).strftime('%Y-%m-%d') + '.txt'
    with open(log_path, 'a') as f:
        f.writelines(log + '\n')
