import asyncio
import aiohttp
import json
import sys
from async_functions import review, queue_links, fetch


async def run(config):
    session = aiohttp.ClientSession()
    queue = asyncio.Queue()
    highlights = asyncio.Queue()
    _ = [asyncio.ensure_future(fetch(queue, highlights, session))
         for _ in range(5)]
    asyncio.ensure_future(review(highlights))
    await queue_links(queue, session)


if __name__ == "__main__":
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("config file not found.")
        sys.exit(1)
    print("loaded configuration.")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(config))
    loop.close()
