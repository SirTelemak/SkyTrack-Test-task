import asyncio
import aiohttp
import requests
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


def get_url_list(req):
    tree = html.fromstring(req.text)
    subtree = tree.xpath('//div[@id="bodyContent"]')[0]
    return {i for i in subtree.xpath("*//a/@href") if i.startswith('/wiki')}

# TODO: remake to async code
def parse_page(parent_url, depth=1):
    '''
    Get all urls from article ignoring unexisting urls (starts with /w/) and
    non-article urls (everything not in "div id='bodyContent'")
    :param parent_url: url to be parsed
    :param depth: current parse depth
    :return:
    '''
    request = requests.get(parent_url)
    url_list = get_url_list(request)
    current_depth = depth + 1
    for url in url_list:
        # TODO: do I need all this here or better make additional function
        current_url = MAIN_DOMAIN + url
        added = update_page_table(current_url, current_depth)
        print(added)
        update_links_table(parent_url, current_url)
        if added and current_depth < MAX_DEPTH:
            print(current_depth)
            parse_page(current_url, current_depth)


if __name__ == '__main__':
    base_url = 'https://ru.wikipedia.org/wiki/Carrissoa'
    Pages.add_page(base_url)
    parse_page(base_url)
