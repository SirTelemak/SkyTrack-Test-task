import asyncio
import aiohttp
import argparse
from datetime import datetime
import logging
from model import Pages, Links
import lxml.html as html


MAX_DEPTH = 4
MAIN_DOMAIN = 'https://ru.wikipedia.org'
LOGGER_FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=LOGGER_FORMAT, datefmt='[%H:%M:%S]')
log = logging.getLogger()
log.setLevel(logging.INFO)


def update_page_table(url, depth=1):
    result = Pages.add_page(url, depth)
    if result:
        return True


def update_links_table(parent_url, current_url):
    Links.add_link(parent_url, current_url)


def get_url_list(resp):
    tree = html.fromstring(resp)
    subtree = tree.xpath('//div[@id="bodyContent"]')[0]
    return {i for i in subtree.xpath("*//a/@href") if i.startswith('/wiki')}


async def fetch(session, url):
    async with session.get(url) as resp:
        return await resp.text()


# TODO: remake to async code
async def parse_page(loop, session, parent_url, depth=1):
    '''
    Get all urls from article ignoring unexisting urls (starts with /w/) and
    non-article urls (everything not in "div id='bodyContent'")
    :param parent_url: url to be parsed
    :param depth: current parse depth
    :return:
    '''
    response = await fetch(session, parent_url)
    url_list = get_url_list(response)
    current_depth = depth + 1
    tasks = []
    for url in list(url_list)[:2]:
        current_url = MAIN_DOMAIN + url
        added = update_page_table(current_url, current_depth)
        update_links_table(parent_url, current_url)
        if added and current_depth < MAX_DEPTH:
            tasks.append(parse_page(loop, session, current_url, current_depth))
    await asyncio.gather(*tasks)


async def main(loop, base_url):
    async with aiohttp.ClientSession(loop=loop) as session:
        now = datetime.now()
        await parse_page(loop, session, base_url)
        log.info(
            '> Parsing with depth 4 took {:.2f} seconds'.format(
                (datetime.now() - now).total_seconds()))


if __name__ == "__main__":
    base_url = 'https://ru.wikipedia.org/wiki/Carrissoa'
    update_page_table(base_url)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop, base_url))
    loop.close()
