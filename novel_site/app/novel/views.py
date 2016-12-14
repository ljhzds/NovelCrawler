# coding: utf-8

from flask import Blueprint, render_template

from .models import Book

mod = Blueprint('novel', __name__)

@mod.route('/')
def index():
    book = Book.objects.all().filter(name__contains="色")[0]
    return render_template('novel/index.html', hello=book.name)
