"""
@Time    : 2019/10/3 12:26
@Author  : Tsangkam
@File    : Parser.py
"""

import re


def xici_parse(content):
    """
    xici proxy web parse
    :param content: the html source code
    :return: return a list include ip, port, address and type
    """
    return_list = []
    result = re.findall(r'<td>(\d+\.\d+\.\d+\.\d+)</td>'  # ip
                        r'[\s\S]*?<td>(\d+)</td>'  # 端口
                        r'[\s\S]*?<td>[\s\S]*?'
                        r'<a href=".*?">(\S+)</a>[\s\S]*?</td>'  # 地址
                        r'[\s\S]*?<td>(.*?)</td>', content)  # 类型
    for proxy_info in result:
        if proxy_info[3] == 'HTTPS':
            return_list.append((proxy_info[0], proxy_info[1], proxy_info[2]))
    return return_list


def xici_url_construction(max_page=100):
    menu_url = 'https://www.xicidaili.com/nn/'
    menu_list = []
    for i in range(1, max_page):
        menu_list.append(menu_url + str(i))
    return menu_list
