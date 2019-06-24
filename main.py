import asyncio
import aiohttp
import argparse
from datetime import datetime
import logging

from wiki_parser import Parser

LOGGER_FORMAT = '%(filename)s %(asctime)s %(message)s'
logging.basicConfig(format=LOGGER_FORMAT, datefmt='[%H:%M:%S]')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


arg_parser = argparse.ArgumentParser(
    description='Get every URL presented in article. Repeat for each found link recursive until max depth reached')
arg_parser.add_argument('--depth', type=int, default=4, help='maximum recursion depth')
arg_parser.add_argument('--url', type=str, help='URL of a article in Wikipedia', required=True)


async def main(loop, base_url, max_depth):
    async with aiohttp.ClientSession(loop=loop) as session:
        now = datetime.now()
        parser = Parser(loop, session, max_depth)
        await parser.parse_page(base_url)
        log.info(
            'Parsing with depth {} took {:.2f} seconds'.format(
                max_depth, (datetime.now() - now).total_seconds()))


if __name__ == "__main__":
    args = arg_parser.parse_args()
    base_url = args.url
    max_depth = args.depth
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop, base_url, max_depth))
    loop.close()
