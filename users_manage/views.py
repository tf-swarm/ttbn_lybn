# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.shortcuts import render
from django.core.paginator import Paginator
from login_manage.views import decorator
from util.context import Context
from login_manage.models import *
from control_manage.models import Account
from util.gamedate import *
from xlwt import *
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from data_process.day_player import Player
from util.tool import Time
from .models import *
from run_manage.models import *
from util.Tips_show import Tips
from util.process import *
import re

import copy
# Create your views here.


@decorator
def relax_overview(request):
    phone, number, room_type, room_list = request.session.get('uid'), 1, 1, ["301", "302", "303", "304", "305", "306", "307"]
    query_data, sort_data = Data_Info.get_query_data(), Data_Info.get_sort_info()
    filter_data = Data_Info.get_filter_info(1)
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info['1000']
    url_date = "/users_manage/relax_overview/"
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page:
            conf, play_info = get_player_info(phone, room_type)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            play_info.update({"number": number, "page": page, "online_users": len(conf)})
        else:
            day_time = datetime.date.today().strftime('%Y-%m-%d')
            play_info = {"channel": "0", "start_day": day_time, "end_day": day_time, "query_info": "online_player", "input_data": "", "number": number, "page": [], "online_users": 0}
    else:
        dic = request.POST
        channel = dic.get('channel').encode('utf-8')
        query_info = dic.get('query_info').encode('utf-8')
        start_time = dic.get("start_time").encode('utf-8')[:10]
        end_time = dic.get("stop_time").encode('utf-8')[:10]
        input_data = dic.get('input_data').encode('utf-8').strip()
        sort_field = dic.get('sort_field').encode('utf-8')
        sort_order = dic.get("sort_order").encode('utf-8')

        def_info = {"channel": channel, "query_info": query_info, "start_day": start_time,"end_day": end_time, "input_data": input_data,"sort_field": sort_field, "sort_order": sort_order}
        keys = 'relax_overview:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, def_info)
        play_info = get_server_data(phone, def_info, room_type, room_list)

    user_limit = Context.get_user_limit(phone)
    play_info.update({"user_limit": user_limit, "Data_info": query_data, "sort_data": sort_data,"filter_data": filter_data, "url_date": url_date, "chanel_info": chanel_info})
    return render(request, "users_manage/relax_overview.html", play_info)


@decorator
def power_overview(request):
    phone, number, room_type, room_list = request.session.get('uid'), 1, 2, ["400", "401", "402", "403"]
    query_data, sort_data = Data_Info.get_query_data(), Data_Info.get_sort_info()
    filter_data = Data_Info.get_filter_info(2)
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info['1000']
    url_date = "/users_manage/power_overview/"
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page:
            conf, play_info = get_player_info(phone, room_type)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            play_info.update({"number": number, "page": page, "online_users": len(conf)})
        else:
            day_time = datetime.date.today().strftime('%Y-%m-%d')
            play_info = {"channel": "0","start_day": day_time, "end_day": day_time, "query_info": "online_player", "input_data": "", "number": number, "page": [], "online_users": 0}
    else:
        dic = request.POST
        channel = dic.get('channel').encode('utf-8')
        query_info = dic.get('query_info').encode('utf-8')
        start_time = dic.get("start_time").encode('utf-8')[:10]
        end_time = dic.get("stop_time").encode('utf-8')[:10]
        input_data = dic.get('input_data').encode('utf-8').strip()
        sort_field = dic.get('sort_field').encode('utf-8')
        sort_order = dic.get("sort_order").encode('utf-8')

        def_info = {"channel": channel, "query_info": query_info, "start_day": start_time,"end_day": end_time, "input_data": input_data,"sort_field": sort_field, "sort_order": sort_order}
        keys = 'power_overview:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, def_info)
        play_info = get_server_data(phone, def_info, room_type, room_list)

    user_limit = Context.get_user_limit(phone)
    play_info.update({"user_limit": user_limit, "Data_info": query_data, "sort_data": sort_data,"filter_data": filter_data, "url_date": url_date, "chanel_info": chanel_info})
    return render(request, "users_manage/power_overview.html", play_info)


def get_server_data(phone, user_info, room_type, room_list):
    channel, start_time,end_time, query_info, input_data = user_info["channel"], user_info["start_day"], user_info["end_day"], user_info["query_info"], user_info["input_data"]
    channel, start_time, query_info, input_data = channel.encode('utf-8'), start_time.encode('utf-8'), query_info.encode('utf-8'), input_data.encode('utf-8')
    number,day_time = 1, Time.current_time('%Y-%m-%d')

    if query_info == "online_player" or query_info == "pay_player":
        context = {"query_info": query_info, "channel": channel}
    elif (query_info == "uid" or query_info == "nick" or query_info == "phone") and input_data != "":
        context = {"query_info": query_info, "input_data": input_data}
    elif (query_info == "uid" or query_info == "nick") and input_data != "" and (start_time == end_time):
        context = {"query_info": query_info, "input_data": input_data, "start": start_time, "end": end_time}
    else:
        context = {"query_info": query_info, "channel": channel, "start": start_time, "end": end_time}
    url = '/v2/shell/query_player_overview'
    context.update({"phone": phone, "room_list": room_list})
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.text)
    if "info" not in config:
        user_info.update({"number": number, "page": [], "online_users": 0})
        return user_info
    else:
        user_config = config["info"]
        if not user_config:
            user_info.update({"number": number, "page": [], "online_users": 0})
            return user_info
        else:
            sort_field, sort_order = user_info["sort_field"], user_info["sort_order"]
            deal_info = deal_user_info(user_config, phone, room_type)  # 处理数据并存储

            if sort_order == "1":  # 正序
                sorted_info = (get_sort_info(sort_order, deal_info, "all_pay_total") if sort_field == "all_pay_total" else get_sort_info(sort_order, deal_info, "day_pay_total") if sort_field == "day_pay_total" else get_sort_info(sort_order, deal_info, "day_in_warhead") if sort_field == "day_in_warhead" else get_sort_info(sort_order, deal_info, "day_in_power") if sort_field == "day_in_power" else get_sort_info(sort_order, deal_info, "day_in_silver_coupon") if sort_field == "day_in_silver_coupon" else get_sort_info(sort_order, deal_info, "uid"))
            else:
                sorted_info = (get_sort_info(sort_order, deal_info, "all_pay_total") if sort_field == "all_pay_total" else get_sort_info(sort_order, deal_info, "day_pay_total") if sort_field == "day_pay_total" else get_sort_info(sort_order, deal_info, "day_in_warhead") if sort_field == "day_in_warhead" else get_sort_info(sort_order, deal_info, "day_in_power") if sort_field == "day_in_power" else get_sort_info(sort_order, deal_info, "day_in_silver_coupon") if sort_field == "day_in_silver_coupon" else get_sort_info(sort_order, deal_info, "uid"))
            paginator = Paginator(sorted_info, 30)
            page, plist = Context.paging(paginator, 1)  # 翻页
            user_info.update({"number": number, "page": page, "online_users": len(user_config)})
            return user_info


def deal_user_info(play_info, phone, room_type):
    if room_type == 1:
        name = "relax_overview"
    else:
        name = "power_overview"
    ret = Context.RedisCache.hget_keys('{}:{}:*'.format(name, phone))
    if ret:
        for item in ret:
            uid = item.split(':')[2]
            del_key = "{}:{}:{}".format(name,phone, uid)
            Context.RedisCache.delete(del_key)

    for user in play_info:
        if len(user) > 1:
            result = data_processing(user, room_type)
            keys = "{}:{}:{}".format(name, phone, user["uid"])
            Context.RedisCache.hash_mset(keys, result)
        else:
            continue
    sort_info = []
    ret = Context.RedisCache.hget_keys('{}:{}:*'.format(name, phone))
    for item in ret:
        uid = item.split(':')[2]
        play_key = "{}:{}:{}".format(name, phone, uid)
        user_info = Context.RedisCache.hash_getall(play_key)
        if len(user_info) > 0:
            in_coin_pop = Context.json_loads(user_info["in_coin_pop"])
            user_info.update({"in_coin_pop": in_coin_pop, "coin_control": eval(user_info.get("coin_control", [])), "power_control": eval(user_info.get("power_control", [])), "freeze_user": int(user_info["freeze_user"])})
            sort_info.append(user_info)
        else:
            continue
    return sort_info


def get_sort_info(pid, deal_info, key):
    if pid == "1":
        sorted_info = sorted(deal_info, key=lambda x: int(x["{}".format(key)]), reverse=True)
    else:
        sorted_info = sorted(deal_info, key=lambda x: int(x["{}".format(key)]))
    return sorted_info


