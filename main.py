import asyncio
import aiohttp
import requests as re
from model import Pages, Links
import lxml.html as html


MAX_DEPTH = 4
MAIN_DOMAIN = 'https://ru.wikipedia.org'
loop = asyncio.get_event_loop()


def update_page_table(url, depth):
    result = Pages.add_page(url, depth)
    if result:
        return True


def update_links_table(parent_url, current_url):
    Links.add_link(parent_url, current_url)


def parse_page(parent_url, depth=1):
    '''
    Get all urls from article ignoring unexisting urls (starts with /w/) and
    non-article urls (everything not in "div id='bodyContent'")
    :param parent_url: url to be parsed
    :param depth: current parse depth
    :return:
    '''
    r = re.get(parent_url)
    tree = html.fromstring(r.text)
    subtree = tree.xpath('//div[@id="bodyContent"]')[0]
    url_list = [i for i in subtree.xpath("*//a/@href") if i.startswith('/wiki')]
    current_depth = depth + 1
    for url in url_list:
        current_url = MAIN_DOMAIN + url
        exists = update_page_table(current_url, current_depth)
        update_links_table(parent_url, current_url)
        if not exists and current_depth != MAX_DEPTH:
            parse_page(current_url, current_depth)