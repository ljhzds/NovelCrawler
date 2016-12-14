# coding: utf-8

from flask_mongoengine import MongoEngine
from mongoengine import DoesNotExist

db = MongoEngine()


class BaseModel(db.Document):
    create_at = db.DateTimeField()

    meta = {'allow_inheritance': True,
            'abstract': True}


class Proxy(BaseModel):
    address = db.StringField(unique=True)

    meta = {'collection': 'proxy'}

    @classmethod
    def get_random(cls):
        proxy = cls.objects.aggregate({'$sample': {'size': 1}}).next()
        return proxy


class BookUrl(BaseModel):
    url = db.StringField(unique=True)
    base_site = db.StringField(max_length=100)

    @classmethod
    def get_or_create(cls, url, base_site=None):
        try:
            return cls.objects.get(url=url)
        except DoesNotExist:
            bookurl = cls(url=url, base_site=base_site)
            bookurl.save()
            return bookurl

class Author(BaseModel):
    name = db.StringField(max_length=50, required=True)
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
    title = db.StringField(max_length=120)
    book = db.ReferenceField('Book', dbref=True)
    url = db.StringField(required=True)
    content = db.StringField()
    index = db.StringField()

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
    name = db.StringField(max_length=120, required=True)
    tag = db.StringField(max_length=100)
    cover_url = db.StringField()
    book_url = db.StringField(required=True)
    to_update_url = db.StringField()
    description = db.StringField()
    author = db.ReferenceField(Author, required=True)
    chapters = db.ListField(db.ReferenceField(Chapter))
    read_times = db.IntField(default=1)
    download_times = db.IntField(default=1)
    from_site = db.StringField(max_length=50)
    from_site_book_id = db.StringField(max_length=50)

    meta = {
            'collection': 'book',
            'indexes': [
                '-create_at',
                {'fields': ['name', 'author'],
                 'unique': True}
            ],
            'ordering': ['-read_times', '-download_times', '-create_at']
        }
