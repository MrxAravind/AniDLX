from pyrogram import Client, filters,enums
import asyncio, aiohttp, os
import aria2p
from Utils.File import convertFilePath
from Utils.TechZApi import TechZApi
from Utils.Downloader import startDownload, get_status
from Utils.FFmpeg import ConvertTsToMp4

TechZApi = TechZApi()


app = Client(
    name="AniDLX-bot",
    api_hash=Config.API_HASH,
    api_id=int(Config.TELEGRAM_API),
    bot_token=Config.BOT_TOKEN,
    workers=300
)


os.system("nohup aria2c --enable-rpc --rpc-listen-all=true --rpc-allow-origin-all > aria2c.log 2>&1 &")

aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret=""
    )
)




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
            vid = startDownload(aria2,url[-1][-1])
            vstatus = get_status(aria2,vid.gid)
            file_name = vstatus['file_name']
            while True:
               if vstatus['is_complete']:
                        #os.system(f"ffmpeg -i {status['file_name']} ss.jpg") thumbnail if uploading to tg
                        print(f">> Episode {ep} - {quality}p Downloaded")
                        os.rename(file_name,f"{anime.get('name')} - Episode {ep} - {url[-1][0]}p.mp4")
                        await app.send_message(Config.DUMP_ID,file_name,thumb=thumbnail)
            
        except Exception as e:
            print("Failed To Download Episode", ep)
            print(">> Error: ", e)
            continue


app.run(StartDownload())
