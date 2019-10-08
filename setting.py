"""
@Time    : 2019/10/4 21:39
@Author  : Tsangkam
@File    : setting.py
"""

from multiprocessing import Lock

# Normal setting
MAXSIZE_OF_QUEUE = 200
MAX_QUANTITY_OF_CRAWLER = 20
MAX_QUANTITY_OF_VERIFY = 20
MAX_QUANTITY_OF_HIA_PROXY_SELECT = 50
MAX_QUANTITY_OF_RARELY_USED_PROXY_SELECT = 50
INTERVAL_TIME_OF_RARELY_USED_PROXY = 3600
INTERVAL_TIME_OF_VERIFY = 600

# Database Setting
HOST = 'localhost'
DATABASE = 'proxy_warehouse'
USER = 'root'
PASSWORD = 'kanbujian'
PORT = 3306

# Sleeping time for processing/thread
SLEEPING_TIME_FOR_VERIFY_MANAGER = 1
SLEEPING_TIME_FOR_CRAWLER_MANAGER = 12*60*60
SLEEPING_WHILE_NO_PROXY = 30
MULTIPLE_TIMEOUT_WHILE_NO_PROXY = 10
MULTIPLE_TIMEOUT_WHILE_WAITING_PROXY = 5
BASE_TIMEOUT_WHILE_WAITING_PROXY = 5
TIMEOUT_WHILE_REQUEST = 10

TEST_URL = ['https://www.baidu.com',
            'https://www.bilibili.com/',
            'https://www.xicidaili.com/',
            'https://www.taobao.com/',
            'https://www.sina.com.cn/',
            'https://www.zhihu.com/',
            'https://www.https://github.com/',
            'https://www.jd.com/',
            'https://www.alipay.com/',
            'https://www.cnki.net/']
