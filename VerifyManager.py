"""
@Time    : 2019/10/3 21:22
@Author  : Tsangkam
@File    : VerifyManager.py
"""

from SystemLogWriter import log_writer
from setting import TEST_URL
from multiprocessing import Process
from threading import Thread, Semaphore
from _queue import Empty
import CrawlerManager
import time

SPIDER_Semaphore = Semaphore(20)


class VerifyManager(Process):
    def __init__(self, verify_queue, feedback_queue,
                 interval_time=600, sleep_time=600):
        super().__init__()
        self.__verify_queue = verify_queue
        self.__feedback_queue = feedback_queue
        self.verify_pool = []
        self.sleep_time = sleep_time
        self.interval_time = interval_time

    def run(self):
        global SPIDER_Semaphore
        rmd = Thread(target=self.remove_death)
        rmd.start()
        start_time = time.time()
        while True:
            for url in TEST_URL:
                SPIDER_Semaphore.acquire()
                try:
                    v = CrawlerManager.Crawler(url=url,
                                               proxy=self.__verify_queue.get(timeout=self.interval_time/10))
                    v.start()
                    self.verify_pool.append(v)
                except Empty:
                    continue
                finally:
                    end_time = time.time()
                    if end_time - start_time >= self.interval_time:
                        log_writer("verify manager sleeping", self.sleep_time, 'sec')
                        time.sleep(self.sleep_time)
                        start_time = time.time()
                        log_writer("verify manager wakeup")

    def remove_death(self):
        global SPIDER_Semaphore
        while True:
            for v in self.verify_pool:
                if not v.is_alive():
                    self.__feedback_queue.put(v.feedback())
                    log_writer(v.proxy.id, v.delta_time)
                    self.verify_pool.remove(v)
                    SPIDER_Semaphore.release()
            time.sleep(1)

    def terminate(self):
        log_writer("verify manager exit")
        super().terminate()
