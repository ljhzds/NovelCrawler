# coding: utf-8
import time
from datetime import timedelta

from tornado import httpclient, queues, gen, ioloop

from .utils import get_user_agent


class Fetcher(object):
    def __init__(self, entry, parse, config):
        """
        entry: 爬虫入口函数
        parse: 当前页面解析函数
        规定parse 接受3个参数： item(object), html(html str), config(dict)
        parse需要返回两个值: target, next_page, target会保存，next_page则继续推送到队列
        config: 该类页面解析规则
        """
        self.entry = entry
        self.config = config
        self.parse = parse

        self.encoding = self.config.get("encoding", "gbk")

        self.headers = dict().update({'user-agent': get_user_agent()})

        self.concurrency = 20
        self._q = queues.Queue()
        self.fetching, self.fetched = set(), set()
        self.count = 0

    @gen.coroutine
    def _fetch(self, item, **kwargs):
        url = item.url
        try:
            response = yield httpclient.AsyncHTTPClient().fetch(url, headers=self.headers, **kwargs)
            print("抓取到页面 {}".format(url))
            html = response.body if isinstance(response.body, str) \
                else response.body.decode(self.encoding, "ignore")
            target, next_item = self.parse(item, html, self.config)
        except Exception as e:
            print('{}, {}'.format(e, url))
            raise gen.Return([None, None])
        raise gen.Return([target, next_item])

    @gen.coroutine
    def fetch(self):
        item = yield self._q.get()
        try:
            if item.url in self.fetching or not item.url:
                return
            print("正在抓取: {}".format(item.url))
            # self.fetching.add(item.url)
            result = yield self._fetch(item)
            targets, next_item = result[:]
            # self.fetched.add(item.url)
            self.count += 1
            if next_item:
                self._q.put(next_item)
        finally:
            self._q.task_done()

    @gen.coroutine
    def worker(self):
        while True:
            yield self.fetch()

    @gen.coroutine
    def main(self):
        start = time.time()
        for item in self.entry:
            self._q.put(item)

        for _ in range(self.concurrency):
            self.worker()

        yield self._q.join(timeout=timedelta(seconds=300000))
        # assert self.fetching == self.fetched

        print("共收集了{}页目录信息,耗时{}".format(self.count, time.time() - start))

    def run(self):
        import logging
        logging.basicConfig()
        io_loop = ioloop.IOLoop.current()
        io_loop.run_sync(self.main)


if __name__ == "__main__":
    print("123")
    # 小说URL入库
    # entry = book_url_entry()
    # parser = book_info_parser
    # fetcher = Fetcher(entry, parser, piaotian)
    # fetcher.run()

    # 小说信息入库
    # entry = book_info_entry()
    # parser = book_info_parser
    # fetcher = Fetcher(entry, parser, piaotian)
    # fetcher.run()

    # 小说章节更新
    # entry = chapter_info_entry()
    # parser = chapter_info_parser
    # fetcher = Fetcher(entry, parser, piaotian)
    # fetcher.run()

    # 章节内容更新
    # entry = chapter_content_entry(name__contains="爱")
    # parser = chapter_content_parser
    # fetcher = Fetcher(entry, parser, piaotian)
    # fetcher.run()
    pass
