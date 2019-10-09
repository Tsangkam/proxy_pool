"""
@Time    : 2019/10/2 23:34
@Author  : Tsangkam
@File    : ProxyManager.py
"""
from SystemLogWriter import log_writer
import pymysql
from multiprocessing import Process
import threading
import time

CONN_LOCK = threading.Lock()


class ProxyManager(Process):
    """
    A process used to connect with the database
    """
    def __init__(self, appender_queue, getter_queue, usage_queue,
                 verify_queue, host, database, user, pwd, port,
                 multiple_timeout=10, hia_amount=500, rarely_amount=500, rarely_time=3600):
        """
        The constructor of Proxy Manager
        :param appender_queue:  a queue used to get the new proxy
        :param getter_queue:    a queue used to put the HIA proxy
        :param usage_queue:     a queue used to get the usage log
        :param verify_queue:    a queue used to put rarely use proxy
        :param host:    the host of database
        :param database:    the name of database
        :param user:    the user name of database
        :param pwd:     the password of user
        :param port:    the port of database
        :param hia_amount:  the number of get HIA proxy once
        :param rarely_amount:   the number of get rarely use proxy once
        :param rarely_time:     defines how long is rarely use
        """
        super().__init__()
        self.__db = None
        self.__appender_queue = appender_queue
        self.__getter_queue = getter_queue
        self.__usage_queue = usage_queue
        self.__verify_queue = verify_queue
        self.host = host
        self.database = database
        self.user = user
        self.pwd = pwd
        self.port = port
        self.hia_amount = hia_amount
        self.rarely_amount = rarely_amount
        self.rarely_time = rarely_time
        self.multiple_timeout = multiple_timeout

    def add_proxy(self, proxy_info):
        global CONN_LOCK
        CONN_LOCK.acquire()
        cursor = self.__db.cursor()
        try:
            cursor.callproc('Insert_proxy', args=proxy_info)
        except pymysql.err.IntegrityError:
            # log_writer(proxy_info, 'duplicate')
            return False
        finally:
            cursor.close()
            CONN_LOCK.release()
            return True

    def add_usage(self, usage_info):
        sql = 'insert into usage_log(proxy_id, target_url, start_time, elapsed_time)' \
              'values (%s, %s, %s, %s)'
        global CONN_LOCK
        CONN_LOCK.acquire()
        cursor = self.__db.cursor()
        try:
            cursor.execute(sql, usage_info)
            self.__db.commit()
        finally:
            cursor.close()
            CONN_LOCK.release()

    def fill_getter(self):
        global CONN_LOCK
        CONN_LOCK.acquire()
        cursor = self.__db.cursor()
        try:
            cursor.callproc('Select_HIA', args=(self.hia_amount, ))
            return cursor.fetchall()
        finally:
            cursor.close()
            CONN_LOCK.release()

    def get_rarely_proxy(self):
        global CONN_LOCK
        CONN_LOCK.acquire()
        cursor = self.__db.cursor()
        try:
            cursor.callproc('Select_rarely_used', args=(self.rarely_amount, self.rarely_time))
            return cursor.fetchall()
        finally:
            cursor.close()
            CONN_LOCK.release()

    def run(self):
        self.__db = pymysql.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.pwd,
            port=self.port
        )

        appender = threading.Thread(target=self.appender_listener, name='appender_listener')
        appender.start()
        usage = threading.Thread(target=self.usage_listener, name='usage_listener')
        usage.start()
        verify = threading.Thread(target=self.verify_control, name='verify_filler')
        verify.start()
        getter = threading.Thread(target=self.getter_filler, name='proxy_filler')
        getter.start()
        appender.join()
        usage.join()
        getter.join()

    def appender_listener(self):
        log_writer("appender listener start!")
        while self.__db:
            self.add_proxy(self.__appender_queue.get())

    def usage_listener(self):
        log_writer("usage listener start!")
        while self.__db:
            self.add_usage(self.__usage_queue.get())

    def verify_control(self):
        log_writer("verify control start")
        while self.__db:
            proxies_info = self.get_rarely_proxy()
            for proxy_info in proxies_info:
                self.__verify_queue.put(Proxy(proxy_info[0], proxy_info[1], proxy_info[2]))

    def getter_filler(self):
        log_writer("filler start")
        fail_times = 0
        while self.__db:
            proxies_info = self.fill_getter()
            log_writer('put', len(proxies_info), 'proxies')
            if not proxies_info:
                fail_times += 1
                log_writer("no suit proxy", fail_times)
                time.sleep(self.multiple_timeout*fail_times)
                continue
            for proxy_info in proxies_info:
                self.__getter_queue.put(Proxy(proxy_info[0], proxy_info[1], proxy_info[2]))

    def terminate(self):
        log_writer("Proxy Manager exit")
        super().terminate()


class Proxy:
    def __init__(self, proxy_id, proxy_ip, proxy_port):
        self.id = proxy_id
        self.ip = proxy_ip
        self.port = proxy_port

    def ip_port(self):
        return self.ip + ':' + self.port


# test use case
def main():
    pass


if __name__ == '__main__':
    main()
