import logging

from ATRIlib.bpsim import calculate_bpsim
from ATRIlib.joindate import calculate_joindate
from ATRIlib.avg import calculate_avg_pp,calculate_avg_pt,calculate_avg_tth
from ATRIlib.choke import calculate_choke_pp
from utils import get_userstruct_automatically,get_bpstruct
from ATRIlib.TOOLS.CommonTools import sort_dict_by_value
from ATRIlib.addpp import calculate_if_get_pp
from ATRIlib.score import calculate_pr_score,calculate_score,update_scores_to_db
from ATRIlib.pttpp import calculate_ptt_pp
from ATRIlib.tdba import calculate_tdba
from ATRIlib.tdba import calculate_tdba_sim

from ATRIlib.beatmapranking import calculate_beatmapranking,calculate_beatmapranking_update

from ATRIlib.myjobs import job_update_all_bind_user_info,job_compress_score_database,job_update_all_bind_user_bps
from ATRIlib.myjobs import job_update_all_user_info,job_update_all_user_bp

from ATRIlib.group import update_group_info

from ATRIlib.bind import update_bind_info

from ATRIlib.interbot import get_interbot_test1,get_interbot_test2

from ATRIlib.API.PPYapiv2 import get_token
from ATRIlib.whatif import calculate_pp,calculate_rank

from ATRIlib.medal import calculate_medal, download_all_medals, calculate_medal_pr

from ATRIlib.help import get_help

import traceback
import asyncio


def handle_exceptions(func):
    if asyncio.iscoroutinefunction(func):
        async def wrapper(*args, **kwargs):
            try:
                s_result = await func(*args, **kwargs)
                logging.info(f'[{func.__name__}]\n{s_result}')
                return s_result
            except Exception as e:
                error_message = f"An error occurred in {func.__name__}:\n"
                error_message += traceback.format_exc()
                logging.error(error_message)
                if type(e) == ValueError:
                    return str(e)
                else:
                    logging.error("Unexpected error")
                    return "发生了预期外的错误"
    else:
        def wrapper(*args, **kwargs):
            try:
                s_result = func(*args, **kwargs)
                logging.info(s_result)
                return s_result
            except Exception as e:
                error_message = f"An error occurred in {func.__name__}:\n"
                error_message += traceback.format_exc()
                logging.error(error_message)
                if type(e) == ValueError:
                    return str(e)
                else:
                    logging.error("Unexpected error")
                    return "发生了预期外的错误"
    return wrapper

@handle_exceptions
def format_help():

    raw = get_help()

    return raw

@handle_exceptions
def format_token():

    get_token()

    return 'success'

@handle_exceptions
async def format_test1(qq_id, osuname):
    userstruct = await get_userstruct_automatically(qq_id, osuname)
    username = userstruct["username"]

    raw = await get_interbot_test1(username)

    if "王者" in raw:
        raw = raw.replace("王者","老登")

    return raw


@handle_exceptions
async def format_test2(qq_id, osuname):
    userstruct = await get_userstruct_automatically(qq_id, osuname)
    username = userstruct["username"]

    raw = await get_interbot_test2(username)

    return raw

@handle_exceptions
async def format_bpsim(qq_id, osuname, pp_range):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    await get_bpstruct(user_id)

    raw = calculate_bpsim(user_id,pp_range)

    result_text = f'{raw[0]["user_data"]["username"]}与其他玩家的bp相似度\nPP段:+-{pp_range}pp'
    for i in raw[1:11]:
        result_text += f'\n{i["sim_count"]}张 --> {i["user_data"]["username"]}'

    return result_text

@handle_exceptions
async def format_joindate(qq_id, group_id, osuname, pp_range,group_member_list):

    if group_member_list:
        format_job_update_group_list(group_id,group_member_list)

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username= userstruct["username"]

    raw = calculate_joindate(user_id, group_id, pp_range)

    result_text1 = f'{username}的注册日期在本群\nPP段:+-{pp_range}pp\n'
    index = 0
    result_text2 = ''
    total_count = len(raw)
    user_rank = None

    for i in raw:
        if i["user_data"]["id"] == user_id:
            user_rank = index + 1
            break
        index += 1
    if user_rank is None:
        return f'没有在本群找到你哦'
    else:
        start_index = user_rank - 5
        end_index = user_rank +5
        if start_index < 0:
            start_index = 0
        for i in raw[start_index:end_index]:
            joindate_format = i["user_data"]["join_date"][:10] #截取时间格式
            result_text2 += f'\n{joindate_format} --> {i["user_data"]["username"]}'
            if user_id == i["user_data"]["id"]:
                result_text2 += f' <--你在这里 '

    result_text1 += f'你的排名是{user_rank}/{total_count}'

    result_text = result_text1 + result_text2

    return result_text

