from datetime import datetime
from multiprocessing.pool import worker

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.responses import FileResponse

from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from pydantic import BaseModel

from typing import Optional

from six import BytesIO

import ATRIproxy

import uvicorn

import logging


class IName(BaseModel):
    qq_id: int
    pp_range : Optional[int] = None
    osuname: Optional[str] = None
    pt_range: Optional[int] = None
    tth_range :Optional[int] = None
    pp_lists :Optional[list] = []
    users_id_list :Optional[list] = []
    beatmap_id : Optional[int] = None
    group_id : Optional[int] = None
    mods_list: Optional[list] = []
    group_member_list: Optional[list] = []


class ItemN(BaseModel):
    pp: Optional[int] = None
    rank: Optional[int] = None
    beatmap_id: Optional[int] = None
    group_id: Optional[int] = None
    group_member_list: Optional[list] = []
    medalid: Optional[int] = None

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    logging.info("亚托莉，启动!")
    scheduler.add_job(job_fetch_token,
                      trigger="interval", seconds=3600) #定时获取token
    scheduler.start()
    yield
    logging.info("亚托莉，关闭!")

app = FastAPI(lifespan=app_lifespan)


@app.api_route("/help", methods=["GET", "POST"])
async def fetch_help():
    img_bytes = ATRIproxy.format_help()
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)

@app.api_route("/qq/medal", methods=["GET", "POST"])
async def fetch_medal(item:ItemN):
    img_bytes = await ATRIproxy.format_medal(item.medalid)
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)

@app.api_route("/qq/medal/pr", methods=["GET", "POST"])
async def fetch_medal_pr(item:IName):
    img_bytes = await ATRIproxy.format_medal_pr(item.qq_id, item.osuname)
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)


@app.api_route("/qq/medal/download", methods=["GET", "POST"])
async def job_fetch_group_info():
    result = await ATRIproxy.format_download_medal()
    return str(result)

@app.api_route("/job/token", methods=["GET", "POST"])
def job_fetch_token():
    result = ATRIproxy.format_token()
    return str(result)

@app.api_route("/job/updategroup", methods=["GET", "POST"])
async def job_fetch_group_info(item:ItemN):
    result = await ATRIproxy.format_job_update_group_list(item.group_id, item.group_member_list)
    return str(result)

@app.api_route("/job/compress", methods=["GET", "POST"])
def job_compress_score_database():
    result = ATRIproxy.format_job_compress_score_database()
    return str(result)

@app.api_route("/job/update_info_all", methods=["GET", "POST"])
async def job_update_info_all():
    result = await ATRIproxy.format_job_update_all_users_info()
    return str(result)

@app.api_route("/job/update_bp_all", methods=["GET", "POST"])
async def job_update_info_all():
    result = await ATRIproxy.format_job_update_all_users_bp()
    return str(result)


@app.api_route("/job/update_info_bind", methods=["GET", "POST"])
async def job_update_info_all():
    result = await ATRIproxy.format_job_update_all_bind_users_info()
    return str(result)

@app.api_route("/job/update_bp_bind", methods=["GET", "POST"])
async def job_update_bp_all():
    result = await ATRIproxy.format_job_update_all_bind_users_bp()
    return str(result)

@app.api_route("/qq/test1", methods=["GET", "POST"])
async def fetch_test1(item:IName):
    result = await ATRIproxy.format_test1(item.qq_id,item.osuname)
    return str(result)

@app.api_route("/qq/test2", methods=["GET", "POST"])
async def fetch_test2(item:IName):
    result = await ATRIproxy.format_test2(item.qq_id,item.osuname)
    return str(result)

@app.api_route("/qq/bind", methods=["GET", "POST"])
async def fetch_bind(item:IName):
    result = await ATRIproxy.format_bind(item.qq_id,item.osuname)
    return str(result)

@app.api_route("/qq/brkup", methods=["GET", "POST"])
async def jobs(item:ItemN):
    result = await ATRIproxy.format_brk_up(item.beatmap_id,item.group_id)
    return str(result)

@app.api_route("/qq/brk", methods=["GET", "POST"])
async def jobs(item:IName):
    img_bytes = await ATRIproxy.format_brk(item.qq_id, item.osuname,item.beatmap_id,item.group_id,item.mods_list)
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)

@app.api_route("/qq/pr", methods=["GET", "POST"])
async def fetch_pr(item:IName):
    img_bytes = await ATRIproxy.format_pr(item.qq_id, item.osuname)
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)

@app.api_route("/qq/tdba", methods=["GET", "POST"])
async def fetch_tdba(item:IName):
    img_bytes = await ATRIproxy.format_tdba(item.qq_id, item.osuname)
    if type(img_bytes) is BytesIO:
        return StreamingResponse(img_bytes, media_type="image/jpeg")
    else:
        return str(img_bytes)

@app.api_route("/qq/tdbasim", methods=["GET", "POST"])
async def fetch_tdbasim(item:IName):
    result = await ATRIproxy.format_tdba_sim(item.qq_id, item.osuname)
    return str(result)

@app.api_route("/qq/pttpp", methods=["GET", "POST"])
async def fetch_pttpp(item:IName):
    result = await ATRIproxy.format_pttpp(item.qq_id, item.osuname,item.pp_range)
    return str(result)

@app.api_route("/qq/addpp", methods=["GET", "POST"])
async def fetch_addpp(item:IName):
    result = await ATRIproxy.format_addpp(item.qq_id, item.osuname,item.pp_lists)
    return str(result)

@app.api_route("/whatif_backrank", methods=["GET", "POST"])
async def fetch_rank(item:ItemN):
    result = await ATRIproxy.format_calculate_rank(item.pp)
    return str(result)

@app.api_route("/whatif_backpp", methods=["GET", "POST"])
async def fetch_pp(item:ItemN):
    result = await ATRIproxy.format_calculate_pp(item.rank)
    return str(result)

@app.api_route("/qq/choke", methods=["GET", "POST"])
async def fetch_choke(item:IName):
    result = await ATRIproxy.format_choke(item.qq_id, item.osuname)
    return str(result)

@app.api_route("/qq/bpsim", methods=["GET", "POST"])
async def fetch_bpsim(item:IName):
    result = await ATRIproxy.format_bpsim(item.qq_id, item.osuname, item.pp_range)
    return str(result)

@app.api_route("/qq/joindate", methods=["GET", "POST"])
async def fetch_joindate(item:IName):
    result = await ATRIproxy.format_joindate(item.qq_id,item.group_id, item.osuname, item.pp_range,item.group_member_list)
    return str(result)

@app.api_route("/qq/avgpp", methods=["GET", "POST"])
async def fetch_avgpp(item:IName):
    result = await ATRIproxy.format_avgpp(item.qq_id, item.osuname, item.pp_range)
    return str(result)

@app.api_route("/qq/avgpt", methods=["GET", "POST"])
async def fetch_avgpt(item:IName):
    result = await ATRIproxy.format_avgpt(item.qq_id, item.osuname, item.pt_range)
    return str(result)

@app.api_route("/qq/avgtth", methods=["GET", "POST"])
async def fetch_avgtth(item:IName):
    result = await ATRIproxy.format_avgtth(item.qq_id, item.osuname, item.tth_range)
    return str(result)


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8008,log_config="log_config.ini", reload=True, workers=4)
