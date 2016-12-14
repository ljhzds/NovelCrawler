# coding: utf-8

from flask import Flask
from app.novel.models import db
from app.novel.views import mod


def create_app():
    app = Flask(__name__)
    app.config.from_object('dev_config')
    db.init_app(app)
    app.register_blueprint(mod, url_prefix='/')
    return app
    # db.init_app(app)


