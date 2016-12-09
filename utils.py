# coding=utf-8

import random
import time

import requests
from fake_useragent import UserAgent
# from retry import retry

from config import REFERER_LIST, TIMEOUT, PROXY_TIME_OUT, piaotian


class CrawlerError(Exception):
    pass

class ParseHtmlError(Exception):
    pass

class SaveError(Exception):
    pass


def add_prefix(url, prefix=piaotian['prefix']):
    if not url.startswith(prefix):
        return ''.join([prefix, url])
    else:
        return url


def get_referer():
    return random.choice(REFERER_LIST)


def get_user_agent():
    ua = UserAgent()
    return ua.random


def fetch(url, proxy=None, timesleep=0.5):
    s = requests.Session()
    s.headers.update({'user-agent': get_user_agent()})

    proxies = None
    if proxy is not None:
        proxies = {
            'http': proxy,
        }

    try:
        r = s.get(url, timeout=TIMEOUT, proxies=proxies)
    except requests.exceptions.RequestException:
        time.sleep(timesleep)
        r = s.get(url, timeout=TIMEOUT, proxies=proxies)
    else:
        time.sleep(timesleep)
        r = s.get(url, timeout=TIMEOUT, proxies=proxies)
    finally:
        assert 199 < r.status_code < 300

    return r