@handle_exceptions
async def format_avgpp(qq_id, osuname, pp_range):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    bpstruct = await get_bpstruct(user_id)

    raw = calculate_avg_pp(user_id, pp_range)

    count = round(raw[0]["count"])
    avgbp1 = round(raw[0]["avgbp1"])
    avgbp2 = round(raw[0]["avgbp2"])
    avgbp3 = round(raw[0]["avgbp3"])
    avgbp4 = round(raw[0]["avgbp4"])
    avgbp5 = round(raw[0]["avgbp5"])
    avgbp100 = round(raw[0]["avgbp100"])

    mypp = round(userstruct["statistics"]["pp"])
    mybp1 = round(bpstruct["bps_pp"][0])
    mybp2 = round(bpstruct["bps_pp"][1])
    mybp3 = round(bpstruct["bps_pp"][2])
    mybp4 = round(bpstruct["bps_pp"][3])
    mybp5 = round(bpstruct["bps_pp"][4])
    mybp100 = round(bpstruct["bps_pp"][99])

    diff_bp1 = round(mybp1 - avgbp1)
    diff_bp2 = round(mybp2 - avgbp2)
    diff_bp3 = round(mybp3 - avgbp3)
    diff_bp4 = round(mybp4 - avgbp4)
    diff_bp5 = round(mybp5 - avgbp5)
    diff_bp100 = round(mybp100 - avgbp100)

    diff_top5_total = diff_bp1 + diff_bp2 + diff_bp3 + diff_bp4 + diff_bp5

    result_text=f'根据亚托莉的数据库(#{count})\n{username}对比平均PP\nPP段:{mypp}(±{pp_range})pp'
    result_text += f'\nbp1:{mybp1}pp -- {avgbp1}pp({diff_bp1})'
    result_text += f'\nbp2:{mybp2}pp -- {avgbp2}pp({diff_bp2})'
    result_text += f'\nbp3:{mybp3}pp -- {avgbp3}pp({diff_bp3})'
    result_text += f'\nbp4:{mybp4}pp -- {avgbp4}pp({diff_bp4})'
    result_text += f'\nbp5:{mybp5}pp -- {avgbp5}pp({diff_bp5})'
    result_text += f'\nbp100:{mybp100}pp -- {avgbp100}pp({diff_bp100})'
    result_text += f'\n前bp5共偏差:{diff_top5_total}pp'

    return result_text

@handle_exceptions
async def format_avgpt(qq_id, osuname, pt_range):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    bpstruct = await get_bpstruct(user_id)

    raw = calculate_avg_pt(user_id, pt_range)

    pt_range = round(pt_range/60/60)

    count = round(raw[0]["count"])
    avgpp = round(raw[0]["avgpp"])
    avgbp1 = round(raw[0]["avgbp1"])
    avgbp2 = round(raw[0]["avgbp2"])
    avgbp3 = round(raw[0]["avgbp3"])
    avgbp4 = round(raw[0]["avgbp4"])
    avgbp5 = round(raw[0]["avgbp5"])
    avgbp100 = round(raw[0]["avgbp100"])

    mypt = round(userstruct["statistics"]["play_time"]/60/60)
    mypp = round(userstruct["statistics"]["pp"])
    mybp1 = round(bpstruct["bps_pp"][0])
    mybp2 = round(bpstruct["bps_pp"][1])
    mybp3 = round(bpstruct["bps_pp"][2])
    mybp4 = round(bpstruct["bps_pp"][3])
    mybp5 = round(bpstruct["bps_pp"][4])
    mybp100 = round(bpstruct["bps_pp"][99])

    diff_pp = round(mypp - avgpp)
    diff_bp1 = round(mybp1 - avgbp1)
    diff_bp2 = round(mybp2 - avgbp2)
    diff_bp3 = round(mybp3 - avgbp3)
    diff_bp4 = round(mybp4 - avgbp4)
    diff_bp5 = round(mybp5 - avgbp5)
    diff_bp100 = round(mybp100 - avgbp100)

    diff_top5_total = diff_bp1 + diff_bp2 + diff_bp3 + diff_bp4 + diff_bp5

    result_text = f'根据亚托莉的数据库(#{count})\n{username}对比平均游玩时间\nPT段:{mypt}(±{pt_range})h'
    result_text += f'\nPP:{mypp}pp -- {avgpp}pp({diff_pp})'
    result_text += f'\nbp1:{mybp1}pp -- {avgbp1}pp({diff_bp1})'
    result_text += f'\nbp2:{mybp2}pp -- {avgbp2}pp({diff_bp2})'
    result_text += f'\nbp3:{mybp3}pp -- {avgbp3}pp({diff_bp3})'
    result_text += f'\nbp4:{mybp4}pp -- {avgbp4}pp({diff_bp4})'
    result_text += f'\nbp5:{mybp5}pp -- {avgbp5}pp({diff_bp5})'
    result_text += f'\nbp100:{mybp100}pp -- {avgbp100}pp({diff_bp100})'
    result_text += f'\n前bp5共偏差:{diff_top5_total}pp'

    return result_text

