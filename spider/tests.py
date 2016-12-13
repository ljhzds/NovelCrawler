# coding: utf-8
import re
import time

from .models import Book, Chapter, BookUrl
from .novel_site_config import sites


# for c in Chapter.objects.filter(url__not__contains="html"):
#     pass
# start = time.time()
# words = 0
# with open('锦衣夜行.txt', 'w', encoding="utf-8") as f:
#     for book in Book.objects.filter(name="锦衣夜行"):
#         for chapter in Chapter.objects.filter(book=book).order_by("index"):
#             print(chapter.index)
#             f.write(chapter.title)
#             f.write('\n')
#             f.write(chapter.content)
#             f.write('\n')
#             words += len(chapter.content)
# print(words)
# end = time.time()
# print(end-start)
count = 0
def find_book(**kwargs):
    for book in Book.objects.all().filter(**kwargs):
        print(book.name, book.book_url, book.to_update_url)
        # book.to_update_url = book.book_url
        # book.save()

def find_chapter(**kwargs):
    for book in Book.objects.all().filter(**kwargs):
        clist = list(Chapter.objects.all().filter(book=book))
        clist.sort(key=lambda x:x.index)
        for x in clist:
            print(book.name, x.title)
            yield x

if __name__ == "__main__":
    find_book(name__contains="爱")