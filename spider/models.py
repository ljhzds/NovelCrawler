# coding=utf-8
from mongoengine import (connect, StringField, DateTimeField, ReferenceField,
                         DictField, IntField, ListField, Document,
                         DoesNotExist)

from .config import DB_HOST, DB_PORT, DATABASE_NAME

def lazy_connect():
    return connect(DATABASE_NAME, host=DB_HOST, port=DB_PORT)

db = lazy_connect()


class BaseModel(Document):
    create_at = DateTimeField()

    meta = {'allow_inheritance': True,
            'abstract': True}


class Proxy(BaseModel):
    address = StringField(unique=True)

    meta = {'collection': 'proxy'}

    @classmethod
    def get_random(cls):
        proxy = cls.objects.aggregate({'$sample': {'size': 1}}).next()
        return proxy


class BookUrl(BaseModel):
    url = StringField(unique=True)
    base_site = StringField(max_length=100)

    @classmethod
    def get_or_create(cls, url, base_site=None):
        try:
            return cls.objects.get(url=url)
        except DoesNotExist:
            bookurl = cls(url=url, base_site=base_site)
            bookurl.save()
            return bookurl

class Author(BaseModel):
    name = StringField(max_length=50, required=True)
    meta = {'collection': 'author'}

    @classmethod
    def get_or_create(cls, name):
        try:
            return cls.objects.get(name=name)
        except DoesNotExist:
            author = cls(name=name)
            author.save()
            return author


class Chapter(BaseModel):
    title = StringField(max_length=120)
    book = ReferenceField('Book', dbref=True)
    url = StringField(required=True)
    content = StringField()
    index = StringField()

    meta = {
        'collection': 'chapter',
        'indexes': [
            {'fields': ['url'],
             'unique': True
            },
            {'fields': ['book']
            },
            {'fields': ['$title', "$content"],
                # 'default_language': 'zh',
                'weights': {'title': 10, 'content': 2}
            }
        ],
        'ordering': ['url']
    }

    @classmethod
    def get_or_create(cls, book, url, **kwargs):
        try:
            return cls.objects.get(book=book, url=url)
        except DoesNotExist:
            chapter = cls(book=book, url=url, **kwargs)
            chapter.save()
            return chapter



class Book(BaseModel):
    name = StringField(max_length=120, required=True)
    tag = StringField(max_length=100)
    cover_url = StringField()
    book_url = StringField(required=True)
    to_update_url = StringField()
    description = StringField()
    author = ReferenceField(Author, required=True)
    chapters = ListField(ReferenceField(Chapter))
    read_times = IntField(default=1)
    download_times = IntField(default=1)
    from_site = StringField(max_length=50)
    from_site_book_id = StringField(max_length=50)

    meta = {
            'collection': 'book',
            'indexes': [
                '-create_at',
                {'fields': ['name', 'author'],
                 'unique': True}
            ],
            'ordering': ['-read_times', '-download_times', '-create_at']
        }
# db.drop_database('chapter')