# coding: utf-8

import re
import time
from datetime import timedelta
from bs4 import BeautifulSoup
from tornado import httpclient, queues, gen, ioloop
from mongoengine import NotUniqueError

from utils import add_prefix, ParseHtmlError, SaveError, CrawlerError, get_user_agent
from config import piaotian
from models import BookUrl, Book, Chapter, Author


class Item(object):
    def __init__(self, url):
        self.url = url


class BookItem(object):
    def __init__(self, book):
        self.url = book.book_url
        self.book = book


class ChapterItem(object):
    def __init__(self, chapter):
        self.url = chapter.url
        self.chapter = chapter


def _next(soup, nextpage_regex):
    next_page_tag = soup.find("a", text=nextpage_regex)
    if next_page_tag and next_page_tag.has_attr("href"):
        next_page = add_prefix(next_page_tag["href"])
    else:
        next_page = None
    return next_page


def find_urls_and_next_page(item, html, config, **kwargs):
    """
    找到某个页面下所有书本url，
    以及下一页url
    """
    url = item.url

    nextpage_regex = config['reNextpage']
    book_regex = config['reBook']

    soup = BeautifulSoup(html, "html.parser")
    book_urls = [add_prefix(a["href"])
                 for a in soup.find_all("a", attrs={"href": book_regex})]
    next_page = _next()

    item = Item(next_page) if next_page else None

    for url in book_urls:
        BookUrl.get_or_create(url, **kwargs)
    return book_urls, item


def save_book(item, html, config):
    url = item.url

    book_id = re.search(re.compile(r"/book/(\d+).html"), url).group(1)
    book = Book.objects.filter(from_site_book_id=book_id)
    if book:
        return book[0], None
    book = None
    soup = BeautifulSoup(html, "html.parser")

    try:
        cover_url = soup.find("div", class_="block_img2").img["src"]
        book_url = soup.find("a", text="查看目录")["href"]
        block_txt2 = soup.find("div", class_="block_txt2")
        name, authorname, tag = [p.text.split(
            '：')[-1] for p in block_txt2.find_all("p")[:3]]
        description = soup.find("div", class_="intro_info").text.strip()
        print(name, authorname, tag)
    except:
        raise ParseHtmlError("解析{}时碰到错误{}。".format(book_url, e))

    author = Author.get_or_create(authorname)
    book = Book(name=name, author=author, tag=tag, cover_url=cover_url,
                book_url=book_url, description=description)
    try:
        book.save()
    except NotUniqueError:
        raise SaveError("书本已存在:{}".format(name))
    return book, None


def save_chapter(item, html, config, **kwargs):

    url = item.url
    book = item.book
    nextpage_regex = config["reNextpage"]

    soup = BeautifulSoup(html, "html.parser")

    # todo
    # page_num chapter 应该抽象出来到config 里
    div_chapters = soup.find("ul", class_="chapter")
    try:
        page_num = config["pageNumFunc"](html)
    except AttributeError as e:
        raise ParseHtmlError(e)

    if not div_chapters:
        raise ParseHtmlError("未找到章节信息: {0}, {1}".format(book.name, url))

    for i, a in enumerate(div_chapters.find_all("a")):
        title = a.text
        chapter_url = add_prefix(a["href"])
        index = "{:0>4}{:0>4}".format(page_num, i)
        print(chapter_url, title, index)
        chapter = Chapter.get_or_create(
            book=book, url=chapter_url, title=title, index=index)
    next_page = _next(soup, nextpage_regex)
    item = None
    if next_page and next_page != url:
        book.book_url = next_page
        book.save()
        item = BookItem(book)
    return None, item


def save_chapter_content(item, html, config):
    """
    """
    reLiner = re.compile(r"<br[\s\t]*/>")
    reSpace = re.compile(r"&nbsp;")
    html = re.sub(reLiner, "\n", html)
    html = re.sub(reSpace, " ", html)
    soup = BeautifulSoup(html, "html.parser")
    content_div = soup.find("div", attrs={"id": "nr1"})
    chapter = item.chapter
    try:
        content = content_div.text
    except:
        return None, None
    if not content:
        return None, None
    chapter.content = content
    chapter.save()
    return None, None


class Fetcher(object):
    def __init__(self, entries, parse, config):
        """
        entries: 爬虫入口函数
        parse: 当前页面解析函数
        规定parse 接受3个参数： item(object), html(html str), config(dict)
        parse需要返回两个值: target, next_page, target会保存，next_page则继续推送到队列
        config: 该类页面解析规则
        """

        self.entries = entries
        self.config = config
        self.parse = parse

        self.encoding = config.get("encoding", "gbk")

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
            print('Exception: {}, {}'.format(e, url))
            raise gen.Return([None, None])
        raise gen.Return([target, next_item])

    @gen.coroutine
    def fetch(self):
        item = yield self._q.get()
        try:
            if item.url in self.fetching:
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
        for item in self.entries:
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
    def book_urls_get_entries(config=piaotian):
        for url in config["category"]:
            item = Item(url)
            yield item

    def book_get_entries(config=piaotian):
        for bu in BookUrl.objects.filter(base_site=piaotian["prefix"]):
            yield Item(bu.url)

    def chapter_get_entries(config=piaotian, bookname=None):
        for book in Book.objects.filter(name=bookname):
            yield BookItem(book)

    def chapter_content_get_entries(config=piaotian, bookname=None, force_update=False, **kwargs):
        for book in Book.objects.filter(name=bookname):
            if force_update:
                for chapter in Chapter.objects.filter(book=book, **kwargs):
                    yield ChapterItem(chapter)
            else:
                for chapter in Chapter.objects.filter(book=book, **kwargs).filter(content=None):
                    yield ChapterItem(chapter)

    # entries = chapter_get_entries(bookname="锦衣夜行")
    # fetcher = Fetcher(entries, save_chapter, piaotian)
    # fetcher.run()
    entries = chapter_content_get_entries(bookname="锦衣夜行")
    parser = save_chapter_content
    fetcher = Fetcher(entries, parser, piaotian)
    fetcher.run()
    pass
