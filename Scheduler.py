"""
@Time    : 2019/10/3 0:12
@Author  : Tsangkam
@File    : Scheduler.py
"""
from setting import *
from SystemLogWriter import log_writer
from multiprocessing import Queue, Process
from SquidModify import modify_launcher
import CrawlerManager
import ProxyManager
import VerifyManager
import Parser


def main():
    """
    the entrance of whole system
    :return:
    """
    getter_queue = Queue(maxsize=MAXSIZE_OF_QUEUE)
    appender_queue = Queue(maxsize=MAXSIZE_OF_QUEUE)
    usage_queue = Queue(maxsize=MAXSIZE_OF_QUEUE)
    verify_queue = Queue(maxsize=MAXSIZE_OF_QUEUE)
    pm = ProxyManager.ProxyManager(getter_queue=getter_queue,
                                   appender_queue=appender_queue,
                                   usage_queue=usage_queue,
                                   verify_queue=verify_queue,
                                   host=HOST,
                                   database=DATABASE,
                                   pwd=PASSWORD,
                                   user=USER,
                                   port=PORT,
                                   multiple_timeout=MULTIPLE_TIMEOUT_WHILE_NO_PROXY,
                                   hia_amount=MAX_QUANTITY_OF_HIA_PROXY_SELECT,
                                   rarely_amount=MAX_QUANTITY_OF_RARELY_USED_PROXY_SELECT,
                                   rarely_time=INTERVAL_TIME_OF_RARELY_USED_PROXY)

    vm = VerifyManager.VerifyManager(verify_queue=verify_queue,
                                     feedback_queue=usage_queue,
                                     sleep_time=SLEEPING_TIME_FOR_VERIFY_MANAGER,
                                     interval_time=INTERVAL_TIME_OF_VERIFY)

    cm = CrawlerManager.CrawlerManager(url_getter=Parser.xici_url_construction,
                                       data_parse=Parser.xici_parse,
                                       data_queue=appender_queue,
                                       feedback_queue=usage_queue,
                                       proxy_queue=getter_queue,
                                       maxsize_queue=MAXSIZE_OF_QUEUE,
                                       interval_time=SLEEPING_TIME_FOR_CRAWLER_MANAGER,
                                       base_time=BASE_TIMEOUT_WHILE_WAITING_PROXY,
                                       multiple_time=MULTIPLE_TIMEOUT_WHILE_WAITING_PROXY)
    sm = Process(target=modify_launcher, args=(getter_queue, 20))
    try:
        log_writer('pm start')
        pm.start()  # proxy manager start
        log_writer('vm start')
        vm.start()  # verify manager start
        log_writer('cm start')
        cm.start()  # crawler manager start
        log_writer('squid modifier start')
        sm.start()    # squid modifier start
        # the system controller --only func exit now
        while True:
            order = input()
            if order == 'exit':
                break
    finally:
        if pm.is_alive():
            pm.terminate()
        if vm.is_alive():
            vm.terminate()
        if cm.is_alive():
            cm.terminate()
        if sm.is_alive():
            sm.terminate()


if __name__ == '__main__':
    main()
