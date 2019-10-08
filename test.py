"""
@Time    : 2019/10/3 16:12
@Author  : Tsangkam
@File    : test.py
"""

import multiprocessing
import time


class ClockProcess(multiprocessing.Process):
    def __init__(self, interval, q):
        multiprocessing.Process.__init__(self)
        self.interval = interval
        self.q = q

    def run(self):
        while True:
            print('get', self.q.get())
            time.sleep(1)


if __name__ == '__main__':
    print("3.3.3.3:3".split(':'))
