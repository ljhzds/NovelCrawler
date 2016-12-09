# coding=utf-8
from gevent.pool import Pool
from requests.exceptions import RequestException

from utils import fetch
from models import Proxy


def check_proxy(p):
    try:
        fetch('http://baidu.com', proxy=p['address'])
    except RequestException:
        print(p['address'])
        p.delete()


if __name__ == "__main__":
    # pool = Pool(10)
    # pool.map(check_proxy, Proxy.objects.all())
    print(Proxy.objects.all().count())
    print(Proxy.get_random())