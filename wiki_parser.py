import asyncio
import logging
import aiohttp
from lxml import html as html

from model import Pages, Links

LOGGER_FORMAT = '%(filename)s %(asctime)s %(message)s'
logging.basicConfig(format=LOGGER_FORMAT, datefmt='[%H:%M:%S]')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Parser:
    def __init__(self, loop, session, max_depth=4):
        self.max_depth = max_depth
        self.domain = 'https://ru.wikipedia.org'
        self.loop = loop
        self.session = session

    @staticmethod
    def _update_page_table(urls, depth=0):
        urls_to_add = [url for url in urls if not Pages.select().where(Pages.url == url).exists()]
        Pages.add_pages(urls_to_add, depth)

    @staticmethod
    def _update_links_table(parent_url, urls):
        Links.add_link(parent_url, urls)

    def get_url_list(self, resp):
        tree = html.fromstring(resp)
        subtree = tree.xpath('//div[@id="bodyContent"]')[0]
        return {self.domain + i for i in subtree.xpath("*//a/@href") if i.startswith('/wiki')}

    async def get_url_content(self, url, failed=False):
        try:
            async with self.session.get(url) as resp:
                return await resp.text()
        except Exception as e:
            if failed:
                log.info('{}: Failed to process {} again'.format(e, url))
            log.info('{}: Failed to process {}, retrying'.format(e, url))
            asyncio.sleep(2)
            return await self.get_url_content(url, True)

    async def parse_page(self, parent_url, depth=0):
        """
        Get all urls from article ignoring unexisting urls (starts with /w/) and
        non-article urls (everything not in "div id='bodyContent'")
        :param parent_url: url to be parsed
        :param depth: current parse depth
        :return:
        """

        if depth == 0:
            self._update_page_table([parent_url])
        response = await self.get_url_content(parent_url)
        url_list = []
        if response:
            url_list = self.get_url_list(response)

        current_depth = depth + 1

        self._update_page_table(url_list, current_depth)
        self._update_links_table(parent_url, url_list)
        log.info('{} found {} urls'.format(parent_url, len(url_list)))
        if current_depth < self.max_depth:
            tasks = [self.parse_page(url, current_depth) for url in url_list]
            await asyncio.gather(*tasks)
