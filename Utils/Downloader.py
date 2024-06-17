import aiohttp
import asyncio
import aiofiles
import os
from typing import List

folder_path = "./Downloads/temp/"

chunksDownloaded = 0
sizeDownloaded = 0

async def download_direct_links(session: aiohttp.ClientSession, urls: List[str], workers: int):
    TOTAL = len(urls)
    chunkSize = TOTAL // workers
    chunkList = [urls[i * chunkSize:(i + 1) * chunkSize] for i in range(workers)]
    chunkList[-1].extend(urls[workers * chunkSize:])

    tasks = [progress(TOTAL)]
    for pos, chunk in enumerate(chunkList, start=1):
        tasks.append(downloadChunks(pos, session, chunk))

    await asyncio.gather(*tasks)

def resetCache():
    global chunksDownloaded, sizeDownloaded
    chunksDownloaded = 0
    sizeDownloaded = 0

    os.makedirs(folder_path, exist_ok=True)

    files = os.listdir(folder_path)
    for file in files:
        os.remove(os.path.join(folder_path, file))

def clearLine(n: int = 1):
    for _ in range(n):
        print("\033[1A\x1b[2K", end="")

async def progress(TOTAL: int):
    global chunksDownloaded, sizeDownloaded
    x = 0
    c = 0

    print("-" * 88)
    print(
        "|"
        + "Chunks Downloaded".center(21)
        + "|"
        + "Chunks/sec".center(14)
        + "|"
        + "Size Downloaded".center(19)
        + "|"
        + "Speed".center(15)
        + "|"
        + "Time Left".center(13)
        + "|"
    )
    print("-" * 88 + "\n\n")

    while chunksDownloaded < TOTAL:
        speed = round((sizeDownloaded - x) / (1024 * 1024 * 2), 2)
        speed2 = round((chunksDownloaded - c) / 2)
        if speed2 == 0:
            speed2 = 1
        time = round(((TOTAL - chunksDownloaded) / speed2) / 60, 2)
        size = round(sizeDownloaded / (1024 * 1024))

        clearLine(2)
        print(
            "|"
            + f"{chunksDownloaded}/{TOTAL}".center(21)
            + "|"
            + f"{speed2} Chunks".center(14)
            + "|"
            + f"{size} MB".center(19)
            + "|"
            + f"{speed} MB/s".center(15)
            + "|"
            + f"{time} min".center(13)
            + "|"
        )
        print("-" * 88)
        x = sizeDownloaded
        c = chunksDownloaded

        await asyncio.sleep(2)

async def downloadChunks(pos: int, session: aiohttp.ClientSession, chunks: List[str]):
    global chunksDownloaded, sizeDownloaded

    async with aiofiles.open(f"{folder_path}{pos}.ts", "ab") as f:
        for i in chunks:
            async with session.get(i) as response:
                resp = await response.read()

            await f.write(resp)

            sizeDownloaded += len(resp)
            chunksDownloaded += 1
