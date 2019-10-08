"""
@Time    : 2019/10/6 21:55
@Author  : Tsangkam
@File    : SquidModify.py
"""
# coding: 'utf8'
from SystemLogWriter import log_writer
from _queue import Empty
import time
import os
import subprocess


def squid_modify(proxy_queue, amount, file_path='squid.conf'):
    peer_conf = "cache_peer %s parent %s 0 no-query proxy-only never_direct allow all" \
                " round-robin weight=1 connect-fail-limit=2 allow-miss max-conn=5\n"
    with open(file_path, 'r', encoding='utf-8') as f:
        squid_conf = f.readlines()
    squid_conf.append('\n# Cache peer config\n')
    actually_append = 0
    for i in range(amount):
        try:
            ip, port = proxy_queue.get(timeout=10).ip_port().split(':')
        except Empty:
            continue
        actually_append += 1
        squid_conf.append(peer_conf % (ip, port))
    with open('/etc/squid/squid.conf', 'w') as f:
        f.writelines(squid_conf)
    failed = os.system('squid -k reconfigure')
    if failed:
        log_writer('something wrong in squid, reboot squid')
        p = subprocess.Popen("ps -ef | grep squid | grep -v grep  | awk '{print $2}'", shell=True,
                             stdout=subprocess.PIPE, universal_newlines=True)
        p.wait()
        result_lines = [int(x.strip()) for x in p.stdout.readlines()]
        log_writer('found', len(result_lines), 'processes')
        if len(result_lines):
            for proc_id in result_lines:
                log_writer('start to kill proc', proc_id)
                os.system('kill -s 9 {}'.format(proc_id))
            log_writer('squid was killed, start new squid now')
            os.system('service squid restart')
            time.sleep(10)
            log_writer('reloading configure')
            os.system('squid -k reconfigure')
        log_writer(actually_append, 'proxy appended')


def modify_launcher(proxy_queue, amount):
    while True:
        squid_modify(proxy_queue, amount)
        time.sleep(15*60)