def data_processing(result, room_type):
    """数据处理"""
    # 总充值额度
    all_pay_total = int(result.get('pay_total', 0))

    if room_type == 1:
        day_in_silver = int(result.get('day_in_silver_coupon', 0))
        day_in_warhead = int(result.get('relax_day_in_props_701', 0)) + int(result.get('relax_day_in_props_702', 0)) + int(result.get('relax_day_in_props_703', 0)) + int(result.get('relax_day_in_props_704', 0))
        day_out_warhead = int(result.get('relax_day_out_props_701', 0)) + int(result.get('relax_day_out_props_702', 0)) + int(result.get('relax_day_out_props_703', 0)) + int(result.get('relax_day_out_props_704', 0))
        all_in_warhead = int(result.get('relax_in_props_701', 0)) + int(result.get('relax_in_props_702', 0)) + int(result.get('relax_in_props_703', 0)) + int(result.get('relax_in_props_704', 0))
        all_out_warhead = int(result.get('relax_out_props_701', 0)) + int(result.get('relax_out_props_702', 0)) + int(result.get('relax_out_props_703', 0)) + int(result.get('relax_out_props_704', 0))
        day_props_701_704 = int(result.get('props_701', 0)) + int(result.get('props_702', 0)) + int(result.get('props_703', 0)) + int(result.get('props_704', 0))

        result['day_in_warhead'], result['day_out_warhead'] = day_in_warhead, day_out_warhead
        result['all_in_warhead'], result['all_out_warhead'] = all_in_warhead, all_out_warhead
        result['day_props_701_704'], result['day_in_silver'] = day_props_701_704, day_in_silver
    else:
        result["dragon_egg"] = int(result.get('props_701', 0)) + int(result.get('props_702', 0)) + int(result.get('props_703', 0)) + int(result.get('props_704', 0))
        day_in_warhead = int(result.get('day_in_power', 0))
        result['day_in_warhead'] = day_in_warhead

    if all_pay_total > 0:
        # 鸟蛋场当日出奖率=(当前剩余能量+今日兑出能量)/(昨日剩余能量+ 当日兑入能量)
        power = int(result.get('power', 0))
        exchange_in_power = float(result.get("exchange_in_power", 0))
        if exchange_in_power == 0.0:
            result['power_award_rate'] = 1.0
        else:
            result['power_award_rate'] = round((power + float(result.get("exchange_out_power", 0))) / (exchange_in_power), 2)
        # 金币场当日出奖率=((当日产出毒龙蛋*1/2)+(冰龙蛋*10/2)+(火龙蛋*50/2)+(圣磷蛋*100/2) + 当日话费券产出/100)/当日充值
        in_701, in_702 = float(result.get("relax_in_props_701")) * 1 / 2, float(result.get("relax_in_props_702")) * 10 / 2
        in_703, in_704 = float(result.get("relax_in_props_703")) * 50 / 2, float(result.get("relax_in_props_704")) * 100 / 2
        silver_coupon = float(result['in_silver_coupon']) / 100
        result['relax_award_rate'] = round((in_701 + in_702 + in_703 + in_704 + silver_coupon) / all_pay_total, 2)
    else:
        result['relax_award_rate'] = 10.0
        result['power_award_rate'] = 1.0

    day_bird_in_power, wash_quantity = result.get("day_bird_in_power", 0), result.get("wash_quantity", 0)
    day_power_bonus_pool_raffle = result.get("day_power_bonus_pool_raffle", 0)
    result['power_yield'] = int(day_bird_in_power) + int(day_power_bonus_pool_raffle) - int(wash_quantity)
    # if day_out_power == 0:
    #     result['power_yield'] = 0
    # else:
    #     result['power_yield'] = result.get("day_in_power", 0) - day_out_power

    in_coin_info, day_in_coin = {}, 0
    for keys, values in result.items():
        # 金币场产出金币
        if keys.startswith('in.coin.') and not keys.startswith('in.coin.catch.bird.'):
            in_coin_info[keys] = int(in_coin_info.get(keys, 0)) + int(values)
            day_in_coin += int(values)

    in_coin_popup = Tips.get_in_coin_popup(in_coin_info, day_in_coin)
    result.update({"all_pay_total": all_pay_total, "day_in_coin": day_in_coin, "in_coin_pop": Context.json_dumps(in_coin_popup)})
    return result


def get_player_info(phone, room_type):
    if room_type == 1:
        name = "relax_overview"
    else:
        name = "power_overview"
    keys = '{}:{}:{}'.format(name, phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["channel", "query_info", "start_day","end_day", "input_data", "sort_field", "sort_order"]) #筛选条件
    sort_field, sort_order = result[5], result[6]
    def_info = {"channel": result[0], "query_info": result[1], "start_day": result[2], "end_day": result[3],"input_data": result[4], "sort_field": sort_field, "sort_order": sort_order}

    deal_info = []
    ret = Context.RedisCache.hget_keys('{}:{}:*'.format(name, phone))
    for item in ret:
        uid = item.split(':')[2]
        play_key = "{}:{}:{}".format(name, phone, uid)
        user_info = Context.RedisCache.hash_getall(play_key)
        if len(user_info) > 0:
            in_coin_pop = Context.json_loads(user_info["in_coin_pop"])
            user_info.update({"in_coin_pop": in_coin_pop, "coin_control": eval(user_info.get("coin_control", [])), "power_control": eval(user_info.get("power_control", [])), "freeze_user": int(user_info["freeze_user"])})
            deal_info.append(user_info)
        else:
            continue
    if sort_order == "1":  # 正序
        sorted_info = (get_sort_info(sort_order, deal_info, "all_pay_total") if sort_field == "all_pay_total" else get_sort_info(sort_order, deal_info, "day_pay_total") if sort_field == "day_pay_total" else get_sort_info(sort_order, deal_info, "day_in_warhead") if sort_field == "day_in_warhead" else get_sort_info(sort_order, deal_info, "day_in_power") if sort_field == "day_in_power" else get_sort_info(sort_order, deal_info, "day_in_silver_coupon") if sort_field == "day_in_silver_coupon" else get_sort_info(sort_order, deal_info, "uid"))
    else:
        sorted_info = (get_sort_info(sort_order, deal_info, "all_pay_total") if sort_field == "all_pay_total" else get_sort_info(sort_order, deal_info, "day_pay_total") if sort_field == "day_pay_total" else get_sort_info(sort_order, deal_info, "day_in_warhead") if sort_field == "day_in_warhead" else get_sort_info(sort_order, deal_info, "day_in_power") if sort_field == "day_in_power" else get_sort_info(sort_order, deal_info, "day_in_silver_coupon") if sort_field == "day_in_silver_coupon" else get_sort_info(sort_order, deal_info, "uid"))
    return sorted_info, def_info


@decorator
def user_period_data(request):
    """(新)玩家期间数据"""
    phone, index, number = request.session.get('uid'), 1, 1
    player_period = Data_Info.get_player_period()
    url_date = "/users_manage/user_period_data/"
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page:
            conf, day_info = get_user_period(phone)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            day_info.update({"number": number, "page": page})
        else:
            day_time = datetime.date.today().strftime('%Y-%m-%d')
            before_time = Time.datetime_to_str(Time.str_to_datetime(day_time, '%Y-%m-%d') + datetime.timedelta(days=-1))[:10]
            day_info = {"start_day": before_time, "end_day": before_time, "number": number, "page": [], "input_data": "", "period": "money"}
    else:
        dic = request.POST
        query_info = dic.get("query_info", 0).encode('utf-8')
        input_data = dic.get("input_data", 0).encode('utf-8').strip()
        start_time = dic.get("start_time")[:10]
        end_time = dic.get("stop_time")[:10]

        sort_info, play_data = [], []
        day_info = {"start_day": start_time, "end_day": end_time, "query_info": query_info, "input_data": input_data}
        keys = 'player_period:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, day_info)

        g_list = insert_period_data(phone, start_time, end_time, query_info, input_data)  # 插入数据
        PeriodData.objects.all().delete()
        for info in g_list:
            if query_info == "uid":
                sort_info.append(info)
            else:
                if info["pay_total"] >= int(input_data):
                    sort_info.append(info)
                else:
                    continue
            new_player = PeriodData(
                uid=info["uid"],
                json_data=Context.json_dumps(info),
            )
            play_data.append(new_player)

            if len(play_data) > 1000:
                PeriodData.objects.bulk_create(play_data)
                play_data = []

        PeriodData.objects.bulk_create(play_data)
        paginator = Paginator(sort_info, 30)
        page, plist = Context.paging(paginator, 1)
        day_info.update({'page': page, "url_date": url_date, "number": number, "player_period": player_period})
    day_info.update({"player_period": player_period, "url_date": url_date})
    return render(request, 'users_manage/user_period_data.html', day_info)


def insert_period_data(phone, start_day, end_day, query_info, input_data):
    url = '/v2/shell/gm/query/player_days_period'
    if query_info == "uid":
        context = {"start": start_day, "end": end_day, "uid": input_data}
    else:
        context = {"start": start_day, "end": end_day}
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    ret_dict = Context.json_loads(ret.text)
    if "info" not in ret_dict:
        user_list = []
    else:
        result = ret_dict["info"]
        user_list = deal_period_data(result)
    return user_list


def deal_period_data(result):
    user_list = []
    for day_time, user_info in result.items():
        for uid, user_data in user_info.items():
            user_data.update({"uid": uid, "day_time": day_time})
            deal_user = Player.deal_user_info(user_data)
            user_list.append(deal_user)
    return user_list


def get_user_period(phone):
    """翻页"""
    keys = 'player_period:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day", "query_info", "input_data"])  # 筛选条件
    start_time, end_time, query_info, input_data = result[0], result[1], result[2], result[3]

    def_time = {"start_day": start_time, "end_day": end_time, "query_info": query_info, "input_data":input_data}
    conf_info = []
    res_info = PeriodData.objects.all().values("json_data")
    for data in res_info:
        conf_info.append(Context.json_loads(data.get("json_data")))
    return conf_info, def_time


@decorator
def user_control_deal(request):
    phone = request.session.get('uid')
    dic = request.POST
    pid = int(dic.get('pid'))
    user_id = dic.get('user_id')
    if pid == 1:  # 封冻
        url = '/v1/shell/gm/account/freeze'
        freeze_day = int(dic.get('freezing_day'))
        if freeze_day == 0:
            context = {'userId': user_id}
            freeze = "解封"
            day_time = 0
        else:
            freeze = "封冻"
            day_time = Time.current_ts() + freeze_day * 3600 * 24
            context = {'userId': user_id, 'days': freeze_day}
        context.update({"phone": phone})
        ret = Context.Controller.request(url, context)
        conf = Context.json_loads(ret.content)
        if not conf or "end_ts" in conf:
            keys = "freeze_user:{}:{}".format(phone, user_id)
            Context.RedisCache.hash_set(keys, "freeze_user", day_time)
            info = "{}成功！".format(freeze)
            msg = True
        else:
            info = "{}失败！".format(freeze)
            msg = False
        return JsonResponse({'code': msg, 'info': info, "frozen": freeze_day, "uid": user_id})
    else:  # 修改昵称
        url = '/v2/shell/gm/player/alter_nick'
        user_nick = int(dic.get('user_nick'))
        if user_nick == 0:
            new_nick = "游客{}".format(user_id)
            context = {'userId': user_id}
        else:
            new_nick = dic.get('new_nick').encode('utf-8')
            context = {'userId': user_id, 'nick': new_nick}
        context.update({"phone": phone})
        ret = Context.Controller.request(url, context)
        conf = Context.json_loads(ret.content)
        if not conf:
            info = "修改成功！"
            msg = True
        else:
            info = "修改失败！"
            msg = False
        return JsonResponse({'status': msg, 'msg': info, "uid": user_id, "nick": new_nick})


