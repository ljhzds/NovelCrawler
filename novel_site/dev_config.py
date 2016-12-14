# coding: utf-8
import os

_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

SECRET_KEY = 'testkeyzhangdesheng'

MONGODB_SETTINGS = {
    'db': 'novel',
    'host': 'localhost',
    'port': 27017,
    # 'username': '',
    # 'password': ''
}

del os