@handle_exceptions
async def format_avgtth(qq_id, osuname, tth_range):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    bpstruct = await get_bpstruct(user_id)

    raw = calculate_avg_tth(user_id, tth_range)

    tth_range = round(tth_range/1000)

    count = round(raw[0]["count"])
    avgpp = round(raw[0]["avgpp"])
    avgbp1 = round(raw[0]["avgbp1"])
    avgbp2 = round(raw[0]["avgbp2"])
    avgbp3 = round(raw[0]["avgbp3"])
    avgbp4 = round(raw[0]["avgbp4"])
    avgbp5 = round(raw[0]["avgbp5"])
    avgbp100 = round(raw[0]["avgbp100"])

    mytth = round(userstruct["statistics"]["total_hits"] / 1000)
    mypp = round(userstruct["statistics"]["pp"])
    mybp1 = round(bpstruct["bps_pp"][0])
    mybp2 = round(bpstruct["bps_pp"][1])
    mybp3 = round(bpstruct["bps_pp"][2])
    mybp4 = round(bpstruct["bps_pp"][3])
    mybp5 = round(bpstruct["bps_pp"][4])
    mybp100 = round(bpstruct["bps_pp"][99])

    diff_pp = round(mypp - avgpp)
    diff_bp1 = round(mybp1 - avgbp1)
    diff_bp2 = round(mybp2 - avgbp2)
    diff_bp3 = round(mybp3 - avgbp3)
    diff_bp4 = round(mybp4 - avgbp4)
    diff_bp5 = round(mybp5 - avgbp5)
    diff_bp100 = round(mybp100 - avgbp100)

    diff_top5_total = diff_bp1 + diff_bp2 + diff_bp3 + diff_bp4 + diff_bp5

    result_text = f'根据亚托莉的数据库(#{count})\n{username}对比平均游玩时间\nTTH段:{mytth}(±{tth_range})w'
    result_text += f'\nPP:{mypp}pp -- {avgpp}pp({diff_pp})'
    result_text += f'\nbp1:{mybp1}pp -- {avgbp1}pp({diff_bp1})'
    result_text += f'\nbp2:{mybp2}pp -- {avgbp2}pp({diff_bp2})'
    result_text += f'\nbp3:{mybp3}pp -- {avgbp3}pp({diff_bp3})'
    result_text += f'\nbp4:{mybp4}pp -- {avgbp4}pp({diff_bp4})'
    result_text += f'\nbp5:{mybp5}pp -- {avgbp5}pp({diff_bp5})'
    result_text += f'\nbp100:{mybp100}pp -- {avgbp100}pp({diff_bp100})'
    result_text += f'\n前bp5共偏差:{diff_top5_total}pp'

    return result_text