@decorator
def barrel_control(request):
    """炮倍控制"""
    phone = request.session.get('uid')
    url = '/v2/shell/gm/control_power_pool'
    dic = request.POST
    pid = int(dic.get('pid'))
    room_type = int(dic.get('room_type'))  # 金币场 2  鸟蛋场 1
    user_id = int(dic.get('uid'))
    print("--------room_type", room_type)
    if pid == 1:  # 查询
        context = {'phone': phone, 'pid': pid, 't': 2, 'uid': user_id}
        ret = Context.Controller.request(url, context)
        result = Context.json_loads(ret.content)
        print("--------query--------result", result)
        if "info" not in result or "value" not in result:
            control, status, show = [], False, "服务器数据异常!"
        else:
            if result["info"]:
                control, index = [], 1
                for info in result["info"]:
                    room = int(info["room_type"])
                    if room_type == room:
                        deal_info = copy.deepcopy(info)
                        deal_info.update({"index": index})
                        control.append(deal_info)
                    else:
                        continue
            else:
                control = []
            status, show = True, ""
        print("--------control", control)
        return JsonResponse({'status': status, 'show': show, "control": control})
    elif pid == 2:  # 修改
        room = ("鸟蛋场" if room_type == 1 else "金币场")
        barrel_list = []
        start_list, end_list = dic.getlist("start_barrel"), dic.getlist("end_barrel")
        rate_list, kill_list = dic.getlist("rate"), dic.getlist("kill")
        total_list, point_list = dic.getlist("total"), dic.getlist("point")
        for start, end in zip(start_list, end_list):
            start, end = start.encode('utf-8'), end.encode('utf-8')
            if start == "" or end == "":
                status = False
                msg = "请输入{}炮倍区间!".format(room)
                return JsonResponse({"status": status, "info": msg})
            else:
                barrel_list.append([start, end])
        all_control = []
        for barrel, rate, kill, total, point in zip(barrel_list, rate_list, kill_list, total_list, point_list):
            control = {}
            rate, kill, total, point = rate.encode('utf-8'), kill.encode('utf-8'), total.encode('utf-8'), point.encode('utf-8')
            if rate == "" or kill == "" or total == "" or point == "":
                status = False
                msg = "请输入抽/送分的比率或控制概率纠正或抽/送分的额度或击杀鸟概率!"
                return JsonResponse({"status": status, "info": msg})
            else:
                rate, kill, total, point = float(rate), float(kill), int(float(total)), int(float(point))
                barrel_info = [int(barrel[0]), int(barrel[1])]
                control.update({"room_type": room_type, "area": barrel_info, "rate": rate, "kill": kill, "total": total,"point": point})
                all_control.append(control)
        context = {'phone': phone, 'pid': pid, 't': 2, 'uid': user_id, 'ac': all_control}  # t:1 全服 2 个人
        print("--------alter--------context", context)
        ret = Context.Controller.request(url, context)
        result = Context.json_loads(ret.content)
        if "t" in result:
            status = True
            msg = "{}炮倍池设置成功!".format(room)
        else:
            status = False
            msg = "{}炮倍池设置失败!".format(room)
        return JsonResponse({"status": status, "info": msg})
    else:  # 删除
        barrel_info = dic.get("barrel_list").encode("utf-8").split(",", 1)
        context = {'phone': phone, 'pid': pid, 't': 2, 'uid': user_id, 'area1': int(barrel_info[0]), 'area2': int(barrel_info[1]),"room_type": 2}  # t:1 全服 2 个人
        print("--------delete--------context", context)
        ret = Context.Controller.request(url, context)
        result = Context.json_loads(ret.content)
        if "t" in result:
            status = True
            msg = "{}-{}倍删除成功!".format(barrel_info[0], barrel_info[1])
        else:
            status = False
            msg = "{}-{}倍删除失败!".format(barrel_info[0], barrel_info[1])
        return JsonResponse({"status": status, "info": msg})


