# coding: utf-8
import re
from bs4 import BeautifulSoup


def add_prefix(url, prefix="http://m.piaotian.net"):
    if not url:
        return url
    if not url.startswith(prefix):
        return ''.join([prefix, url])
    else:
        return url

def get_next_page(html):
    soup = BeautifulSoup(html, "html.parser")
    next_page_tag = soup.find("a", text=re.compile(r"下[1一]?页"))
    if next_page_tag and next_page_tag.has_attr("href"):
        return add_prefix(next_page_tag["href"])
    # reNextPage = re.compile(r'<a[\s\n\t]+href="([\.a-zA-Z0-9_/]*?)">[\s\n\t]?下[1一]?页[\s\n\t]?</a>')
    # if reNextPage.search(html):
    #     return reNextPage.search(html).group(1)
    # else:
    #     return None


def get_book_url(html):
    soup = BeautifulSoup(html, "html.parser")
    book_urls = [config["urlFix"](a["href"])
                 for a in soup.find_all("a", attrs={"href": re.compile(r"/book/\d+.html")})]
    return book_urls


def get_book_info(html):
    soup = BeautifulSoup(html, "html.parser")
    try:
        cover_url = soup.find("div", class_="block_img2").img["src"]
        to_update_url = soup.find("a", text="查看目录")["href"]
        block_txt2 = soup.find("div", class_="block_txt2")
        name, authorname, tag = [p.text.split(
            '：')[-1] for p in block_txt2.find_all("p")[:3]]
        description = soup.find("div", class_="intro_info").text.strip()
        print(name, authorname, tag)
    except:
        raise Exception("解析{}时碰到错误{}。".format(to_update_url, e))
    to_update_url = add_prefix(to_update_url)
    return cover_url, to_update_url, name, authorname, tag, description


def get_chapter_page(html):
    try:
        page_num = re.search(r"第(\d+)/(\d+)页", html).group(1)
    except AttributeError:
        raise AttributeError("未找到当前页码")
    return page_num


def get_chapters_info(html):
    soup = BeautifulSoup(html, "html.parser")
    div_chapters = soup.find("ul", class_="chapter")
    if not div_chapters:
        raise Exception("未找到章节信息: {}".format(soup.title.text))

    return div_chapters.find_all("a")


def get_chapter_content(html):

    reLiner = re.compile(r"<br[\s\t]*/>")
    reSpace = re.compile(r"&nbsp;")
    html = re.sub(reLiner, "\n", html)
    html = re.sub(reSpace, " ", html)
    
    soup = BeautifulSoup(html, "html.parser")
    content_div = soup.find("div", attrs={"id": "nr1"})
    return content_div.text

sites = {
    "piaotian": {
        'category': [
            # 'http://m.piaotian.net/sort/{tag_num}_1/',
            'http://m.piaotian.net/top/allvote_1/',
            'http://m.piaotian.net/top/allvisit_1/',
            'http://m.piaotian.net/top/goodnum_1/',
            'http://m.piaotian.net/full/1/',
        ],
        'prefix': "http://m.piaotian.net",
        'urlFix': add_prefix,
        'bookUrlFunc': get_book_url,
        'nextPageFunc': get_next_page,
        'bookInfoFunc': get_book_info,
        'pageNumFunc': get_chapter_page,
        'chaptersInfoFunc': get_chapters_info,
        'contentFunc': get_chapter_content,
        'encoding': 'gbk',
    },
}


if __name__ == "__main__":
    import requests

    html = requests.get("http://m.piaotian.net/html/6/6603_7/").content.decode("gbk", "ignore")
    r = get_next_page(html)
    print(r)