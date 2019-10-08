"""
@Time    : 2019/10/2 23:15
@Author  : Tsangkam
@File    : CrawlerManager.py
"""

from SystemLogWriter import log_writer
from threading import Thread, Semaphore
from multiprocessing import Process
from _queue import Empty
from datetime import datetime
from queue import Queue
import requests
import time

SPIDER_Semaphore = Semaphore(20)


class CrawlerManager(Process):
    """
    a process used to grab proxy from the website.
    """
    def __init__(self, url_getter, data_parse,
                 proxy_queue, data_queue,
                 feedback_queue,
                 maxsize_queue=200, interval_time=900,
                 base_time=5, multiple_time=5):
        """
        The constructor of CM
        :param url_getter:  a function used to get the url list
        :param data_parse:  a function used to parse the html
        :param proxy_queue: a queue stored some proxy
        :param data_queue:  a queue used to transfer useful data from web
        :param feedback_queue:  a queue used to feedback the usage log
        :param interval_time:   a integer used to describe the interval time
        """
        super().__init__()
        self.__proxy_queue = proxy_queue
        self.__feedback_queue = feedback_queue
        self.__data_queue = data_queue
        self.url_getter = url_getter
        self.data_parse = data_parse
        self.interval_time = interval_time
        self.url_queue = None
        self.html_queue = None
        self.crawler_pool = []
        self.time_of_using_local_ip = 0
        self.maxsize_queue = maxsize_queue
        self.base_time = base_time
        self.multiple_time = multiple_time

    def run(self):
        """
        The entrance of the process.
        This process has three threads:
        1.u_listener: used to listen for urls to crawl, and start the crawler
        2.th_rmd: used to searching the completed crawler
        3.h_listener: used to listen for html to parse
        """
        self.url_queue = Queue(maxsize=self.maxsize_queue)
        self.html_queue = Queue(maxsize=self.maxsize_queue)
        u_listener = Thread(target=self.url_listener, name='crawler_creator')
        u_listener.start()
        log_writer('url listener start')
        th_rmd = Thread(target=self.remove_death, name='crawler_sweeper')
        th_rmd.start()
        log_writer('spider sweeper start')
        h_listener = Thread(target=self.html_listener, name='parse_listener')
        h_listener.start()
        log_writer('parse listener start')

        while True:
            log_writer('Crawler Manager wakeup')
            for u in self.url_getter():
                while self.url_queue.qsize()+1 >= self.maxsize_queue:
                    # log_writer('current url:', self.url_queue.qsize())
                    continue
                self.url_queue.put(u)
            log_writer('Crawler Manager going to sleep', self.interval_time, 'sec')
            time.sleep(self.interval_time)

    def remove_death(self):
        global SPIDER_Semaphore
        while True:
            for c in self.crawler_pool:
                if not c.is_alive():    # checking the complete crawler
                    SPIDER_Semaphore.release()
                    if not c.feedback() is None:    # feedback while not local ip address is used
                        self.__feedback_queue.put(c.feedback())
                    if c.delta_time <= 0:   # if the crawler failed, put the url into the url queue again
                        self.url_queue.put(c.url)
                        log_writer(c.url, c.proxy.id if c.proxy else 'local ip', 'failed')
                    else:                   # else put the html text into the html queue
                        self.html_queue.put(c.session.text)
                        log_writer(c.url, c.proxy.id if c.proxy else 'local ip', 'succeed')
                    self.crawler_pool.remove(c)

    def url_listener(self):
        """
        used to listen the url to crawler, and start a crawler as a thread
        """
        start_time = time.time()
        while True:
            SPIDER_Semaphore.acquire()
            # if there is not useful proxy in the proxy queue, use local ip
            try:
                proxy = self.__proxy_queue.get(timeout=self.base_time+self.multiple_time*self.time_of_using_local_ip)
            except Empty:
                proxy = None
                self.time_of_using_local_ip += 1
                log_writer("using local ip", self.time_of_using_local_ip)
            c = Crawler(url=self.url_queue.get(), proxy=proxy)
            c.start()
            self.crawler_pool.append(c)

    def html_listener(self):
        while True:
            proxies_info = self.data_parse(self.html_queue.get())
            for proxy_info in proxies_info:
                self.__data_queue.put(proxy_info)

    def terminate(self):
        log_writer("crawler manager exit")
        super().terminate()


class Crawler(Thread):
    def __init__(self, url, proxy, timeout=10):
        super().__init__()
        self.url = url
        self.proxy = proxy
        self.__start_time = 0
        self.session = None
        self.delta_time = 0
        self.timeout = timeout

    def run(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) '
                          'AppleWebKit/537.36 (KHTML, like Gecko)'
                          'Chrome/52.0.2743.116 Safari/537.36'
        }
        if self.proxy:
            proxies = {"https": "https://" + self.proxy.ip_port()}
        else:
            proxies = None
        # log_writer(proxies)
        try:
            self.__start_time = time.time()
            # log_writer('start to get', self.url)
            self.session = requests.get(self.url, headers=headers,
                                        proxies=proxies, timeout=self.timeout)
            finish_time = time.time()
            self.delta_time = round(finish_time - self.__start_time, 3)
            if self.session.status_code != 200:
                self.delta_time = -1
        except requests.exceptions.Timeout:
            self.delta_time = -1
        except requests.exceptions.ProxyError:
            self.delta_time = -1
        except requests.exceptions.ConnectionError:
            self.delta_time = -1
        except Exception as e:
            log_writer(type(e))
            log_writer(e)

    def feedback(self):
        if not self.proxy:
            return None
        start_time = datetime.fromtimestamp(self.__start_time).strftime('%Y-%m-%d %H:%M:%S')
        usage_info = (self.proxy.id, self.url, start_time, self.delta_time)
        return usage_info


# test use case
if __name__ == "__main__":
    pass
