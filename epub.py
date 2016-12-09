# coding: utf-8
import os
import os.path
import re
import zipfile
# from chardet.universaldetector import UniversalDetector
# from cchardet import Detector as UniversalDetector
import jinja2
import requests
from mongoengine import DoesNotExist

from models import Book, Chapter


__author__ = "ZhangDesheng"

__related_links__ = (
    "http://jingyan.baidu.com/album/3ea51489c553db52e61bbaa1.html?picindex=2",
    "http://blog.itpub.net/29733787/viewspace-1477082/",
    )


def make_epub(bookname):
    epub_name = '.'.join([bookname, "epub"])
    save_dir = os.path.dirname(__file__)
    # os.chdir(save_dir)
    epub_name = os.path.join(save_dir, epub_name)

    try:
        book = Book.objects.get(name=bookname)
    except DoesNotExist:
        print("{}书库中不存在这本书".format(bookname))

    chapterList = Chapter.objects.filter(book=book).order_by("index")

    with zipfile.ZipFile(epub_name, "w") as epub:
        print("-"*20, "制作epub开始", "-"*20)
        create_mimetype(epub)
        create_container(epub)
        create_stylesheet(epub)
        create_cover(epub, book.cover_url)
        create_ncx(epub, chapterList)
        create_opf(epub, chapterList)
        create_chapters(epub, chapterList)
    print("-"*20, "制作epub完成", "-"*20)
    print("-"*20, "epub保存在{0}".format(os.path.join(save_dir, epub_name)), "-"*20)
    return epub_name



def render_chapter(chapter, chapter_template="static/chapter.html"):
    with open(chapter_template) as f:
        template = jinja2.Template(f.read())
        chapter_str = template.render(title=chapter.title, content=chapter.content)
        return chapter_str


def create_mimetype(epub):
    epub.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)


def create_container(epub):
    container_info = '''<?xml version="1.0" encoding="UTF-8" ?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
         <rootfile full-path="OEBPS/fb.opf" media-type="application/oebps-package+xml"/>
    </rootfiles> 
</container>'''
    epub.writestr('META-INF/container.xml', container_info, compress_type=zipfile.ZIP_STORED)


def create_stylesheet(epub, css_name="static/main.css"):
    with open(css_name) as f:
        css_info = f.read()
    epub.writestr('OEBPS/css/main.css', css_info, compress_type=zipfile.ZIP_STORED)


def create_cover(epub, cover_url=None):
    try:
        req = requests.get(cover_url)
        epub.writestr('OEBPS/images/cover.jpg', req.content, compress_type=zipfile.ZIP_STORED)
    except:
        with open("static/cover.jpg", "rb") as f:    
            epub.writestr('OEBPS/images/cover.jpg', f.read(), compress_type=zipfile.ZIP_STORED)


def create_chapters(epub, chapterList):
    for chapter in chapterList:
        epub.writestr("OEBPS/chapter{}.html".format(chapter.index), render_chapter(chapter), compress_type=zipfile.ZIP_STORED)


def create_ncx(epub, chapterList, ncx_template="static/fb.ncx", **kwargs):
    bookname = kwargs.get("bookname", "")
    author = kwargs.get("author", "")
    with open(ncx_template, encoding="utf-8") as f:
        template = jinja2.Template(f.read())
        ncx_str =  template.render(bookname=bookname, author=author, chapterList=chapterList)
        epub.writestr("OEBPS/fb.ncx", ncx_str, compress_type=zipfile.ZIP_STORED)

def create_opf(epub, chapterList, opf_template="static/fb.opf", **kwargs):
    kwargs.update({"rights":  "请支持正版阅读，实在不能支持时才阅读这个版本，请感恩作者。"})
    # with open(opf_template, encoding="utf-8") as f, open("opftext.opf", "w", encoding="utf-8") as fw:
    with open(opf_template, encoding="utf-8") as f:
        template = jinja2.Template(f.read())
        opf_str = template.render(chapterList=chapterList, **kwargs)
        # fw.write(opf_str)
        epub.writestr("OEBPS/fb.opf", opf_str, compress_type=zipfile.ZIP_STORED)


if __name__ == "__main__":
    make_epub("锦衣夜行")