# coding: utf-8

import random

from mongoengine import NotUniqueError

from .models import BookUrl, Book, Chapter, Author
from .utils import ParseHtmlError, SaveError


def book_url_parser(item, html, config, **kwargs):
    """
    找到某个页面下所有书本url，
    以及下一页url
    """
    url = item.url
    book_urls = config["bookUrlFunc"](html)

    next_page = config["nextPageFunc"](html)

    if next_page:
        item.set_url(next_page)
    else:
        item = None

    for url in book_urls:
        BookUrl.get_or_create(url, **kwargs)
    return book_urls, item


def book_info_parser(item, html, config, **kwargs):
    url = item.url

    book = Book.objects.filter(book_url=url)
    if book:
        book = book[0]

    try:
        cover_url, to_update_url, name, authorname, tag, description = config["bookInfoFunc"](html)
    except Exception as e:
        raise ParseHtmlError("解析{}时碰到错误{}。".format(url, e))
    author = Author.get_or_create(authorname)
    if not book:
        book = Book(name=name, author=author, tag=tag, cover_url=cover_url,
                    book_url=url, to_update_url=to_update_url, description=description)
    else:
        book.name = name
        book.author = author
        book.tag = tag
        book.cover_url = cover_url
        book.book_url = url
        book.description = description
        # book.from_site_book_id = book_id
    try:
        book.save()
    except NotUniqueError:
        raise SaveError("书本已存在:{}".format(name))
    return book, None


def chapter_info_parser(item, html, config, **kwargs):

    url = item.url
    book = item.book

    try:
        page_num = config["pageNumFunc"](html)
    except AttributeError as e:
        raise ParseHtmlError(e)
    
    try:
        tagAlist = config["chaptersInfoFunc"](html)
    except:
        raise ParseHtmlError("章节信息解析失败: {}{}".format(book.name, url))

    for i, a in enumerate(tagAlist):
        title = a.text
        chapter_url = config["urlFix"](a["href"])
        index = "{:0>4}{:0>4}".format(page_num, i)
        print(chapter_url, title, index)
        chapter = Chapter.get_or_create(
            book=book, url=chapter_url, title=title, index=index)
 
    next_page = config["nextPageFunc"](html)

    if next_page and next_page != url:
        book.to_update_url = next_page
        book.save()
        item.set_url(next_page)
    else:
        item = None

    return None, item


def chapter_content_parser(item, html, config, **kwargs):
    """
    """
    try:
        content = config["contentFunc"](html)
    except Exception as e:
        print(e)
        raise ParseHtmlError("获取章节正文失败: {}{}".format(item.chapter.title, item.chapter.url))
    if not content:
        return None, None
    item.chapter.content = content
    item.chapter.save()
    return None, None


def book_url_entry(config, **kwargs):
    class Item(object):
        def __init__(self, url):
            self.url = url

        def set_url(self, url):
            self.url = url
    # print('book_url_entry', config)
    return [Item(url) for url in config["category"]]

def book_info_entry(**kwargs):
    class Item(object):
        def __init__(self, url):
            self.url = url

        def set_url(self, url):
            self.url = url
    return [Item(bu.url) for bu in list(BookUrl.objects.all().filter(**kwargs))]

def chapter_info_entry(**kwargs):
    class BookItem(object):
        def __init__(self, book):
            if not book.to_update_url:
                self.url = None
            else:
                self.url = book.to_update_url
            self.book = book

        def set_url(self, url):
            self.url = url

    booklist = Book.objects.all().filter(**kwargs)

    # for test 100 books
    booklist = list(booklist)
    if len(booklist) > 100:
        booklist = random.sample(booklist, 100)

    # for book in booklist:
    #     yield BookItem(book)
    return [BookItem(book) for book in booklist]


def chapter_content_entry(force_update=False, **kwargs):
    class ChapterItem(object):
        def __init__(self, chapter):
            self.url = chapter.url
            self.chapter = chapter

    booklist = Book.objects.all().filter(**kwargs)
    for book in booklist:
        if force_update:
            clist = list(Chapter.objects.all().filter(book=book))
        else:
            clist = list(Chapter.objects.filter(book=book).filter(content=None))
        clist.sort(key=lambda x:x.index)
        for item in [ChapterItem(c) for c in clist]:
            yield item

parsers = (book_url_parser, book_info_parser, chapter_info_parser, chapter_content_parser)
entries = (book_url_entry, book_info_entry, chapter_info_entry, chapter_content_entry)

parsers_and_entries = list(zip(parsers, entries))