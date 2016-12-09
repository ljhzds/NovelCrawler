# coding:utf-8

import re

PROXY_SITES = [
    'http://cn-proxy.com',
    'http://www.xicidaili.com',
    'http://www.kuaidaili.com/free',
    'http://www.proxylists.net/?HTTP',
    # www.youdaili.net的地址随着日期不断更新
    'http://www.youdaili.net/Daili/http/4565.html',
    'http://www.youdaili.net/Daili/http/4562.html',
    'http://www.kuaidaili.com',
    'http://proxy.mimvp.com',
]

REFERER_LIST = [
    'http://www.google.com/',
    'http://www.bing.com/',
    'http://www.baidu.com/',
]

PROXY_REGEX = re.compile('[0-9]+(?:\.[0-9]+){3}:\d{2,4}')

DB_HOST = 'localhost'
DB_PORT = 27017
DATABASE_NAME = 'novel'

TIMEOUT = 5
PROXY_TIME_OUT = 2


def get_chapter_page(html):
    try:
        page_num = re.search(r"第(\d+)/(\d+)页", html).group(1)
    except AttributeError:
        raise AttributeError("未找到当前页码")
    return page_num


piaotian = {
    'category': [
        # 'http://m.piaotian.net/sort/{tag_num}_1/',
        'http://m.piaotian.net/top/allvote_1/',
        'http://m.piaotian.net/top/allvisit_1/',
        'http://m.piaotian.net/top/goodnum_1/',
        'http://m.piaotian.net/full/1/',
    ],
    'prefix': "http://m.piaotian.net",
    'reBook': re.compile(r"/book/\d+.html"),
    'reNextpage': re.compile(r"下.*页"),
    'pageNumFunc': get_chapter_page,
    'encoding': 'gbk',
}