@handle_exceptions
async def format_choke(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    await get_bpstruct(user_id)

    raw = await calculate_choke_pp(user_id)

    mypp = round(userstruct["statistics"]["pp"])
    weighted_fixed_result_total_pp = round(raw["weighted_fixed_result_total_pp"])
    total_lost_pp = round(raw["total_lost_pp"])
    total_lost_pp_plus = round(raw["total_lost_pp_plus"])

    result_text = f'{username}\'s ≤1miss choke'
    result_text += f'\n现在的pp:{mypp}pp({total_lost_pp})'
    result_text += f'\n如果不choke:{weighted_fixed_result_total_pp}pp'
    result_text += f'\n累加丢失的pp:{total_lost_pp_plus}pp\n'

    result_dict = sort_dict_by_value(raw["choke_dict"])

    count = 0
    for key,value in result_dict.items():
        result_text += f'bp{key + 1}:{round(value)}  '
        if (count+1) % 2 == 0:
            result_text += f'\n'
        count += 1

    return result_text

@handle_exceptions
async def format_addpp(qq_id, osuname,pp_lists):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    await get_bpstruct(user_id)

    raw = await calculate_if_get_pp(user_id,pp_lists)

    nowpp = round(raw["now_pp"],2)
    newpp = round(raw["new_pp_sum"],2)
    diff_pp = round(newpp - nowpp,2)

    diff_rank = int(raw["original_rank"]) - int(raw["new_rank"])

    result_text = f'{username}'
    result_text += f'\n现在的pp:{nowpp}pp'
    result_text += f'\n如果加入这些pp:{newpp}pp'
    result_text += f'\n增加了:{diff_pp}pp\n'
    result_text += f'\n变化前的排名:#{int(raw["original_rank"]):,}'
    result_text += f'\n变化后的排名:#{int(raw["new_rank"]):,}(↑{int(diff_rank):,})'

    return result_text

@handle_exceptions
async def format_pttpp(qq_id, osuname, pp_range):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]
    await get_bpstruct(user_id)

    raw = calculate_ptt_pp(user_id,pp_range)

    nowpp = round(raw['now_pp'],2)
    pttpp = round(raw['ptt_pp'],2)

    result_text = f'{username}\n'
    result_text += f'现在的pp:{nowpp}pp\n'
    result_text += f'预测的pp:{pttpp}pp'

    return result_text


@handle_exceptions
async def format_brk_up(beatmap_id,group_id):

    raw = await calculate_beatmapranking_update(beatmap_id,group_id)

    return raw


@handle_exceptions
async def format_brk(qq_id, osuname,beatmap_id,group_id,mods_list):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]

    await update_scores_to_db(user_id, beatmap_id)

    raw = await calculate_beatmapranking(user_id,beatmap_id,group_id,mods_list)

    return raw

@handle_exceptions
async def format_medal(medalid):

    # userstruct = await get_userstruct_automatically(qq_id, osuname)
    # user_id = userstruct["id"]
    raw = calculate_medal(medalid)

    return raw

@handle_exceptions
async def format_medal_pr(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    raw = await calculate_medal_pr(user_id)

    return raw

@handle_exceptions
async def format_download_medal():

    raw = await download_all_medals()

    return raw


@handle_exceptions
async def format_pr(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    raw = await calculate_pr_score(user_id)

    return raw

@handle_exceptions
async def format_tdba(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]

    await get_bpstruct(user_id)

    raw = calculate_tdba(user_id)

    return raw


@handle_exceptions
async def format_score(qq_id, osuname,beatmapid):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]

    raw = await calculate_score(user_id,beatmapid)

    return raw


@handle_exceptions
async def format_tdba_sim(qq_id, osuname):

    userstruct = await get_userstruct_automatically(qq_id, osuname)
    user_id = userstruct["id"]
    username = userstruct["username"]

    raw = calculate_tdba_sim(user_id)

    result_text = f'{username}的tdba相似度的相似度'

    for i in raw[:10]:
        similarity = round(i['cosineSimilarity'],2)
        result_text += f'\n{similarity} --> {i["user_data"]["username"]}'

    return result_text

@handle_exceptions
async def format_calculate_rank(pp):
    raw = await calculate_rank(pp)
    result_text = f'{pp}pp对应的排名为\n#{raw:,}'

    return result_text

@handle_exceptions
async def format_calculate_pp(rank):
    raw = await calculate_pp(rank)

    result_text = f'#{rank:,}对应的pp为\n{raw}pp'

    return result_text


@handle_exceptions
async def format_job_update_all_bind_users_info():

    raw = await job_update_all_bind_user_info()

    return raw

@handle_exceptions
async def format_job_update_all_users_info():

    raw = await job_update_all_user_info()

    return raw

@handle_exceptions
async def format_job_update_all_users_bp():

    raw = await job_update_all_user_bp()

    return raw



@handle_exceptions
async def format_job_update_all_bind_users_bp():

    raw = await job_update_all_bind_user_bps()

    return raw


@handle_exceptions
def format_job_compress_score_database():

    raw = job_compress_score_database()

    diff_time = raw['diff_time']
    count = raw['count']

    result_text = f'共清理{count}个重复成绩\n用时{diff_time}'

    return result_text


@handle_exceptions
def format_job_update_group_list(group_id,group_members_list):

    raw = update_group_info(group_id,group_members_list)

    return raw


@handle_exceptions
def format_bind(qq_id, osuname):

    raw = update_bind_info(qq_id,osuname)

    return raw






