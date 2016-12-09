# coding: utf-8
import re
import time

from models import Book, Chapter, BookUrl
from config import piaotian



# for c in Chapter.objects.filter(url__not__contains="html"):
#     pass
start = time.time()
words = 0
with open('锦衣夜行.txt', 'w', encoding="utf-8") as f:
    for book in Book.objects.filter(name="锦衣夜行"):
        for chapter in Chapter.objects.filter(book=book).order_by("index"):
            print(chapter.index)
            f.write(chapter.title)
            f.write('\n')
            f.write(chapter.content)
            f.write('\n')
            words += len(chapter.content)
print(words)
end = time.time()
print(end-start)