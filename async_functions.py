import asyncio
import pickle
import time
import json
from synchronous_functions import score_case, get_urls, send_email, get_links


async def fetch(queue, highlights, session):
    while True:
        if queue.empty():
            await asyncio.sleep(6)
            continue
        url = await queue.get()
        if url.startswith("/ew"):
            url = "".join(["http://www.bailii.org", url])
            print("downloading {}".format(url))
            try:
                response = await session.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                score, extracts = score_case(await response.text())
                print(score)
                print(extracts)
                if score > 3:
                    highlights.put_nowait((url, extracts))
                queue.task_done()
            except:
                print("{} error connecting to bailii.org".format(
                    time.strftime("%H:%M:%S", time.gmtime())))
                await asyncio.sleep(6)


async def queue_links(queue, session):
    while True:
        print("loading bailii.org... ({})"
              .format(time.strftime("%H:%M:%S", time.gmtime())))
        urls = get_urls()
        try:
            with open("config.json", "r") as f:
                logfile = json.load(f)["logfile"]
            with open(logfile, "rb") as f:
                seen = pickle.load(f)
        except FileNotFoundError as e:
            print("cannot find list of known cases")
            seen = set()
        links = set()
        for url in urls:
            try:
                response = await session.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                links.update(get_links(await response.text()))
            except:
                print("{} error connecting to bailii.org".format(
                    time.strftime("%H:%M:%S", time.gmtime())))
                await asyncio.sleep(60)
        new = links.difference(seen)
        if new:
            for n in new:
                await queue.put(n)
            print("{} {} new case(s)".format(time.strftime("%d/%m/%y %H:%M:%S",
                                                           time.gmtime()),
                                             queue.qsize()))
        else:
            print("no new cases found")
        seen |= new
        try:
            with open("config.json", "r") as f:
                logfile = json.load(f)["logfile"]

            with open(logfile, "wb") as f:
                pickle.dump(seen, f)
        except FileNotFoundError:
            print("config file not found.")
        await asyncio.sleep(43200)  # 12 hours


async def review(highlights):
    while True:
        if highlights.empty():
            await asyncio.sleep(60)
            continue
        else:
            print("updating... {}".format(highlights.qsize()))
            msg = ""
            while not highlights.empty():
                url, extracts = await highlights.get()
                msg += " ".join([url, "\n"])
                msg += " ".join([extracts, "\n"])  # TODO: type error here - expected str got list
                highlights.task_done()
            send_email(msg)
