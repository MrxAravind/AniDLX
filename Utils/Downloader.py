import os



def add_download(api, uri):
    download = api.add_uris([uri])
    return download

def get_status(api, gid):
    try:
        download = api.get_download(gid)
        total_length = download.total_length
        completed_length = download.completed_length
        download_speed = download.download_speed
        file_name = download.name
        progress = (completed_length / total_length) * 100 if total_length > 0 else 0
        is_complete = download.is_complete

        return {
            "gid": download.gid,
            "status": download.status,
            "file_name": file_name,
            "total_length": format_bytes(total_length),
            "completed_length": format_bytes(completed_length),
            "download_speed": format_bytes(download_speed),
            "progress": f"{progress:.2f}%",
            "is_complete": is_complete
        }
    except Exception as e:
        print(f"Failed to get status for GID {gid}: {e}")
        raise

def remove_download(api, gid):
    try:
        api.remove([gid])
        print(f"Successfully removed download: {gid}")
    except Exception as e:
        print(f"Failed to remove download: {e}")
        raise

def format_bytes(byte_count):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    index = 0
    while byte_count >= 1024 and index < len(suffixes) - 1:
        byte_count /= 1024
        index += 1
    return f"{byte_count:.2f} {suffixes[index]}"


def startDownload(aria2,url):
    print(">> Starting Download")
    vid = add_download(aria2,url)
    return vid
