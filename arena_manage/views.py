# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Create your views here.
from django.shortcuts import render_to_response, render, redirect
from util.context import Context
from util.tool import Time
import time
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .models import *
import datetime
from util.gamedate import Arena_Info
import json
from xlwt import *
from io import BytesIO
from django.db.models import Sum
from django.http import JsonResponse
from hashlib import sha1
from login_manage.views import decorator

# Create your views here.


# ==========================竞技场总览==============================
@decorator
def arena_general(request):
    phone, number, room_type = request.session.get('uid'), 1, 1
    arena_type = Arena_Info.get_arena_type()
    hour_interval = Arena_Info.get_hour_interval()
    minute_interval = Arena_Info.get_minute_interval()
    quick = query_quick_game(request)  # 快速赛开关
    url_date = "/arena_manage/arena_general/"
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page:
            conf, arena_info = get_game_general(phone)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            arena_info.update({"number": number, "page": page})
        else:
            end_day = datetime.date.today().strftime('%Y-%m-%d')
            arena_info = {"start_day": end_day, "end_day": end_day, "number": number, "page": []}
    else:
        dic = request.POST
        start_time = dic.get("start_time").encode('utf-8')[:10]
        end_time = dic.get("stop_time").encode('utf-8')[:10]
        game = int(dic.get('games'))

        arena_info = {"start_day": start_time, "end_day": end_time, "game": game}
        keys = 'arena_general:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, arena_info)

        CelerityGeneral.objects.all().delete()  # 清除数据

        start_day = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_day = Time.str_to_datetime(end_time, '%Y-%m-%d')
        while start_day <= end_day:
            res = CelerityGeneral.objects.filter(day_time=start_day).first()

            cur_day = Time.datetime_to_str(start_day, '%Y-%m-%d')
            if res:
                if res.day_time == res.insert_time:
                    insert_general_info(phone, cur_day, cur_day, game)  # 插入数据
                else:
                    start_day = Time.next_days(start_day)
                    continue
            else:
                insert_general_info(phone, cur_day, cur_day, game)  # 插入数据

            start_day = Time.next_days(start_day)

        start_date = Time.str_to_datetime(start_time[:10], '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_time[:10], '%Y-%m-%d')

        res_info = CelerityGeneral.objects.filter(day_time__range=[start_date, end_date]).values('json_data').order_by("-day_time")
        sorted_info, serial = [], 1
        for date in res_info:
            data_info = json.loads(date.get("json_data"))
            data_info.update({"serial": serial})
            sorted_info.append(data_info)
            serial += 1
        paginator = Paginator(sorted_info, 30)
        page, plist = Context.paging(paginator, 1)
        arena_info.update({"page": page, "number": number})
    arena_info.update({"switch_open": quick["open"], "s1": str(quick["s1"]), "e1": str(quick["e1"]), "s2": str(quick["s2"]), "e2": str(quick["e2"]), "url_date": url_date, "arena_type": arena_type, "hour_interval": hour_interval, "minute_interval": minute_interval})
    return render(request, 'arena_manage/arena_general.html', arena_info)


# ==========================竞技场详情==============================
@decorator
def arena_details(request):
    phone, number, room_type = request.session.get('uid'), 1, 1
    arena_type = Arena_Info.get_arena_type()  # 竞技场类型
    url_date = "/arena_manage/arena_details/"
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page:
            conf, arena_info = get_arena_details(phone)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            arena_info.update({"number": number, "page": page})
        else:
            end_day = datetime.date.today().strftime('%Y-%m-%d')
            arena_info = {"start_day": end_day, "end_day": end_day, "number": number, "page": [], "uid": ""}
    else:
        dic = request.POST
        start_time = dic.get("start_time").encode('utf-8')[:10]
        end_time = dic.get("stop_time").encode('utf-8')[:10]
        game = int(dic.get('games'))
        uid = dic.get('uid').encode('utf-8')

        arena_info = {"start_day": start_time, "end_day": end_time, "game": game, "uid": uid}
        keys = 'arena_details:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, arena_info)

        CelerityDetails.objects.all().delete()  # 清除数据

        start_day = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_day = Time.str_to_datetime(end_time, '%Y-%m-%d')

        while start_day <= end_day:

            res = CelerityDetails.objects.filter(day_time=start_day).first()

            cur_day = Time.datetime_to_str(start_day, '%Y-%m-%d')
            if res:
                if res.day_time == res.insert_time:
                    insert_details_info(phone, cur_day, cur_day, game)  # 插入数据
                else:
                    start_day = Time.next_days(start_day)
                    continue
            else:
                insert_details_info(phone, cur_day, cur_day, game)  # 插入数据

            start_day = Time.next_days(start_day)

        start_date = Time.str_to_datetime(start_time[:10], '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_time[:10], '%Y-%m-%d')

        if uid != "":
            res_info = CelerityDetails.objects.filter(day_time__range=[start_date, end_date], user_uid__icontains=uid).values('json_data').order_by("-day_time")
        else:
            res_info = CelerityDetails.objects.filter(day_time__range=[start_date, end_date]).values('json_data').order_by("-day_time")

        arena_data, serial = [], 1
        serial = 1
        for date in res_info:
            data_info = json.loads(date.get("json_data"))
            data_info.update({"serial": serial})
            arena_data.append(data_info)
            serial += 1

        paginator = Paginator(arena_data, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        arena_info.update({"page": page, "number": number})
    arena_info.update({"url_date": url_date, "arena_type": arena_type})
    return render(request, 'arena_manage/arena_particulars.html', arena_info)


def insert_details_info(phone, start_time, end_time, games):
    """竞技场--详情"""
    url = '/v2/shell/query_match_data'
    context = {"start": start_time, "end": end_time, "type": games}
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.text)
    if "info" not in config:
        return 0
    else:
        details_list = []
        for info in config["info"]:
            play_info = Context.json_loads(info["md"])
            kick_time = play_info.get("times")
            if play_info.has_key("rw"):
                award_info = play_info.get("rw")
                del play_info['rw']
            else:
                award_info = 0
            del play_info['times']
            play_sort = sorted(play_info.items(), key=lambda x: x[1], reverse=True)
            play_data = []
            user_uid = []
            if isinstance(award_info, list):
                for index, data in enumerate(play_sort):
                    if index < len(award_info):
                        play_dict = {}
                        play_dict.update({"uid": data[0], "score": data[1], "award": award_info[index]["chip"]})
                        play_data.append(play_dict)
                        if data[0] not in user_uid:
                            user_uid.append(data[0])
                    else:
                        play_dict = {}
                        play_dict.update({"uid": data[0], "score": data[1], "award": 0})
                        play_data.append(play_dict)
                        if data[0] not in user_uid:
                            user_uid.append(data[0])
            else:
                for uid, score in play_sort:
                    play_dict = {}
                    play_dict.update({"uid": uid, "score": score, "award": 0})
                    play_data.append(play_dict)
                    if uid not in user_uid:
                        user_uid.append(uid)
            day_time = Time.timestamp_to_str(info["ts"])[:10]
            info.update({"kick_off_time": Time.timestamp_to_str(kick_time),"day_time":day_time,"play_data":play_data,"user_uid":user_uid})
            details_list.append(info)

        # sorted_info = sorted(game_list, key=lambda x: Time.str_to_timestamp(x["day_time"],'%Y-%m-%d'), reverse=True)
        # CelerityDetails.objects.all().delete()
        create_details_data(details_list, games)


def insert_general_info(phone, start_time, end_time, games):
    """竞技场--总览"""
    rake_info = Arena_Info.get_rake_info()  # 竞技场抽成
    url = '/v2/shell/query_match_all_data'
    context = {"start": start_time, "end": end_time}
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.text)
    if "ret" not in config:
        return 0
    else:
        general_list = []
        for gen in config["ret"]:
            general_data = {}
            for day, value in gen.items():
                kasai_time = int(value.get("match_primary_times")) + int(value.get("match_middle_times")) + int(value.get("match_high_times")) # 开赛次数
                chip_ticket = int(value.get("match_ticket_cost"))  # 鸟蛋门票 花费 - 邮件返回鸟蛋
                banker_yield = chip_ticket - int(value.get("match_reward"))  # 庄家收益 float(rake_info[0]["rake"])
                profit = float(banker_yield) / 5000  # 盈利额
                general_data.update(value)
                general_data.update({"day_time": str(day), "chip_ticket": chip_ticket, "banker_yield":int(banker_yield),"profit":profit,"kasai_time":kasai_time})
            general_list.append(general_data)

        # sorted_info = sorted(game_list, key=lambda x: Time.str_to_timestamp(x["day_time"],'%Y-%m-%d'), reverse=True)
        create_general_data(general_list, games)


def create_general_data(result, games):
    """竞技场总览--数据存储"""
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d')
    g_data = []
    g_type = "1"
    for m_info in result:
        day_time = m_info["day_time"]
        res = CelerityGeneral.objects.filter(day_time=day_time)
        if res:
            CelerityGeneral.objects.filter(day_time=day_time).update(
                day_time=day_time,
                insert_time=insert_time,
                games_type=g_type,
                json_data=json.dumps(m_info),
            )
        else:
            new_arena = CelerityGeneral(
                day_time=day_time,
                insert_time=insert_time,
                games_type=g_type,
                json_data=json.dumps(m_info),
            )
            g_data.append(new_arena)
    CelerityGeneral.objects.bulk_create(g_data)


def create_details_data(result, games):
    """竞技场详情--数据存储"""
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d')
    d_data = []
    for m_info in result:
        user_uid = m_info["user_uid"]
        day_time = m_info["day_time"]
        res = CelerityDetails.objects.filter(day_time=day_time)
        if res:
            CelerityDetails.objects.filter(day_time=day_time).update(
                user_uid=user_uid,
                day_time=day_time,
                insert_time=insert_time,
                games_type=m_info["type"],
                json_data=json.dumps(m_info),
            )
        else:
            new_arena = CelerityDetails(
                user_uid=user_uid,
                day_time=day_time,
                insert_time=insert_time,
                games_type=m_info["type"],
                json_data=json.dumps(m_info),
            )
            d_data.append(new_arena)

    CelerityDetails.objects.bulk_create(d_data)


def get_game_general(phone):
    """竞技场--总览"""

    keys = 'arena_general:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day", "game"])
    start_time, end_time, game = result[0], result[1], result[2]
    def_info = {"start_day": start_time, "end_day": end_time, "game": result[2]}

    start_date = Time.datetime_to_str(start_time, '%Y-%m-%d')
    end_date = Time.datetime_to_str(end_time, '%Y-%m-%d')

    res_info = CelerityGeneral.objects.filter(day_time__range=[start_date, end_date]).values('json_data').order_by("-day_time")
    sorted_info, serial = [], 1
    for date in res_info:
        data_info = json.loads(date.get("json_data"))
        data_info.update({"serial": serial})
        sorted_info.append(data_info)
        serial += 1
    return sorted_info, def_info


def get_arena_details(phone):
    """竞技场--详情"""
    keys = 'arena_details:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day", "game", "uid"])
    start_time, end_time, game, uid = result[0], result[1], result[2], result[3]
    def_info = {"start_day": start_time, "end_day": end_time, "game": result[2], "uid": result[3]}

    start_date = Time.datetime_to_str(start_time, '%Y-%m-%d')
    end_date = Time.datetime_to_str(end_time, '%Y-%m-%d')

    if uid != "":
        res_info = CelerityDetails.objects.filter(day_time__range=[start_date, end_date],user_uid__icontains=uid).values('json_data').order_by("-day_time")
    else:
        res_info = CelerityDetails.objects.filter(day_time__range=[start_date, end_date]).values('json_data').order_by("-day_time")

    sorted_info, serial = [], 1
    for date in res_info:
        data_info = json.loads(date.get("json_data"))
        data_info.update({"serial": serial})
        sorted_info.append(data_info)
        serial += 1
    return sorted_info, def_info


# ==========================快速赛开关==============================
@decorator
def alter_quick_game(request):
    """快速赛开关"""
    dic = request.POST
    open = int(dic.get("switch_open"))
    s1 = int(dic.get("start_hour_1"))
    e1 = int(dic.get("end_hour_1"))
    # start_minute_1 = int(dic.get("start_minute_1"))
    # end_minute_1 = int(dic.get("end_minute_1"))
    s2 = int(dic.get("start_hour_2"))
    e2 = int(dic.get("end_hour_2"))
    # start_minute_2 = int(dic.get("start_minute_2"))
    # end_minute_2 = int(dic.get("end_minute_2"))

    url = '/v2/game/config/update_match_config'
    context = {"pid": 2, "open": open, "s1": s1, "e1": e1, "s2": s2, "e2": e2}
    context.update({"phone": request.session.get('uid')})
    ret = Context.Controller.request(url, context)

    if ret.status_code == 200:
        info = "快速赛修改成功！"
        msg = True
    else:
        info = "快速赛修改失败！"
        msg = False
    return JsonResponse({'status': msg, 'info': info})


def query_quick_game(request):
    url = '/v2/game/config/update_match_config'
    context = {"pid": 1}
    context.update({"phone": request.session.get('uid')})
    ret = Context.Controller.request(url, context)
    game_info = Context.json_loads(ret.text)
    if not game_info.has_key("ret"):
        return 0
    else:
        return game_info["ret"]