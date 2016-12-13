# coding: utf-8

from spider.fetcher import Fetcher
from spider.parser_and_entry import parsers_and_entries
from spider.novel_site_config import sites
from epub.epub import make_epub


def book_url_fetch(config, **kwargs):
    parser = parsers_and_entries[0][0]
    entry = parsers_and_entries[0][1](**kwargs)
    fetcher = Fetcher(entry, parser, config)
    fetcher.run()


def book_info_fetch(config, **kwargs):
    parser = parsers_and_entries[1][0]
    entry = parsers_and_entries[2][1](**kwargs)
    fetcher = Fetcher(entry, parser, config)
    fetcher.run()


def chapter_info_fetch(config, **kwargs):
    parser = parsers_and_entries[2][0]
    entry = parsers_and_entries[2][1](**kwargs)
    fetcher = Fetcher(entry, parser, config)
    fetcher.run()


def chapter_content_fetch(config, force_update=False, **kwargs):
    parser = parsers_and_entries[3][0]
    entry = parsers_and_entries[3][1](**kwargs)
    fetcher = Fetcher(entry, parser, config)
    fetcher.run()


def main():
    for config in sites.values():
        # book_url_fetch(config=config)
        # book_info_fetch(config=config)
        # chapter_info_fetch(config=config, name__contains="永夜君王")
        chapter_content_fetch(config=config, name__contains="永夜君王")

    make_epub("姐姐爱上我")


if __name__ == "__main__":
    main()