@decorator
def user_give_info(request):
    url_date, number, phone = "/users_manage/user_give/", 1, request.session.get('uid')
    if request.method == 'GET':
        one_pages = request.GET.get('page')
        if one_pages:
            config, give_info = get_give_info(phone)
            pages = int(one_pages.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(config, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            give_info.update({"page": page, "number": number})

        else:
            day_time = datetime.date.today().strftime('%Y-%m-%d')
            give_info = {"start_day": day_time, "end_day": day_time,"page": [], "number": number, "uid":""}
    else:
        dic = request.POST
        start_time = dic.get('start_time').encode('utf-8')[:10]
        end_time = dic.get('stop_time').encode('utf-8')[:10]
        user_id = dic.get('uid').encode('utf-8')

        give_info = {"start_day": start_time, "end_day": end_time, "uid": user_id}
        keys = 'user_present:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, give_info)

        start_day = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_day = Time.str_to_datetime(end_time, '%Y-%m-%d')

        while start_day <= end_day:
            res = PresentData.objects.filter(day_time=start_day).first()
            cur_day = Time.datetime_to_str(start_day, '%Y-%m-%d')
            if res:
                if res.day_time == res.insert_time:
                    insert_present_info(phone, cur_day, cur_day, user_id)  # 插入数据
                else:
                    start_day = Time.next_days(start_day)
                    continue
            else:
                insert_present_info(phone, cur_day, cur_day, user_id)  # 插入数据
            start_day = Time.next_days(start_day)

        start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')
        if user_id == "":
            res_info = PresentData.objects.filter(day_time__range=[start_date, end_date]).values('json_data').order_by("-day_time")
        else:
            res_info = PresentData.objects.filter(day_time__range=[start_date, end_date], uid=user_id).values('json_data').order_by("-day_time")
        sort_info = []
        for info in res_info:
            sort_info.append(Context.json_loads(info.get("json_data")))
        paginator = Paginator(sort_info, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        give_info.update({"page": page, "number": number})

    give_info.update({"url_date": url_date})
    return render(request, 'users_manage/user_give.html',give_info)


def insert_present_info(phone,start_time,end_time,uid):
    url = '/v2/shell/gm/query/user_give_info'
    start_day, end_day = start_time + " 00:00:00",end_time + " 23:59:59"
    if uid == "":
        context = {"start": start_day, "end": end_day}
    else:
        context = {"start": start_day, "end": end_day, "uid": uid}
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.text)
    if "info" not in config:
        return 0
    else:
        give_info, give_list = {}, []
        give_data = config["info"]
        for info in give_data:
            for key,value in info.items():
                day_time = Time.timestamp_to_str(int(key))[:10]
                user_id = str(value["oneself_uid"])
                if not give_info.has_key(day_time):
                    give_info[day_time] = {}
                if not give_info[day_time].has_key(user_id):
                    give_info[day_time][user_id] = {}
                give_info[day_time][user_id]["day_count"] = int(give_info[day_time][user_id].get("day_count", 0)) + 1
                give_list.append(value)

        present_list = []
        for user_info in give_list:
            day = user_info["give_time"][:10]
            user_id = str(user_info["oneself_uid"])
            day_count = int(give_info[day][user_id]["day_count"])
            user_info.update({"day_count": day_count})
            present_list.append(user_info)

        create_present_info(present_list)


def create_present_info(pay_list):
    # PresentData.objects.all().delete()
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d')
    give_data = []
    for m_info in pay_list:
        day_time, channel, user_id, sole_id = m_info["give_time"][:10], m_info["channel"], m_info["oneself_uid"], m_info["sole_id"]
        res = PresentData.objects.filter(sole_id=sole_id, uid=user_id).first()
        if res:
            PresentData.objects.filter(sole_id=sole_id, uid=user_id).update(
                sole_id=sole_id,
                day_time=day_time,
                insert_time=insert_time,
                uid=user_id,
                channel=channel,
                json_data=Context.json_dumps(m_info)
            )
        else:
            new_give = PresentData(
                sole_id=sole_id,
                day_time=day_time,
                insert_time=insert_time,
                uid=user_id,
                channel=channel,
                json_data=Context.json_dumps(m_info)
            )
            give_data.append(new_give)

        if len(give_data) > 1000:
            PresentData.objects.bulk_create(give_data)
            give_data = []

    PresentData.objects.bulk_create(give_data)


def get_give_info(phone):
    keys = 'user_present:{}:{}'.format(phone,'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day","uid"])
    start_day, end_day, user_id = result[0], result[1], result[2]
    def_info = {"start_day": start_day, "end_day": end_day, "uid": user_id}
    start_date = Time.str_to_datetime(start_day, '%Y-%m-%d')
    end_date = Time.str_to_datetime(end_day, '%Y-%m-%d')
    if user_id == "":
        res_info = PresentData.objects.filter(day_time__range=[start_date, end_date]).values('json_data').order_by("-day_time")
    else:
        res_info = PresentData.objects.filter(day_time__range=[start_date, end_date], uid=user_id).values('json_data').order_by("-day_time")
    sort_info = []
    for info in res_info:
        sort_info.append(Context.json_loads(info.get("json_data")))
    return sort_info, def_info


@decorator
def user_strong_box(request):
    """保险箱"""
    url_date, number, phone = "/users_manage/strong_box/", 1, request.session.get('uid')
    access_list = Data_Info.get_strong_box()
    if request.method == 'GET':
        one_pages = request.GET.get('page')
        if one_pages:
            config, strong_info = get_strong_box_info(phone)
            pages = int(one_pages.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(config, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            strong_info.update({"page": page, "number": number})

        else:
            day_time = datetime.date.today().strftime('%Y-%m-%d')
            strong_info = {"start_day": day_time, "end_day": day_time,"page": [], "number": number, "uid":"", "access_status":"1"}
    else:
        dic = request.POST
        start_time = dic.get('start_time').encode('utf-8')[:10]
        end_time = dic.get('stop_time').encode('utf-8')[:10]
        box_status = dic.get('box_status').encode('utf-8')
        user_id = dic.get('uid').encode('utf-8')

        strong_info = {"start_day": start_time, "end_day": end_time, "access_status": box_status, "uid": user_id}
        keys = 'user_strong_box:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, strong_info)

        start_day = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_day = Time.str_to_datetime(end_time, '%Y-%m-%d')

        while start_day <= end_day:
            res = StrongBox.objects.filter(day_time=start_day, box_status=box_status).first()
            cur_day = Time.datetime_to_str(start_day, '%Y-%m-%d')
            if res:
                if res.day_time == res.insert_time:
                    insert_strong_box(phone, cur_day, cur_day, box_status, user_id)  # 插入数据
                else:
                    start_day = Time.next_days(start_day)
                    continue
            else:
                insert_strong_box(phone, cur_day, cur_day, box_status, user_id)  # 插入数据
            start_day = Time.next_days(start_day)

        start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')
        if user_id == "":
            res_info = StrongBox.objects.filter(day_time__range=[start_date, end_date], box_status=box_status).values('json_data').order_by("-day_time")
        else:
            if box_status == "1":
                res_info = StrongBox.objects.filter(day_time__range=[start_date, end_date], box_status=box_status, uid=user_id).values('json_data').order_by("-day_time")
            else:
                res_info = StrongBox.objects.filter(day_time__range=[start_date, end_date], box_status=box_status, get_user=user_id).values('json_data').order_by("-day_time")

        sort_info = []
        for info in res_info:
            sort_info.append(Context.json_loads(info.get("json_data")))
        paginator = Paginator(sort_info, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        strong_info.update({"page": page, "number": number})

    strong_info.update({"url_date": url_date, "access_list": access_list})
    return render(request, 'users_manage/user_strong_box.html',strong_info)


def insert_strong_box(phone, start_time, end_time, status, uid):
    url = '/v2/shell/gm/query/user_strong_box'
    start_day, end_day = start_time + " 00:00:00", end_time + " 23:59:59"
    box_status = int(status)
    # if uid == "":
    #     context = {"start": start_day, "end": end_day, "status": box_status}
    # else:
    #     context = {"start": start_day, "end": end_day, "status": box_status, "uid": uid}
    context = {"start": start_day, "end": end_day, "status": box_status}
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.text)
    if "ret" not in config:
        return 0
    else:
        box_list = []
        box_config = config["ret"]
        # print("-------box_config", box_config)
        for box_info in box_config:
            for key,value in box_info.items():
                value.update({"box_status":str(status)})
                box_list.append(value)
        create_strong_box_info(box_list)


def create_strong_box_info(box_list):
    # StrongBox.objects.all().delete()
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d')
    box_data = []
    for m_info in box_list:
        day_time, channel, user_id, sole_id, box_status = m_info["day_time"][:10], m_info["channel"], m_info["oneself_uid"], m_info["sole_id"], str(m_info["box_status"])
        get_user = (m_info["get_user"] if box_status == "2" else "")

        res = StrongBox.objects.filter(sole_id=sole_id, uid=user_id).first()
        if res:
            StrongBox.objects.filter(sole_id=sole_id, uid=user_id).update(
                sole_id=sole_id,
                day_time=day_time,
                insert_time=insert_time,
                box_status=box_status,
                uid=user_id,
                get_user=get_user,
                channel=channel,
                json_data=Context.json_dumps(m_info)
            )
        else:
            new_give = StrongBox(
                sole_id=sole_id,
                day_time=day_time,
                insert_time=insert_time,
                uid=user_id,
                get_user=get_user,
                box_status=box_status,
                channel=channel,
                json_data=Context.json_dumps(m_info)
            )
            box_data.append(new_give)

        if len(box_data) > 1000:
            StrongBox.objects.bulk_create(box_data)
            box_data = []

    StrongBox.objects.bulk_create(box_data)


def get_strong_box_info(phone):
    keys = 'user_strong_box:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day", "access_status", "uid"])
    start_day, end_day, box_status, user_id = result[0], result[1], result[2], result[3]
    def_info = {"start_day": start_day, "end_day": end_day,"access_status": box_status, "uid": user_id}
    start_date = Time.str_to_datetime(start_day, '%Y-%m-%d')
    end_date = Time.str_to_datetime(end_day, '%Y-%m-%d')
    if user_id == "":
        res_info = StrongBox.objects.filter(day_time__range=[start_date, end_date], box_status=box_status).values('json_data').order_by("-day_time")
    else:
        res_info = StrongBox.objects.filter(day_time__range=[start_date, end_date], box_status=box_status, uid=user_id).values('json_data').order_by("-day_time")
    sort_info = []
    for info in res_info:
        sort_info.append(Context.json_loads(info.get("json_data")))
    return sort_info, def_info


@decorator
def championship_info(request):
    """ 魂王争霸赛"""
    url_date, number, phone = "/users_manage/championship/", 1, request.session.get('uid')
    everyday_list = Data_Info.get_power_championship()
    res_for = EarlyWarning.objects.filter(user_status=3).values("user_list", "user_length").first()
    if res_for:
        f_list = Context.json_loads(res_for.get("user_list", []))
    else:
        f_list = ["1000000"]

    url = "/v2/shell/gm/query/user_power_rank"
    context = {"pid": 4, "phone": phone}
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.text)
    if "ret" in config and config["ret"] == 0:
        rank_switch = int(config["ret"])
    else:
        rank_switch = 1

    if request.method == 'GET':
        one_pages = request.GET.get('page')
        if one_pages:
            config, power_rank = get_give_info(phone)
            pages = int(one_pages.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(config, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            power_rank.update({"page": page, "number": number})

        else:
            day_time = datetime.date.today().strftime('%Y-%m-%d')
            power_rank = {"start_day": day_time, "end_day": day_time, "page": [], "number": number,"point_time": "1", "uid": ""}
    else:
        dic = request.POST
        start_time = dic.get('start_time').encode('utf-8')[:10]
        end_time = dic.get('stop_time').encode('utf-8')[:10]
        status = dic.get('point_time').encode('utf-8')
        user_id = dic.get('uid').encode('utf-8')

        power_rank = {"start_day": start_time, "end_day": end_time, "status": status, "uid": user_id}
        keys = 'user_power_rank:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, power_rank)

        start_day = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_day = Time.str_to_datetime(end_time, '%Y-%m-%d')

        while start_day <= end_day:
            res = PowerRank.objects.filter(day_time=start_day, point_status=status).first()
            cur_day = Time.datetime_to_str(start_day, '%Y-%m-%d')
            if res:
                if res.day_time == res.insert_time:
                    insert_championship(phone, cur_day, cur_day, power_rank)
                else:
                    start_day = Time.next_days(start_day)
                    continue
            else:
                insert_championship(phone, cur_day, cur_day, power_rank)
            start_day = Time.next_days(start_day)

        start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')

        if user_id == "":
            res_info = PowerRank.objects.filter(day_time__range=[start_date, end_date], point_status=status).values('json_data').order_by("-day_time")
        else:
            res_info = PowerRank.objects.filter(day_time__range=[start_date, end_date], point_status=status, uid=user_id).values('json_data').order_by("-day_time")

        rank_list = []
        for info in res_info:
            rank_list.append(Context.json_loads(info.get("json_data")))

        paginator = Paginator(rank_list, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        power_rank.update({"page": page, "number": number})

    power_rank.update({"everyday_list": everyday_list, "rank_switch": rank_switch, "url_date": url_date, "f_list": f_list})
    return render(request, 'users_manage/championship.html', power_rank)


def insert_championship(phone, start_day, end_day, res):
    url = '/v2/shell/gm/query/user_power_rank'
    record_status, uid = int(res["status"]), res["uid"]
    if uid == "":
        context = {"start": start_day, "end": end_day, "status": record_status}
    else:
        context = {"start": start_day, "end": end_day, "status": record_status, "uid": uid}
    context.update({"phone": phone, "pid": 1})
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.text)
    # print("-----------config2020",config)
    if "rank" not in config:
        return []
    else:
        rank_list = []
        rank_config, rank_info = config["config"], config["rank"]
        player_list = sorted(rank_info, key=lambda x: int(x["point"]), reverse=True)
        rid = 0
        level_list = rank_config["level"]
        reward = rank_config["reward"]
        for user in player_list:
            day_time = Time.timestamp_to_str(user["day_stamp"])[:10]
            for level in level_list:
                if not user.has_key("reward") and rid+1 in level:
                    user.update({"reward": reward[rid]})
            if user["shop_virtual"] == 2:
                if user["reward"].has_key("silver_coupon"):
                    cost = int(user["reward"]["silver_coupon"]) / 100
                else:
                    pid = user["reward"]["id"]
                    cost = int(ProcessInfo.get_good_cost(pid))
            else:
                if user.has_key("reward"):
                    cost = int(user["reward"]["silver_coupon"]) / 100
                else:
                    cost = 0
            user.update({"day_time": day_time, "cost": cost, "rank": rid + 1})
            rank_list.append(user)
            rid += 1
        create_championship(rank_list, record_status)
        return rank_list


def create_championship(rank_list, status):
    # PowerRank.objects.all().delete()
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d')
    rank_data = []
    for m_info in rank_list:
        day_time, channel, user_id, sole_id = Time.timestamp_to_str(m_info["day_stamp"], "%Y-%m-%d"), m_info["channel_id"], m_info["uid"], m_info["day_stamp"]
        send_status, point = str(m_info["send_status"]), str(m_info["point"])
        res = PowerRank.objects.filter(sole_id=sole_id, uid=user_id).first()
        if res:
            PowerRank.objects.filter(sole_id=sole_id, uid=user_id).update(
                sole_id=sole_id,
                day_time=day_time,
                insert_time=insert_time,
                point_status=status,
                send_status=send_status,
                uid=user_id,
                channel=channel,
                json_data=Context.json_dumps(m_info)
            )
        else:
            new_rank = PowerRank(
                sole_id=sole_id,
                day_time=day_time,
                insert_time=insert_time,
                point_status=status,
                send_status=send_status,
                uid=user_id,
                channel=channel,
                json_data=Context.json_dumps(m_info)
            )
            rank_data.append(new_rank)

        if len(rank_data) > 1000:
            PowerRank.objects.bulk_create(rank_data)
            rank_data = []

    PowerRank.objects.bulk_create(rank_data)


@decorator
def rob_rank(request):
    phone = request.session.get('uid')
    url = "/v2/shell/gm/query/user_power_rank"
    dic = request.POST
    pid = int(dic.get('pid'))
    if pid == 1:
        user_id = dic.get('user_id').encode('utf-8')
        status = int(dic.get('status'))
        point = int(dic.get('point'))
        context = {"pid": 2, "uid": user_id, "status": status, "point": point, "phone": phone}
        msg_info = "排行榜抢占"
    else:
        power_switch = int(dic.get('power_switch'))
        context = {"pid": 3, "phone": phone, "open": power_switch}
        if power_switch == 0:
            msg_info = "排行榜开启"
        else:
            msg_info = "排行榜关闭"
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.text)
    if "ret" in config:
        status = True
        msg = "{}成功!".format(msg_info)
    else:
        status = False
        msg = "{}失败!".format(msg_info)

    return JsonResponse({'status': status, 'msg': msg})


@decorator
def stop_service(request):
    phone = request.session.get('uid')
    url = '/v2/shell/gm/deal_white_list'
    context = {'phone': phone, 'pid': 3, 'white_status': 1}
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.text)
    if "info" not in config:
        user_list = []
    else:
        if config["info"]:
            user_list = config["info"]
        else:
            user_list = []
    res_over = WhiteList.objects.filter(user_status=1).values("user_list").first()
    if res_over:
        player_list = Context.json_loads(res_over.get("user_list", []))
    else:
        player_list = []

    for uid in user_list:
        if uid not in player_list:
            _, _, _ = add_overlook(phone, uid, 3, WhiteList)
        else:
            continue

    if request.method == 'GET':
        res_over = WhiteList.objects.filter(user_status=1).values("user_list", "user_length").first()
        if res_over:
            o_list = Context.json_loads(res_over.get("user_list", []))
            o_length = res_over.get("user_length", 0)
        else:
            o_list = []
            o_length = 0

        early_info = {"o_list": o_list, "o_leg": o_length}
        return render(request, 'users_manage/stop_service_set.html', early_info)
    else:
        dic = request.POST
        pid = int(dic.get('pid'))
        if pid == 1:  # 添加ID
            o_uid = int(dic.get('o_id'))
            status, msg, o_length = add_overlook(phone, o_uid, 3, WhiteList)
            json_info = {"status": status, "msg": msg, "uid": o_uid, "leg": o_length}
        elif pid == 2:  # 删除ID
            o_uid = int(dic.get('o_id'))
            status, msg, o_length = del_overlook(phone, o_uid, 3, WhiteList)
            json_info = {"status": status, "msg": msg, "uid": o_uid, "leg": o_length}
        else:
            stop_status = dic.get('close_server').encode('utf-8')
            stop_content = dic.get('led').encode('utf-8')
            url = '/v2/shell/gm/deal_white_list'
            context = {'phone': phone, 'pid': 2, 'stop_status': stop_status, 'stop_content': stop_content}
            ret = Context.Controller.request(url, context)
            config = Context.json_loads(ret.text)
            if "ret" in config:
                status = True
                msg = "停服设置成功!"
            else:
                status = False
                msg = "服务器添加数据异常!"

            json_info = {"status": status, "msg": msg}
        return JsonResponse(json_info)


def add_overlook(phone, o_uid, pid, user_object):
    overlook_list, white_status = [], 2
    url = '/v2/shell/gm/deal_white_list'
    res_for = user_object.objects.filter(user_status=3).values("user_list", "user_length").first()
    if res_for:
        f_list = Context.json_loads(res_for.get("user_list", []))
    else:
        f_list = []

    res = user_object.objects.filter(user_status=1).values("user_list", "user_length").first()
    if res:
        over_list = res.get("user_list", [])
        over_leg = res.get("user_length", 0)
        o_list = Context.json_loads(over_list)
        o_length = over_leg
        if o_uid not in o_list and o_uid not in f_list:
            o_list.append(o_uid)
            o_length = len(o_list)
            context = {'phone': phone, 'pid': pid, 'white_status': white_status, 'white_list': o_list}
            ret = Context.Controller.request(url, context)
            config = Context.json_loads(ret.text)
            if "ret" in config:
                user_object.objects.filter(user_status=1).update(
                    user_list=Context.json_dumps(o_list),
                    user_length=o_length
                )
                status = True
                msg = "添加白名单ID成功!"
            else:
                status = False
                msg = "服务器添加数据异常!"
        else:
            status = False
            msg = "白名单ID已存在!"
    else:
        overlook_list.append(o_uid)
        o_length = len(overlook_list)
        context = {'phone': phone, 'pid': pid, 'white_status': white_status, 'white_list': overlook_list}
        ret = Context.Controller.request(url, context)
        config = Context.json_loads(ret.text)
        if "ret" in config:
            user_object.objects.create(
                user_status=1,
                user_list=Context.json_dumps(overlook_list),
                user_length=o_length
            )
            status = True
            msg = "添加白名单ID成功!"
        else:
            status = False
            msg = "服务器添加数据异常!"

    # if status:
    #     record_data = {"status_type": "添加白名单ID", "uid": o_uid}
        # insert_record_data(phone, EarlyRecord, record_data)
    return status, msg, o_length


def del_overlook(phone, uid, pid, user_object):
    white_status = 2
    res = user_object.objects.filter(user_status=1).values("user_list", "user_length").first()
    o_list = Context.json_loads(res.get("user_list", []))
    o_length = res.get("user_length", 0)
    if uid in o_list:
        index = [i for i, x in enumerate(o_list) if x == uid][0]
        del o_list[index]
        o_length = len(o_list)
        url = '/v2/shell/gm/deal_white_list'
        context = {'phone': phone, 'pid': pid, 'white_status': white_status, 'white_list': o_list}
        ret = Context.Controller.request(url, context)
        config = Context.json_loads(ret.text)
        if "ret" in config:
            user_object.objects.filter(user_status=1).update(
                user_list=Context.json_dumps(o_list),
                user_length=o_length
            )
            status = True
            msg = "删除白名单ID成功!"
            # record_data = {"status_type": "删除白名单ID", "uid": uid}
            # insert_record_data(phone, EarlyRecord, record_data)
        else:
            status = False
            msg = "服务器删除数据异常!"
    else:
        status = False
        msg = "白名单ID不存在!"

    return status, msg, o_length


# ==========================玩家兑换解锁==============================
@decorator
def query_unlock_info(request):
    """用户管理——玩家兑换解锁"""
    phone = request.session.get('uid')
    if request.method == "GET":
        return render(request, 'users_manage/exchange_unlock.html', {"uid": ""})
    else:
        dic = request.POST
        user_id = int(dic.get('user_id').encode('utf-8').strip())
        url = '/v2/shell/gm/query/unlock_info'
        context = {'userId': user_id, "phone": phone}
        ret = Context.Controller.request(url, context)
        result = Context.json_loads(ret.text)
        if "ret" not in result:
            return render(request, 'users_manage/exchange_unlock.html', {"uid": ""})
        else:
            play_info = result["ret"]
            print("-------play_info-------", play_info)
            return render(request, 'users_manage/exchange_unlock.html', {"play_info": play_info, "uid": user_id})


@decorator
def player_unlock(request):
    """玩家解锁"""
    phone = request.session.get('uid')
    info = request.POST
    user_id = int(info.get("uid"))
    url = '/v2/shell/gm/player/unlock'
    context = {'userId': user_id, "phone": phone}
    ret = Context.Controller.request(url, context)
    if ret.status_code == 200:
        status, msg = True, "解锁成功!"
    else:
        status, msg = False, "解锁失败!"
    return JsonResponse({'status': status, 'info': msg})


@decorator
def derived_user_info(request):
    """玩家总览--导出xls"""
    dic = request.GET
    room_type = int(dic.get('room_type').encode('utf-8'))
    phone = request.session.get('uid')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=user_data.xls'
    wb = Workbook(encoding='utf8')
    sheet = wb.add_sheet('order-sheet')
    style = easyxf("""
            font:
                name Arial,
                colour_index white,
                bold on,
                height 0xA0;
            align:
                wrap off,
                vert center,
                horiz center;
            pattern:
                pattern solid,
                fore-colour 0x19;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            """)
    sheet.write(0, 0, '序号', style)
    sheet.write(0, 1, 'ID', style)
    sheet.write(0, 2, '昵称', style)
    sheet.write(0, 3, '渠道ID', style)
    sheet.write(0, 4, '手机', style)
    sheet.write(0, 5, '总充值', style)
    sheet.write(0, 6, '当日充值', style)
    sheet.write(0, 7, 'sdk支付', style)
    sheet.write(0, 8, '微信', style)
    sheet.write(0, 9, '支付宝', style)
    sheet.write(0, 10, '总兑换码', style)
    sheet.write(0, 11, '当日兑换码', style)
    sheet.write(0, 12, '当日产出话费券(总话费券)', style)
    sheet.write(0, 13, '当前话费券', style)
    sheet.write(0, 14, '当日产出龙蛋', style)
    sheet.write(0, 15, '当日消耗龙蛋', style)
    sheet.write(0, 16, '总产出龙蛋', style)
    sheet.write(0, 17, '总消耗龙蛋', style)
    sheet.write(0, 18, '当前龙蛋', style)
    sheet.write(0, 19, '当日消耗钻石', style)
    sheet.write(0, 20, '总产出钻石', style)
    sheet.write(0, 21, '免费钻石产出', style)
    sheet.write(0, 22, '付费钻石产出', style)
    sheet.write(0, 23, '总消耗钻石', style)
    sheet.write(0, 24, '炮倍升级消耗钻石', style)
    sheet.write(0, 25, '道具消耗钻石', style)
    sheet.write(0, 26, '当前钻石', style)
    sheet.write(0, 27, '当前强化石', style)
    sheet.write(0, 28, '总产出金币', style)
    sheet.write(0, 29, '免费金币产出', style)
    sheet.write(0, 30, '付费金币产出', style)
    sheet.write(0, 31, '当日金币产出', style)
    sheet.write(0, 32, '当日金币消耗', style)
    sheet.write(0, 33, '洗码量', style)
    sheet.write(0, 34, '当前金币', style)
    sheet.write(0, 35, '当日消耗锁定', style)
    sheet.write(0, 36, '当日消耗全屏冰冻', style)
    sheet.write(0, 37, '当日消耗狂暴', style)
    sheet.write(0, 38, '当日消耗赏金传送', style)
    sheet.write(0, 39, '当前锁定', style)
    sheet.write(0, 40, '当前全屏冰冻', style)
    sheet.write(0, 41, '当前狂暴', style)
    sheet.write(0, 42, '当前赏金传送', style)
    sheet.write(0, 43, '新手成长积分', style)
    sheet.write(0, 44, '当日游戏时长(分钟)', style)
    sheet.write(0, 45, '游戏总时长(分钟)', style)
    sheet.write(0, 46, '当前最大炮倍数', style)
    sheet.write(0, 47, '当前场次', style)
    sheet.write(0, 48, '当日出奖率', style)
    sheet.write(0, 49, '返奖率', style)
    sheet.write(0, 50, '登录次数', style)
    sheet.write(0, 51, '系统设备', style)
    sheet.write(0, 52, '最近登录IP', style)
    sheet.write(0, 53, '创建日期', style)
    sheet.write(0, 54, '最近登录日期', style)

    user_info, _ = get_player_info(phone, room_type)
    show_phone = 204
    user = Account.objects.filter(phone=phone).values("control_list").first()
    if user:
        control_info = Context.json_loads(user.get("control_list"))
    else:
        control_info = []

    data_row = 1
    for info in user_info:
        sheet.write(data_row, 0, data_row)
        sheet.write(data_row, 1, info.get("uid", 0))
        sheet.write(data_row, 2, info.get("nick", 0))
        sheet.write(data_row, 3, info.get("channelid", 0))
        phone1, phone2 = str(info.get("phone", 0)), str(info.get("exchange_phone", 0))
        if show_phone in control_info:
            bound_phone = (0 if phone1 == "0" else phone1)
            exchange_phone = (0 if phone2 == "0" else phone2)
        else:
            bound_phone = (0 if not phone1.isdigit() else phone1[:3] + '****' + phone1[8:])
            exchange_phone = (0 if not phone2.isdigit() else phone2[:3] + '****' + phone2[8:])
        sheet.write(data_row, 4, "{}/{}".format(bound_phone, exchange_phone))
        sheet.write(data_row, 5, info.get("pay_total", 0))
        sheet.write(data_row, 6, info.get("day_pay_total", 0))
        sheet.write(data_row, 7, info.get("sdk_pay_total", 0))
        sheet.write(data_row, 8, info.get("weixin_pay_total", 0))
        sheet.write(data_row, 9, info.get("ali_pay_total", 0))
        sheet.write(data_row, 10, info.get("cdkey_pay_total", 0))
        sheet.write(data_row, 11, info.get("day_cdkey_pay_total", 0))
        sheet.write(data_row, 12, "{}/{}".format(info.get("day_in_silver_coupon", 0), info.get("in_silver_coupon", 0)))
        sheet.write(data_row, 13, info.get("silver_coupon", 0))
        txt_desc = '|'
        for index, name in zip([701, 702, 703, 704], ["毒龙蛋", "冰龙蛋", "火龙蛋", "圣龙蛋"]):
            txt_desc += ("{}:".format(name) + info["relax_day_in_props_{}".format(index)] + '|')
        sheet.write(data_row, 14, str(info['day_in_warhead']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for index, name in zip([701, 702, 703, 704], ["毒龙蛋", "冰龙蛋", "火龙蛋", "圣龙蛋"]):
            txt_desc += ("{}:".format(name) + info["relax_day_out_props_{}".format(index)] + '|')
        sheet.write(data_row, 15, str(info['day_out_warhead']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for index, name in zip([701, 702, 703, 704], ["毒龙蛋", "冰龙蛋", "火龙蛋", "圣龙蛋"]):
            txt_desc += ("{}:".format(name) + info["relax_in_props_{}".format(index)] + '|')
        sheet.write(data_row, 16, str(info['all_in_warhead']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for index, name in zip([701, 702, 703, 704], ["毒龙蛋", "冰龙蛋", "火龙蛋", "圣龙蛋"]):
            txt_desc += ("{}:".format(name) + info["relax_out_props_{}".format(index)] + '|')
        sheet.write(data_row, 17, str(info['all_out_warhead']) + '(' + txt_desc + ')')

        sheet.write(data_row, 18, info.get("day_props_701_704", 0))
        sheet.write(data_row, 19, info.get("day_out_diamond", 0))
        sheet.write(data_row, 20, info.get("in_diamond", 0))
        sheet.write(data_row, 21, info.get("in_free_diamond", 0))
        sheet.write(data_row, 22, info.get("in_pay_diamond", 0))
        sheet.write(data_row, 23, info.get("out_diamond", 0))
        sheet.write(data_row, 24, info.get("out_diamond_relax_barrel", 0))
        sheet.write(data_row, 25, info.get("out_diamond_buy_props", 0))
        sheet.write(data_row, 26, info.get("diamond", 0))
        sheet.write(data_row, 27, info.get("props_219", 0))
        sheet.write(data_row, 28, info.get("in_coin", 0))
        sheet.write(data_row, 29, info.get("in_free_coin", 0))
        sheet.write(data_row, 30, info.get("in_pay_coin", 0))
        txt_desc = '|'
        for txt_info in info['in_coin_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 31, str(info['day_in_coin']) + '(' + txt_desc + ')')
        sheet.write(data_row, 32, info.get("day_out_coin", 0))
        sheet.write(data_row, 33, info.get("day_coin_wash", 0))
        sheet.write(data_row, 34, info.get("coin", 0))
        sheet.write(data_row, 35, info.get("relax_day_out_props_201", 0))
        sheet.write(data_row, 36, info.get("relax_day_out_props_202", 0))
        sheet.write(data_row, 37, info.get("relax_day_out_props_203", 0))
        sheet.write(data_row, 38, info.get("relax_day_out_props_205", 0))
        sheet.write(data_row, 39, info.get("props_201", 0))
        sheet.write(data_row, 40, info.get("props_202", 0))
        sheet.write(data_row, 41, info.get("props_203", 0))
        sheet.write(data_row, 42, info.get("props_205", 0))
        sheet.write(data_row, 43, info.get("player_active_value", 0))
        sheet.write(data_row, 44, info.get("play_time", 0))
        sheet.write(data_row, 45, info.get("total_play_time", 0))
        sheet.write(data_row, 46, info.get("relax_multiple", 0))
        sheet.write(data_row, 47, info.get("room_id", 0))
        sheet.write(data_row, 48, info.get("relax_day_award_rate", 0))
        sheet.write(data_row, 49, info.get("relax_award_rate", 0))
        sheet.write(data_row, 50, "{}/{}".format(info.get("day_login_time", 0), info.get("login_time", 0)))
        sheet.write(data_row, 51, info.get("platform", 0))
        sheet.write(data_row, 52, info.get("createIp", 0))
        sheet.write(data_row, 53, info.get("createTime", 0))
        sheet.write(data_row, 54, info.get("session_login", 0))
        data_row = data_row + 1
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response


# ==========================一键导出玩家信息==============================
@decorator
def one_key_derived_user(request):
    """一键导出玩家xls"""
    phone = request.session.get('uid')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=all_user.xls'
    wb = Workbook(encoding='utf8')
    context = {"phone": phone}
    url = '/v1/shell/query/all_player_data'
    ret = Context.Controller.request(url, context)
    ret_dict = Context.json_loads(ret.text)
    data_info = ret_dict["info"]
    rows = 65530
    new_table = []
    length = len(data_info) / rows
    if len(data_info) % rows != 0:
        length += 1
    for n in range(length):
        new_table.append(data_info[n * rows:rows * (n + 1)])

    for index, user_info in enumerate(new_table):
        crate_new_xls(wb, user_info, index, phone)
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response


def crate_new_xls(Workbook, user_data, index, phone):
    sheet = Workbook.add_sheet('player-sheet{}'.format(index))
    style = easyxf("""
                font:
                    name Arial,
                    colour_index white,
                    bold on,
                    height 0xA0;
                align:
                    wrap off,
                    vert center,
                    horiz center;
                pattern:
                    pattern solid,
                    fore-colour 0x19;
                borders:
                    left THIN,
                    right THIN,
                    top THIN,
                    bottom THIN;
                """)
    sheet.write(0, 0, '序号', style)
    sheet.write(0, 1, 'ID', style)
    sheet.write(0, 2, '昵称', style)
    sheet.write(0, 3, '渠道ID', style)
    sheet.write(0, 4, '手机', style)
    sheet.write(0, 5, '总充值', style)
    sheet.write(0, 6, '当日充值', style)
    sheet.write(0, 7, 'sdk支付', style)
    sheet.write(0, 8, '微信', style)
    sheet.write(0, 9, '支付宝', style)
    sheet.write(0, 10, '总兑换码', style)
    sheet.write(0, 11, '当日兑换码', style)
    sheet.write(0, 12, '当日产出话费券(总话费券)', style)
    sheet.write(0, 13, '当前话费券', style)
    sheet.write(0, 14, '当日产出龙蛋', style)
    sheet.write(0, 15, '当日消耗龙蛋', style)
    sheet.write(0, 16, '总产出龙蛋', style)
    sheet.write(0, 17, '总消耗龙蛋', style)
    sheet.write(0, 18, '当前龙蛋', style)
    sheet.write(0, 19, '当日消耗钻石', style)
    sheet.write(0, 20, '总产出钻石', style)
    sheet.write(0, 21, '免费钻石产出', style)
    sheet.write(0, 22, '付费钻石产出', style)
    sheet.write(0, 23, '总消耗钻石', style)
    sheet.write(0, 24, '炮倍升级消耗钻石', style)
    sheet.write(0, 25, '道具消耗钻石', style)
    sheet.write(0, 26, '当前钻石', style)
    sheet.write(0, 27, '当前强化石', style)
    sheet.write(0, 28, '总产出金币', style)
    sheet.write(0, 29, '免费金币产出', style)
    sheet.write(0, 30, '付费金币产出', style)
    sheet.write(0, 31, '当前金币', style)
    sheet.write(0, 32, '当日消耗锁定', style)
    sheet.write(0, 33, '当日消耗全屏冰冻', style)
    sheet.write(0, 34, '当日消耗狂暴', style)
    sheet.write(0, 35, '当日消耗赏金传送', style)
    sheet.write(0, 36, '当前锁定', style)
    sheet.write(0, 37, '当前全屏冰冻', style)
    sheet.write(0, 38, '当前狂暴', style)
    sheet.write(0, 39, '当前赏金传送', style)
    sheet.write(0, 40, '新手成长积分', style)
    sheet.write(0, 41, '当日游戏时长(分钟)', style)
    sheet.write(0, 42, '游戏总时长(分钟)', style)
    sheet.write(0, 43, '当前最大炮倍数', style)
    sheet.write(0, 44, '当前场次', style)
    sheet.write(0, 45, '当日出奖率', style)
    sheet.write(0, 46, '返奖率', style)
    sheet.write(0, 47, '登录次数', style)
    sheet.write(0, 48, '系统设备', style)
    sheet.write(0, 49, '最近登录IP', style)
    sheet.write(0, 50, '创建日期', style)
    sheet.write(0, 51, '最近登录日期', style)

    show_phone = 204
    user = Account.objects.filter(phone=phone).values("control_list").first()
    if user:
        control_info = Context.json_loads(user.get("control_list"))
    else:
        control_info = []

    data_row = 1
    for info in user_data:
        sheet.write(data_row, 0, data_row)
        sheet.write(data_row, 1, info.get("uid", 0))
        sheet.write(data_row, 2, info.get("nick", 0))
        sheet.write(data_row, 3, info.get("channelid", 0))
        phone1, phone2 = str(info.get("phone", 0)), str(info.get("exchange_phone", 0))
        if show_phone in control_info:
            bound_phone = (0 if phone1 == "0" else phone1)
            exchange_phone = (0 if phone2 == "0" else phone2)
        else:
            bound_phone = (0 if phone1 == "0" else phone1[:3] + '****' + phone1[8:])
            exchange_phone = (0 if phone2 == "0" else phone2[:3] + '****' + phone2[8:])
        sheet.write(data_row, 4, "{}/{}".format(bound_phone, exchange_phone))
        sheet.write(data_row, 5, info.get("pay_total", 0))
        sheet.write(data_row, 6, info.get("day_pay_total", 0))
        sheet.write(data_row, 7, info.get("sdk_pay_total", 0))
        sheet.write(data_row, 8, info.get("weixin_pay_total", 0))
        sheet.write(data_row, 9, info.get("ali_pay_total", 0))
        sheet.write(data_row, 10, info.get("cdkey_pay_total", 0))
        sheet.write(data_row, 11, info.get("day_cdkey_pay_total", 0))
        sheet.write(data_row, 12, "{}/{}".format(info.get("day_in_silver_coupon", 0), info.get("in_silver_coupon", 0)))
        sheet.write(data_row, 13, info.get("silver_coupon", 0))
        sheet.write(data_row, 14, info.get("day_in_warhead", 0))
        sheet.write(data_row, 15, info.get("day_out_warhead", 0))
        sheet.write(data_row, 16, info.get("all_in_warhead", 0))
        sheet.write(data_row, 17, info.get("all_out_warhead", 0))
        sheet.write(data_row, 18, info.get("day_props_701_704", 0))
        sheet.write(data_row, 19, info.get("day_out_diamond", 0))
        sheet.write(data_row, 20, info.get("in_diamond", 0))
        sheet.write(data_row, 21, info.get("in_free_diamond", 0))
        sheet.write(data_row, 22, info.get("in_pay_diamond", 0))
        sheet.write(data_row, 23, info.get("out_diamond", 0))
        sheet.write(data_row, 24, info.get("out_diamond_relax_barrel", 0))
        sheet.write(data_row, 25, info.get("out_diamond_buy_props", 0))
        sheet.write(data_row, 26, info.get("diamond", 0))
        sheet.write(data_row, 27, info.get("props_219", 0))
        sheet.write(data_row, 28, info.get("in_coin", 0))
        sheet.write(data_row, 29, info.get("in_free_coin", 0))
        sheet.write(data_row, 30, info.get("in_pay_coin", 0))
        sheet.write(data_row, 31, info.get("coin", 0))
        sheet.write(data_row, 32, info.get("relax_day_out_props_201", 0))
        sheet.write(data_row, 33, info.get("relax_day_out_props_202", 0))
        sheet.write(data_row, 34, info.get("relax_day_out_props_203", 0))
        sheet.write(data_row, 35, info.get("relax_day_out_props_205", 0))
        sheet.write(data_row, 36, info.get("props_201", 0))
        sheet.write(data_row, 37, info.get("props_202", 0))
        sheet.write(data_row, 38, info.get("props_203", 0))
        sheet.write(data_row, 39, info.get("props_205", 0))
        sheet.write(data_row, 40, info.get("player_active_value", 0))
        sheet.write(data_row, 41, info.get("play_time", 0))
        sheet.write(data_row, 42, info.get("total_play_time", 0))
        sheet.write(data_row, 43, info.get("relax_multiple", 0))
        sheet.write(data_row, 44, info.get("room_id", 0))
        sheet.write(data_row, 45, info.get("relax_day_award_rate", 0))
        sheet.write(data_row, 46, info.get("relax_award_rate", 0))
        sheet.write(data_row, 47, "{}/{}".format(info.get("day_login_time", 0), info.get("login_time", 0)))
        sheet.write(data_row, 48, info.get("platform", 0))
        sheet.write(data_row, 49, info.get("createIp", 0))
        sheet.write(data_row, 50, info.get("createTime", 0))
        sheet.write(data_row, 51, info.get("session_login", 0))
        data_row = data_row + 1


@decorator
def derived_period_user(request):
    """玩家期间数据--导出xls"""
    phone = request.session.get('uid')
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=period_user.xls'
    wb = Workbook(encoding='utf8')
    sheet = wb.add_sheet('order-sheet')
    style = easyxf("""
            font:
                name Arial,
                colour_index white,
                bold on,
                height 0xA0;
            align:
                wrap off,
                vert center,
                horiz center;
            pattern:
                pattern solid,
                fore-colour 0x19;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            """)
    sheet.write(0, 0, '序号', style)
    sheet.write(0, 1, '日期', style)
    sheet.write(0, 2, '玩家ID', style)
    sheet.write(0, 3, '渠道ID', style)
    sheet.write(0, 4, '总充值', style)
    sheet.write(0, 5, '当天充值', style)
    sheet.write(0, 6, '当天话费券产出', style)
    sheet.write(0, 7, '当天话费券消耗', style)
    sheet.write(0, 8, '当天话费券剩余', style)
    sheet.write(0, 9, '当天毒龙蛋产出', style)
    sheet.write(0, 10, '当天冰龙蛋产出', style)
    sheet.write(0, 11, '当天火龙蛋产出', style)
    sheet.write(0, 12, '当天圣龙蛋产出', style)
    sheet.write(0, 13, '当天毒龙蛋消耗', style)
    sheet.write(0, 14, '当天冰龙蛋消耗', style)
    sheet.write(0, 15, '当天火龙蛋消耗', style)
    sheet.write(0, 16, '当天圣龙蛋消耗', style)
    sheet.write(0, 17, '当天毒龙蛋剩余', style)
    sheet.write(0, 18, '当天冰龙蛋剩余', style)
    sheet.write(0, 19, '当天火龙蛋剩余', style)
    sheet.write(0, 20, '当天圣龙蛋剩余', style)
    sheet.write(0, 21, '在线总时长', style)
    sheet.write(0, 22, '第一次付费时间', style)
    sheet.write(0, 23, '当天金币场炮倍', style)
    sheet.write(0, 24, '当天鸟蛋场炮倍', style)
    sheet.write(0, 25, '当天产出免费金币', style)
    sheet.write(0, 26, '当天产出付费金币', style)
    sheet.write(0, 27, '当天产出免费钻石', style)
    sheet.write(0, 28, '当天产出付费钻石', style)
    sheet.write(0, 29, '当天钻石消耗', style)
    sheet.write(0, 30, '当天钻石剩余', style)
    sheet.write(0, 31, '当天鸟蛋兑入', style)
    sheet.write(0, 32, '当天鸟蛋兑出', style)
    sheet.write(0, 33, '当天鸟蛋剩余', style)
    sheet.write(0, 34, '前日鸟蛋剩余', style)
    sheet.write(0, 35, '当天强化石产出', style)
    sheet.write(0, 36, '当天强化石消耗', style)
    sheet.write(0, 37, '当天强化石剩余', style)
    sheet.write(0, 38, '当天绿灵石产出', style)
    sheet.write(0, 39, '当天绿灵石消耗', style)
    sheet.write(0, 40, '当天绿灵石剩余', style)
    sheet.write(0, 41, '当天蓝魔石产出', style)
    sheet.write(0, 42, '当天蓝魔石消耗', style)
    sheet.write(0, 43, '当天蓝魔石剩余', style)
    sheet.write(0, 44, '当天紫精石产出', style)
    sheet.write(0, 45, '当天紫精石消耗', style)
    sheet.write(0, 46, '当天紫精石剩余', style)
    sheet.write(0, 47, '当天血精石产出', style)
    sheet.write(0, 48, '当天血精石消耗', style)
    sheet.write(0, 49, '当天血精石剩余', style)
    sheet.write(0, 50, '当天灵魂宝石产出', style)
    sheet.write(0, 51, '当天灵魂宝石消耗', style)
    sheet.write(0, 52, '当天灵魂宝石剩余', style)
    sheet.write(0, 53, '当天锁定产出', style)
    sheet.write(0, 54, '当天冰冻产出', style)
    sheet.write(0, 55, '当天狂暴无双产出', style)
    sheet.write(0, 56, '当天赏金传送产出', style)
    sheet.write(0, 57, '当天锁定消耗', style)
    sheet.write(0, 58, '当天冰冻消耗', style)
    sheet.write(0, 59, '当天狂暴无双消耗', style)
    sheet.write(0, 60, '当天赏金传送消耗', style)
    sheet.write(0, 61, '当天洗码量', style)

    user_info, _ = get_user_period(phone)
    data_row = 1
    for info in user_info:
        sheet.write(data_row, 0, data_row)
        sheet.write(data_row, 1, info["day_time"])
        sheet.write(data_row, 2, info["uid"])
        channel = info["channel"]
        if channel in chanel_info:
            channel_name = chanel_info[channel]
        else:
            channel_name = channel
        sheet.write(data_row, 3, channel_name)
        sheet.write(data_row, 4, info["pay_total"])
        sheet.write(data_row, 5, info["day_pay_total"])
        txt_desc = '|'
        for txt_info in info['in_silver_coupon_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 6, str(info['in_silver_coupon']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['out_silver_coupon_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 7, str(info['out_silver_coupon']) + '(' + txt_desc + ')')
        sheet.write(data_row, 8, info["fix_own_silver_coupon"])
        txt_desc = '|'
        for txt_info in info['in_props_701_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 9, str(info['in_props_701']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['in_props_702_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 10, str(info['in_props_702']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['in_props_703_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 11, str(info['in_props_703']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['in_props_704_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 12, str(info['in_props_704']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['out_props_701_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 13, str(info['out_props_701']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['out_props_702_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 14, str(info['out_props_702']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['out_props_703_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 15, str(info['out_props_703']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['out_props_704_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 16, str(info['out_props_704']) + '(' + txt_desc + ')')
        sheet.write(data_row, 17, info["fix_own_props_701"])
        sheet.write(data_row, 18, info["fix_own_props_702"])
        sheet.write(data_row, 19, info["fix_own_props_703"])
        sheet.write(data_row, 20, info["fix_own_props_704"])
        sheet.write(data_row, 21, info["total_play_time"])
        sheet.write(data_row, 22, info["first_pay_time"])
        sheet.write(data_row, 23, info["relax_multiple"])
        sheet.write(data_row, 24, info["power_multiple"])
        txt_desc = '|'
        for txt_info in info['in_free_coin_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 25, str(info['in_free_coin']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['in_pay_coin_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 26, str(info['in_pay_coin']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['in_free_diamond_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 27, str(info['in_free_diamond']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['in_pay_diamond_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 28, str(info['in_pay_diamond']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['out_diamond_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 29, str(info['out_diamond']) + '(' + txt_desc + ')')
        sheet.write(data_row, 30, info["fix_own_diamond"])
        sheet.write(data_row, 31, info["day_exchange_in"])
        sheet.write(data_row, 32, info["day_exchange_out"])
        sheet.write(data_row, 33, info["fix_own_power"])
        sheet.write(data_row, 34, info["fix_last_own_power"])
        txt_desc = '|'
        for txt_info in info['in_props_219_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 35, str(info['in_props_219']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['out_props_219_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 36, str(info['out_props_219']) + '(' + txt_desc + ')')
        sheet.write(data_row, 37, info["fix_own_props_219"])
        txt_desc = '|'
        for txt_info in info['in_props_215_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 38, str(info['in_props_215']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['out_props_215_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 39, str(info['out_props_215']) + '(' + txt_desc + ')')
        sheet.write(data_row, 40, info["fix_own_props_215"])
        txt_desc = '|'
        for txt_info in info['in_props_216_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 41, str(info['in_props_216']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['out_props_216_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 42, str(info['out_props_216']) + '(' + txt_desc + ')')
        sheet.write(data_row, 43, info["fix_own_props_216"])

        txt_desc = '|'
        for txt_info in info['in_props_217_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 44, str(info['in_props_217']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['out_props_217_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 45, str(info['out_props_217']) + '(' + txt_desc + ')')
        sheet.write(data_row, 46, info["fix_own_props_217"])

        txt_desc = '|'
        for txt_info in info['in_props_218_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 47, str(info['in_props_218']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['out_props_218_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 48, str(info['out_props_218']) + '(' + txt_desc + ')')
        sheet.write(data_row, 49, info["fix_own_props_218"])

        txt_desc = '|'
        for txt_info in info['in_props_301_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 50, str(info['in_props_301']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['out_props_301_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 51, str(info['out_props_301']) + '(' + txt_desc + ')')
        sheet.write(data_row, 52, info["fix_own_props_301"])

        txt_desc = '|'
        for txt_info in info['in_props_201_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 53, str(info['in_props_201']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['in_props_202_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 54, str(info['in_props_202']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['in_props_203_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 55, str(info['in_props_203']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['in_props_205_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 56, str(info['in_props_205']) + '(' + txt_desc + ')')

        txt_desc = '|'
        for txt_info in info['out_props_201_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 57, str(info['out_props_201']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['out_props_202_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 58, str(info['out_props_202']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['out_props_203_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 59, str(info['out_props_203']) + '(' + txt_desc + ')')
        txt_desc = '|'
        for txt_info in info['out_props_205_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 60, str(info['out_props_205']) + '(' + txt_desc + ')')

        txt_desc = '|'
        for txt_info in info['day_in_power_pop']:
            txt_desc += (txt_info + '|')
        sheet.write(data_row, 61, str(info['day_in_power']) + '(' + txt_desc + ')')
        data_row = data_row + 1
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response


@decorator
def derived_power_user(request):
    """鸟蛋场玩家总览--导出xls"""
    phone, room_type = request.session.get('uid'), ["400", "401", "402", "403"]
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=period_user.xls'
    wb = Workbook(encoding='utf8')
    sheet = wb.add_sheet('order-sheet')
    style = easyxf("""
            font:
                name Arial,
                colour_index white,
                bold on,
                height 0xA0;
            align:
                wrap off,
                vert center,
                horiz center;
            pattern:
                pattern solid,
                fore-colour 0x19;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            """)
    sheet.write(0, 0, '序号', style)
    sheet.write(0, 1, '玩家ID', style)
    sheet.write(0, 2, '玩家昵称', style)
    sheet.write(0, 3, '渠道ID', style)
    sheet.write(0, 4, '总充值', style)
    sheet.write(0, 5, '当日鸟蛋产出', style)
    sheet.write(0, 6, '当日鸟蛋消耗', style)
    sheet.write(0, 7, '鸟蛋净收益', style)
    sheet.write(0, 8, '当前龙蛋', style)
    sheet.write(0, 9, '当日鸟蛋兑入', style)
    sheet.write(0, 10, '当日鸟蛋总兑入', style)
    sheet.write(0, 11, '当日鸟蛋兑出', style)
    sheet.write(0, 12, '当日鸟蛋总兑出', style)
    sheet.write(0, 13, '当前鸟蛋', style)
    sheet.write(0, 14, '打鸟消耗', style)
    sheet.write(0, 15, '当前话费券', style)
    sheet.write(0, 16, '当日消耗钻石', style)
    sheet.write(0, 17, '总消耗钻石', style)
    sheet.write(0, 18, '当前钻石', style)
    sheet.write(0, 19, '当日消耗锁/冰/狂/传', style)
    sheet.write(0, 20, '当前消耗锁/冰/狂/传', style)
    sheet.write(0, 21, '最大炮倍数', style)
    sheet.write(0, 22, '当前场次', style)
    sheet.write(0, 23, '当日返奖率', style)
    sheet.write(0, 24, '总返奖率', style)

    user_info, _ = get_player_info(phone, room_type)
    data_row = 1
    for info in user_info:
        sheet.write(data_row, 0, data_row)
        sheet.write(data_row, 1, info["uid"])
        sheet.write(data_row, 2, info["nick"])
        channel = info["channelid"]
        if channel in chanel_info:
            channel_name = chanel_info[channel]
        else:
            channel_name = channel
        sheet.write(data_row, 3, channel_name)
        sheet.write(data_row, 4, info["pay_total"])
        sheet.write(data_row, 5, info["day_in_power"])
        sheet.write(data_row, 6, info["day_out_power"])
        sheet.write(data_row, 7, info["power_yield"])
        sheet.write(data_row, 8, info["dragon_egg"])
        sheet.write(data_row, 9, info["day_exchange_in_power"])
        sheet.write(data_row, 10, info["exchange_in_power"])
        sheet.write(data_row, 11, info["day_exchange_out_power"])
        sheet.write(data_row, 12, info["exchange_out_power"])
        sheet.write(data_row, 13, info["power"])
        sheet.write(data_row, 14, info["wash_quantity"])
        sheet.write(data_row, 15, info["silver_coupon"])
        sheet.write(data_row, 16, info["day_out_diamond"])
        sheet.write(data_row, 17, info["out_diamond"])
        sheet.write(data_row, 18, info["diamond"])
        sheet.write(data_row, 19, str(info['power_day_out_props_201']) + '/' + str(info['power_day_out_props_202']) + '/' + str(info['power_day_out_props_203']) + '/' + str(info['power_day_out_props_205']))
        sheet.write(data_row, 20, str(info['props_201']) + '/' + str(info['props_202']) + '/' + str(info['props_203']) + '/' + str(info['props_205']))
        sheet.write(data_row, 21, info["power_multiple"])
        room = get_room_name(info["room_id"])
        sheet.write(data_row, 22, room)
        sheet.write(data_row, 23, info["power_day_award_rate"])
        sheet.write(data_row, 24, info["power_award_rate"])
        data_row = data_row + 1
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response


def get_room_name(room_id):
    room = str(room_id)
    if room == "301":
        return "新手海岛"
    elif room == "302":
        return "林海雪原"
    elif room == "303":
        return "极寒冰川"
    elif room == "304":
        return "猎龙峡谷"
    elif room == "305":
        return "绝境炼狱"
    elif room == "306":
        return "极度魔界"
    elif room == "307":
        return "上古战场"
    elif room == "400":
        return "刺激战场-体验"
    elif room == "401":
        return "刺激战场-初"
    elif room == "402":
        return "刺激战场-中"
    elif room == "403":
        return "刺激战场-高"
    else:
        return room