from pyrogram import Client, filters,enums
import asyncio, aiohttp, os
from Utils.File import convertFilePath
from Utils.TechZApi import TechZApi
from Utils.Downloader import startDownload, get_status
from Utils.FFmpeg import ConvertTsToMp4
from techzdl import TechZDL
from config import *


TechZApi = TechZApi()


app = Client(
    name="AniDLX-bot",
    api_hash=API_HASH,
    api_id=int(TELEGRAM_API),
    bot_token=BOT_TOKEN,
    workers=300
)

#Switch
bot = BotApp(TOKEN)




async def upload_progress_handler(progress):
    print(f"Upload progress: {format_bytes(progress.readed + progress.current)}")


async def switch_upload(file):
    file = f"downloads/{file}"
    res = await bot.send_media(
        message=f"{os.path.basename(file)}",
        community_id=COMMUNITY_ID,
        group_id=GROUP_ID,
        document=file,
        part_size=50 * 1024 * 1024,
        task_count=10,
        progress=upload_progress_handler
    )    
    return res
    
def progress_callback(description, done, total):
    print(f"{description}: {format_bytes(done)}/{format_bytes(total)} MB downloaded")



def get_anime():
     with open("AnimeList.txt") as reader:
         animes = reader.read().split("\n")
     with open("AnimeList.txt","w+") as writer:
          for i in animes:
             if i != animes[0]:
                writer.write(f"{i}\n")
     return animes[0]
    





    
async def StartDownload():
 async with app:
    anime = get_anime()
    anime = TechZApi.gogo_anime(anime)["results"]
    title = anime.get("title")
    episodes = anime["episodes"]
    for ep in episodes:
        episode_id = ep[1]
        ep = ep[0]
        try:
            anime['name'] = anime['name'].replace("/", " ").replace("\\",' ')
            print(f"\n\n>> Downloading Episode {ep} - {quality}p")
            data = TechZApi.gogo_download(episode_id)["results"]
            url = [ [ i,data[i]] for i in data ]
            file_path = f"{anime.get('name')} - Episode {ep} - {url[-1][0]}p.mp4"
            downloader = TechZDL(
                              url=video_url,
                              debug=False,
                              file_name=file_path,
                              progress=False,
                              progress_callback=progress_callback,
                              progress_interval=2,)
            await downloader.start()
            file_info = await downloader.get_file_info()
            print(f"Filename: {file_info['filename']}")
            if downloader.download_success:
                    print(f">> Episode {ep} - {quality}p Downloaded")
                    print("Starting To Upload..")
                    response = await switch_upload(file_info['filename'],)
                    await app.send_video(DUMP_ID,file_name)
        except Exception as e:
            print("Failed To Download Episode", ep)
            print(">> Error: ", e)
            continue


app.run(StartDownload())
