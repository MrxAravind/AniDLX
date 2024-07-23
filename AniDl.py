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
from pyrogram.types import InputMediaPhoto, InputMediaVideo



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



async def progress(current, total,status,uploadedeps,start):
     current_time = time.time()
     diff = current_time - start
     if round(diff % 10.00) == 0 or current == total:
     #if round(current / total * 100, 0) % 5 == 0:
         per = f"{current * 100 / total:.1f}%"
         start_time = current_time
         text = f"{status.text}\nDownloaded Eps:{uploadedeps}\nStatus:Downloading\nUPProgress:{format_bytes(current)} / {format_bytes(total)} [{per}]"
         if status.text != text:
            await status.edit_text(text)


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



async def progress_callback(description, done, total,status,uploadedeps,start):
     current_time = time.time()
     diff = current_time - start
     if round(diff % 10.00) == 0:
        text = f"{status.text}\nDownloaded Eps:{uploadedeps}\nStatus:Downloading\nDLProgress:{format_bytes(done)} / {format_bytes(total)}"
        await status.edit_text(text)




def get_anime():
     with open("AnimeList.txt") as reader:
         animes = [i.strip() for i in reader.read().split("\n")]
     with open("AnimeList.txt","w+") as writer:
          for i in animes:
             if i != animes[0]:
                writer.write(f"{i}\n")
     return animes
    





    
async def StartDownload():
 async with app:
  while True:
    anime = get_anime()
    print(anime)
    if len(anime) == 0:
        await app.send_message(LOG_ID,"Ran out of Animes\nUpdate the List\nASAP")
        await asyncio.sleep(3800)
    anime = anime[0]
    status = await app.send_message(LOG_ID,"Bot Started")
    anime = TechZApi.gogo_anime(anime)["results"]
    title = anime.get("name")
    print(f"Selected Anime : {title}")
    status = await status.edit_text(f"{status.text}\nAnime : {title}")
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
            episode_list = [ [ i,data[i]] for i in data ]
            files = []
            for quality,url  in episode_list:
                 file_path = f"{anime.get('name')} - Episode {ep} - {quality}p.mp4"
                 print(f"\n\n>> Downloading Episode {ep} - {quality}p")
                 start = time.time()
                 downloader = TechZDL(
                              url=url,
                              debug=False,
                              filename=file_path,
                              progress=False,
                              progress_callback=progress_callback,
                              progress_args=(status,uploadedeps,start),
                              progress_interval=4,)
                 await downloader.start()
                 file_info = await downloader.get_file_info()
                 print(f"Filename: {file_info['filename']}")
                 if downloader.download_success:
                    print(f">> Episode {ep} - {quality}p Downloaded")
                    files.append(InputMediaDocument(media=f"downloads/{file_path}",thumb=f"downloads/{thumb_path}",caption=file_path))
                    #response = await switch_upload(file_path,) caption=f"[Direct Link]({response.media_link})",
                    #await app.send_document(DUMP_ID,,,progress=progress,progress_args=(status,uploadedeps,start_time))       
                 if len(files) == len(episodes):
                    print("Starting To Upload..")
                    await status.edit_text(f"{status.text}\nDownloaded Eps:{uploadedeps}\nStatus:Uploading")
                    await app.send_media_group(DUMP_ID,files)
                    await status.edit_text(f"{status.text}\nDownloaded Eps:{uploadedeps}\nStatus:Downloading")
                    print("Upload Finished...")
                    uploadedeps +=1
                    
        except Exception as e:
            print("Failed To Download Episode", ep)
            print(">> Error: ", e)
            await status.edit_text(f"{status.text}\nDownloaded Eps:{uploadedeps}\nStatus:Error")
            await status.delete()
            continue
    if len(episodes) == uploadedeps:
         await status.edit_text(f"{status.text}\nDownloaded Eps:{uploadedeps}\nStatus:Finished")
    await asyncio.sleep(120)


app.run(StartDownload())
