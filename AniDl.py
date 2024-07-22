from pyrogram import Client, filters,enums
import asyncio, aiohttp, os
from Utils.File import convertFilePath
from Utils.TechZApi import TechZApi
from Utils.Downloader import startDownload, get_status
from Utils.FFmpeg import ConvertTsToMp4
from techzdl import TechZDL
from config import *
import static_ffmpeg
import time



# ffmpeg installed on first call to add_paths()
#static_ffmpeg.add_paths()  


TechZApi = TechZApi()


app = Client(
    name="AniDLX-bot",
    api_hash=API_HASH,
    api_id=int(API_ID),
    bot_token=BOT_TOKEN,
    workers=300
)

#Switch
#bot = BotApp(TOKEN)



def format_bytes(byte_count):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    index = 0
    while byte_count >= 1024 and index < len(suffixes) - 1:
        byte_count /= 1024
        index += 1
    return f"{byte_count:.2f} {suffixes[index]}"


def status_progress(start):
    global start_time
    current_time = time.time()
    elapsed_time = current_time - start
    if elapsed_time >= 4:
        start_time = current_time
    return True


async def progress(current, total,status,uploadedeps,start):
    per = f"{current * 100 / total:.1f}%"
    st = status_progress(start)
    if st:
          await status.edit_text(f"{status.text}\nDownloaded Eps:{uploadedeps}\nStatus:Downloading\nUPProgress:{format_bytes(current)} / {format_bytes(total)} [{per}]")
        
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
    
async def progress_callback(description, done, total,status,uploadedeps):
    await status.edit_text(f"{status.text}\nDownloaded Eps:{uploadedeps}\nStatus:Downloading\nDLProgress:{format_bytes(done)} / {format_bytes(total)}")


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
    status = await app.send_message(LOG_ID,"Bot Started")
    anime = get_anime()
    anime = TechZApi.gogo_anime(anime)["results"]
    title = anime.get("name")
    print(f"Selected Anime : {title}")
    status = await status.edit_text(f"{status.text}\n Anime : {title}")
    image_url = anime.get("image")
    episodes = anime["episodes"]
    print(f"Total No.OF Episodes: {len(episodes)}")
    status = await status.edit_text(f"{status.text}\nTotal Eps:{len(episodes)}")
    image_downloader = TechZDL(url=image_url,progress=False,debug=False)
    await image_downloader.start()
    img = await image_downloader.get_file_info()
    thumb_path = img['filename']
    uploadedeps = 0
    await status.edit_text(f"{status.text}\nStatus:Downloading")
    for ep in episodes:
        episode_id = ep[1]
        ep = ep[0]
        try:
            anime['name'] = anime['name'].replace("/", " ").replace("\\",' ')
            data = TechZApi.gogo_download(episode_id)["results"]
            url = [ [ i,data[i]] for i in data ]
            file_path = f"{anime.get('name')} - Episode {ep} - {url[-2][0]}p.mp4"
            print(f"\n\n>> Downloading Episode {ep} - {url[-2][0]}p")
            downloader = TechZDL(
                              url=url[-2][1],
                              debug=False,
                              filename=file_path,
                              progress=False,
                              progress_callback=progress_callback,
                              progress_args=(status,uploadedeps),
                              progress_interval=2,)
            await downloader.start()
            file_info = await downloader.get_file_info()
            print(f"Filename: {file_info['filename']}")
            if downloader.download_success:
                    print(f">> Episode {ep} - {url[-2][0]}p Downloaded")
                    print("Starting To Upload..")
                    start_time = time.time()
                    await status.edit_text(f"{status.text}\nDownloaded Eps:{uploadedeps}\nStatus:Uploading")
                    #response = await switch_upload(file_path,) caption=f"[Direct Link]({response.media_link})",
                    await app.send_document(DUMP_ID,f"downloads/{file_path}",thumb=f"downloads/{thumb_path}",progress=progress,progress_args=(status,uploadedeps,start_time))
            uploadedeps +=1
            await status.edit_text(f"{status.text}\nDownloaded Eps:{uploadedeps}\nStatus:Downloading")
        except Exception as e:
            print("Failed To Download Episode", ep)
            print(">> Error: ", e)
            await status.edit_text(f"{status.text}\nDownloaded Eps:{uploadedeps}\nStatus:Error")
            continue
    if len(episodes) == uploadedeps:
         await status.edit_text(f"{status.text}\nDownloaded Eps:{uploadedeps}\nStatus:Finished")
app.run(StartDownload())
