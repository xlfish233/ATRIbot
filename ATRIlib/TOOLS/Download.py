import aiohttp
import asyncio
from pathlib import Path
from PIL import Image
from io import BytesIO
import logging
import base64

logger = logging.getLogger(__name__)

beatmaps_path = Path('./data/beatmaps/')
beatmaps_path_tmp = Path('./data/beatmaps_tmp/')
avatar_path = Path('./data/avatar/')
cover_path = Path('./data/cover/')
medal_path = Path('./assets/medal/')
semaphore = asyncio.Semaphore(16)


# 下载ppy的资源(图片)
async def download_resource(session, url):
    """
    异步下载资源并保存到内存中，对图片进行压缩，跳过SVG文件
    """
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                content_type = response.headers.get('Content-Type', '')
                
                # 如果是SVG，直接返回None
                if content_type == 'image/svg+xml':
                    with open("./logs/svg.txt", "wb") as f:
                        f.write(await response.read())
                    return url, None
                
                content = await response.read()
                
                # 如果是其他类型的图片，进行压缩
                if content_type.startswith('image'):
                    img = Image.open(BytesIO(content))
                    img_io = BytesIO()
                    img.save(img_io, format='JPEG', quality=100, optimize=True)
                    content = img_io.getvalue()
                
                return url, content
    except Exception as e:
        logger.error(f"下载资源时出错: {url}, 错误: {str(e)}")
    return url, None
        
async def download_resource_async(resources_to_download):
    async with aiohttp.ClientSession() as session:
        tasks = [download_resource(session, url) for url, _, _ in resources_to_download]
        return await asyncio.gather(*tasks)


# 下载谱面
async def download_beatmap_file(session, beatmap_id, Temp=True):
    if Temp:
        file_path = beatmaps_path_tmp / f'{beatmap_id}.osu'
    else:
        file_path = beatmaps_path / f'{beatmap_id}.osu'
    url = f'https://osu.ppy.sh/osu/{beatmap_id}'
    async with semaphore:
        async with session.get(url) as response:
            if response.status == 200:  # 检查状态码是否为200
                with open(file_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)
            else:
                print(
                    f'Error: {response.status} {response.reason} - {url}')

# 下载头像
async def download_avatar_file(session, avatar_url, user_id):
    url = avatar_url
    async with semaphore:
        async with session.get(url) as response:
            if response.status == 200:  # 检查状态码是否为200
                avatar_file = avatar_path / f'{user_id}.jpeg'
                with open(avatar_file, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)
            else:
                print(
                    f'Error: {response.status} {response.reason} - {url}')

# 下载封面
async def download_cover(cover_url, beatmapset_id):
    url = cover_url
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:  # 检查状态码是否为200
                cover_file = cover_path / f'{beatmapset_id}.jpg'
                with open(cover_file, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)

# 下载奖牌
async def download_medal(session, medal_url, medalid):
    url = medal_url
    async with semaphore:
        async with session.get(url) as response:
            if response.status == 200:  # 检查状态码是否为200
                medal_file = medal_path / f'{medalid}.png'
                with open(medal_file, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)
            else:
                print(
                    f'Error: {response.status} {response.reason} - {url}')

# 批量下载谱面
async def download_osu_async(beatmap_ids, Temp=True):
    async with aiohttp.ClientSession() as session:
        tasks = [download_beatmap_file(session, beatmap_id, Temp)
                 for beatmap_id in beatmap_ids]
        await asyncio.gather(*tasks)

# 批量下载头像
async def download_avatar_async(avatar_urls, user_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [download_avatar_file(session, avatar_url, user_id)
                 for avatar_url, user_id in zip(avatar_urls, user_ids)]
        await asyncio.gather(*tasks)

# 批量下载奖章
async def download_medal_async(medal_urls, medal_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [download_medal(session, medal_url, medal_id)
                 for medal_url, medal_id in zip(medal_urls, medal_ids)]
        await asyncio.gather(*tasks)


# 获取单个谱面(ranked or unranked)
async def fetch_beatmap_file_async_one(beatmap_id, Temp=True):
    if Temp:
        filepath = beatmaps_path_tmp / f'{beatmap_id}.osu'
    else:
        filepath = beatmaps_path / f'{beatmap_id}.osu'
    if filepath.exists():
        return
    else:
        beatmap_ids = [beatmap_id]
    await download_osu_async(beatmap_ids, Temp=Temp)


# 批量获取谱面(ranked or unranked)
async def fetch_beatmap_file_async_all(beatmap_id_list, Temp=False):
    beatmap_ids = []
    for beatmap_id in beatmap_id_list:
        file_path = beatmaps_path / f'{beatmap_id}.osu'
        if file_path.exists():
            pass
        else:
            beatmap_ids.append(beatmap_id)

    await download_osu_async(beatmap_ids, Temp=Temp)
