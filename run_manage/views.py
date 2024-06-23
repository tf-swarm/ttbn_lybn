# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.paginator import Paginator
from util.context import Context
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from xlwt import *
from io import BytesIO
from util.tool import Time, Tool
from .models import *
from util.process import ProcessInfo
from util.gamedate import *
import time
import json
from xlwt import *
from login_manage.models import *
from login_manage.views import decorator
from control_manage.models import Account
from hashlib import sha1
from limit_time_shop.views import insert_redis_exchange
from limit_time_shop.models import *
from util.Tips_show import Tips
from django.conf import settings
import os
import copy
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

@decorator
def game_data_collect(request):
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    add_channel = {"1004_10": "OPPO游客", "1004_11": "OPPO广告包游客"}
    for ch_id, ch_name in add_channel.items():
        chanel_info.update({ch_id: ch_name})
    url_date, number, phone = "/run_manage/game_data_collect/", 1, request.session.get('uid')
    data_type = 1
    if request.method == 'GET':
        end_day = datetime.date.today().strftime('%Y-%m-%d')
        one_page = request.GET.get('page')
        if one_page:
            conf, day_info = get_data_collect(phone, GameCollect, data_type)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            day_info.update({"number": number, "page": page})
        else:
            day_info = {"channel": "0", "start_day": end_day, "end_day": end_day, "number": number}
    else:
        dic = request.POST
        channel = dic.get('channel').encode('utf-8')  # 渠道name
        start_time = dic.get("start_time")[:10]  # 查询开始时间
        end_time = dic.get("stop_time")[:10]  # 查询结束时间

        start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')

        day_list = []
        while start_date <= end_date:
            res = GameCollect.objects.filter(day_time=start_date).first()
            every_day = Time.datetime_to_str(start_date, '%Y-%m-%d')
            if res:
                start_date = Time.next_days(start_date)
                continue
            else:
                day_order = Context.RedisCache.hget_keys('game_collect:{}:{}:*'.format("system", every_day))
                if day_order:
                    day_list.append(every_day)
                    # if every_day == datetime.datetime.now().strftime('%Y-%m-%d'):
                    #     redis_key = Context.RedisCache.hget_keys('game_collect:{}:{}:*'.format(phone, every_day))  # 删除当天数据
                    #     for del_key in redis_key:
                    #         Context.RedisCache.delete(del_key)
                    #     insert_redis_collect(phone, every_day, every_day, channel, data_type)  # 插入数据
                    # else:
                    start_date = Time.next_days(start_date)
                    continue
                else:
                    day_list.append(every_day)
                    start_date = Time.next_days(start_date)
                    continue
                    #insert_redis_collect("system", every_day, every_day, channel, data_type)  # 插入数据
            #start_date = Time.next_days(start_date)

        day_info = {"start_day": start_time, "end_day": end_time, "channel": channel, "day_list": day_list}
        keys = 'game_collect:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, day_info)

        sort_info = get_day_collect(phone, day_info, GameCollect, data_type)
        paginator = Paginator(sort_info, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        day_info.update({"page": page, "number": number})

    day_info.update({"chanel_info": chanel_info, "url_date": url_date})
    return render(request, 'run_manage/game_data_collect.html', day_info)


@decorator
def run_data_collect(request):
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    url_date, number, phone = "/run_manage/run_data_collect/", 1, request.session.get('uid')
    data_type = 2
    if request.method == 'GET':
        end_day = datetime.date.today().strftime('%Y-%m-%d')
        one_page = request.GET.get('page')
        if one_page:
            conf, day_info = get_data_collect(phone, RunCollect, data_type)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            day_info.update({"number": number, "page": page})
        else:
            day_info = {"channel": "0", "start_day": end_day, "end_day": end_day, "number": number}
    else:
        dic = request.POST
        channel = dic.get('channel').encode('utf-8')  # 渠道name
        start_time = dic.get("start_time")[:10]  # 查询开始时间
        end_time = dic.get("stop_time")[:10]  # 查询结束时间

        start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')

        day_list = []
        while start_date <= end_date:
            res = RunCollect.objects.filter(day_time=start_date).first()
            every_day = Time.datetime_to_str(start_date, '%Y-%m-%d')
            if res:
                start_date = Time.next_days(start_date)
                continue
            else:
                day_order = Context.RedisCache.hget_keys('run_collect:{}:{}:*'.format("system", every_day))
                if day_order:
                    day_list.append(every_day)
                    # if every_day == datetime.datetime.now().strftime('%Y-%m-%d'):
                    #     redis_key = Context.RedisCache.hget_keys('run_collect:*:{}:*'.format(every_day))  # 删除当天数据
                    #     for del_key in redis_key:
                    #         Context.RedisCache.delete(del_key)
                    #     insert_redis_collect(phone, every_day, every_day, channel, data_type)  # 插入数据
                    # else:
                    start_date = Time.next_days(start_date)
                    continue
                else:
                    day_list.append(every_day)
                    start_date = Time.next_days(start_date)
                    continue
                    #insert_redis_collect("system", every_day, every_day, channel, data_type)  # 插入数据
            #start_date = Time.next_days(start_date)

        day_info = {"start_day": start_time, "end_day": end_time, "channel": channel, "day_list": day_list}
        keys = 'run_collect:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, day_info)

        sort_info = get_day_collect(phone, day_info, RunCollect, data_type)
        paginator = Paginator(sort_info, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        day_info.update({"page": page, "number": number})

    day_info.update({"chanel_info": chanel_info, "url_date": url_date})
    return render(request, 'run_manage/run_data_collect.html', day_info)


@decorator
def retention_rate(request):
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    url_date, number, phone = "/run_manage/retention_rate/", 1, request.session.get('uid')
    if request.method == 'GET':
        end_day = datetime.date.today().strftime('%Y-%m-%d')
        one_page = request.GET.get('page')
        if one_page:
            conf, day_info = get_remain_data(phone)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            day_info.update({"number": number, "page": page})
        else:
            day_info = {"channel": "0", "start_day": end_day, "end_day": end_day, "number": number}
    else:
        dic = request.POST
        channel = dic.get('channel').encode('utf-8')  # 渠道name
        start_time = dic.get("start_time")[:10]  # 查询开始时间
        end_time = dic.get("stop_time")[:10]  # 查询结束时间

        day_info = {"start_day": start_time, "end_day": end_time, "channel": channel}
        keys = 'retention_rate:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, day_info)

        start_day = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_day = Time.str_to_datetime(end_time, '%Y-%m-%d')

        while start_day <= end_day:
            res = Retention.objects.filter(day_time=start_day).first()
            cur_day = Time.datetime_to_str(start_day, '%Y-%m-%d')
            if res:
                start_day = Time.next_days(start_day)
                continue
            else:
                one_channel = "1000"
                insert_retention_info(cur_day, cur_day, one_channel)  # 插入数据
            start_day = Time.next_days(start_day)

        start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')
        if channel == "0":
            res_info = Retention.objects.filter(day_time__range=(start_date, end_date)).values('json_data').order_by("-day_time")
        else:
            res_info = Retention.objects.filter(day_time__range=(start_date, end_date), channel=channel).values('json_data')

        sorted_info = []
        for data in res_info:
            sorted_info.append(Context.json_loads(data.get("json_data")))
        paginator = Paginator(sorted_info, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        day_info.update({"page": page, "number": number})

    day_info.update({"chanel_info": chanel_info, "url_date": url_date})
    return render(request, 'run_manage/retention_rate.html', day_info)


def insert_retention_info(start, end, one_channel):
    """留存数据"""
    start_day = Time.str_to_datetime(start, '%Y-%m-%d')
    end_day = Time.str_to_datetime(end, '%Y-%m-%d')

    day_info = []
    visitor_info = {"1004_10": "1004_0", "1004_11": "1004_2", "1004_0": "1004_0", "1004_2": "1004_2"}
    login_level = login_level_list()
    old_data = ChannelList.objects.all().values('channel_data').first()
    all_channel = Context.json_loads(old_data['channel_data'])  # 渠道
    del all_channel['0']
    del all_channel['1000']
    add_channel = {"1004_10": "OPPO游客", "1004_11": "OPPO广告包游客"}
    for ch_id, ch_name in add_channel.items():
        all_channel.update({ch_id: ch_name})
    while start_day <= end_day:
        channel_data = []
        fmt = Time.datetime_to_str(start_day, '%Y-%m-%d')
        if one_channel == "1000":
            for channel_id, channel_name in all_channel.items():
                if visitor_info.has_key(str(channel_id)):
                    channel = visitor_info[channel_id]
                    if channel == str(channel_id):
                        only_channel = visitor_retention_rate(fmt, channel, 0)
                    else:
                        only_channel = visitor_retention_rate(fmt, channel, 1)
                else:
                    only_channel = channel_retention_rate(fmt, channel_id)
                if len(only_channel) > 0 and int(only_channel["daily_count"]) > 0:
                    only_channel.update({"channel": channel_id})
                    channel_data.append({channel_id: only_channel})
            all_info, daily_count = {}, 0
            for info in channel_data:
                for channel_id, channel_info in info.items():
                    daily_count += int(channel_info['daily_count'])
                    for channelKey, channelValue in channel_info.items():
                        if channelKey != 'day_time' and channelKey != 'channel' and channelKey != 'daily_count':
                            all_info.update({channelKey: int(all_info.get(channelKey, 0)) + int(channelValue)})

            if len(all_info) > 0:
                new_user_count = daily_count
                # 次日留存率-30日留存率
                for index, days in login_level.items():
                    all_info["login_rate_{}".format(index)] = round((0 if new_user_count == 0 else all_info["login_level_{}".format(index)] / float(new_user_count)), 3)
                all_info.update({"day_time": fmt, "channel": "1000", "daily_count": daily_count})
                channel_data.append({one_channel: all_info})
        else:
            if visitor_info.has_key(str(one_channel)):
                channel = visitor_info[one_channel]
                if channel == str(one_channel):
                    only_channel = visitor_retention_rate(fmt, channel, 0)
                else:
                    only_channel = visitor_retention_rate(fmt, channel, 1)
                only_channel.update({"channel": one_channel})
            else:
                only_channel = channel_retention_rate(fmt, one_channel)
            if len(only_channel) > 0 and int(only_channel["daily_count"]) > 0:
                channel_data.append({one_channel: only_channel})
        day_info.append({fmt: channel_data})
        start_day = Time.next_days(start_day)
    create_retention_info(day_info)


def channel_retention_rate(fmt, channel):
    login_level = login_level_list()
    remain_info = get_login_remain(channel, fmt, login_level)
    result = Context.RedisCache.hash_getall('stat:{}:{}'.format(channel, fmt))
    user_daily = Context.RedisCache.hget_keys('user_daily:{}:{}:*'.format(channel, fmt))
    remain_info["daily_count"] = 0
    if result and user_daily:
        remain_info["daily_count"] = result.get('{}.new.user.count'.format(channel), 0)  # 新增人数

    new_user_count = int(remain_info["daily_count"])
    for index, days in login_level.items():
        remain_info["login_rate_{}".format(index)] = round((0 if new_user_count == 0 else remain_info["login_level_{}".format(index)] / float(new_user_count)), 3)
    remain_info.update({"day_time": fmt, "channel": channel})
    return remain_info


def visitor_retention_rate(fmt, channel, status):
    login_level = login_level_list()
    remain_info = get_login_visitor(channel, fmt, login_level, status)
    _, daily_count = deal_visitor_user(fmt, channel, status)
    new_user_count = len(daily_count)
    for index, days in login_level.items():
        remain_info["login_rate_{}".format(index)] = round((0 if new_user_count == 0 else remain_info["login_level_{}".format(index)] / float(new_user_count)), 3)
    remain_info.update({"day_time": fmt, "daily_count": len(daily_count)})
    return remain_info


def get_login_visitor(channel_id, day_time, login_level, status):
    guid = status
    user_list = Context.RedisCache.hget_keys('user_daily:{}:{}:*'.format(channel_id, day_time))
    player_list = []
    start_stamp = Time.str_to_timestamp(day_time + " 00:00:00")
    end_stamp = Time.str_to_timestamp(day_time + " 23:59:59")
    for user_str in user_list:
        user_id = int(user_str.split(':')[3])
        if user_id > 1000000:
            guid_create = Tool.to_int(Context.RedisMix.hash_get('user:{}'.format(user_id), 'guidCreate'), 0)
            create_stamp = Time.str_to_timestamp(str(Context.RedisMix.hash_get('user:{}'.format(user_id), 'createTime'))[:19])
            if create_stamp >= start_stamp and create_stamp <= end_stamp and user_id not in player_list and guid_create == guid:
                player_list.append(user_id)
            else:
                continue
        else:
            continue

    login_remain = {}
    for index, days in login_level.items():
        login_remain["login_level_{}".format(index)] = 0

    for uid in player_list:
        for index, days in login_level.items():
            result = get_day_login_level(day_time, channel_id, uid, days)
            login_remain["login_level_{}".format(index)] += result
    return login_remain


def get_login_remain(channel_id, day_time, login_level):
    user_list = Context.RedisCache.hget_keys('user_daily:{}:{}:*'.format(channel_id, day_time))
    player_list = []
    start_stamp = Time.str_to_timestamp(day_time + " 00:00:00")
    end_stamp = Time.str_to_timestamp(day_time + " 23:59:59")
    for user_str in user_list:
        user_id = int(user_str.split(':')[3])
        if user_id > 1000000:
            create_stamp = Time.str_to_timestamp(str(Context.RedisMix.hash_get('user:{}'.format(user_id), 'createTime'))[:19])
            if create_stamp >= start_stamp and create_stamp <= end_stamp and str(user_id) not in player_list:
                player_list.append(user_id)
            else:
                continue
        else:
            continue

    login_remain = {}
    for index, days in login_level.items():
        login_remain["login_level_{}".format(index)] = 0

    for uid in player_list:
        for index, days in login_level.items():
            result = get_day_login_level(day_time, channel_id, uid, days)
            login_remain["login_level_{}".format(index)] += result
    return login_remain


def get_remain_data(phone):
    """留存数据"""
    keys = 'retention_rate:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day", "channel"])  # 筛选条件
    start_time, end_time, channel = result[0], result[1], result[2]
    def_info = {"start_day": start_time, "end_day": end_time, "channel": channel}

    start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
    end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')
    if channel == "0":
        res_info = Retention.objects.filter(day_time__range=(start_date, end_date)).values('json_data').order_by("-day_time")
    else:
        res_info = Retention.objects.filter(day_time__range=(start_date, end_date), channel=channel).values('json_data')

    config = []
    for data in res_info:
        config.append(Context.json_loads(data.get("json_data")))
    return config, def_info


@decorator
def ltv_collect(request):
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    url_date, number, phone = "/run_manage/ltv_collect/", 1, request.session.get('uid')
    if request.method == 'GET':
        end_day = datetime.date.today().strftime('%Y-%m-%d')
        one_page = request.GET.get('page')
        if one_page:
            conf, day_info = get_ltv_data(phone)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            day_info.update({"number": number, "page": page})
        else:
            day_info = {"channel": "0", "start_day": end_day, "end_day": end_day, "number": number}
    else:
        dic = request.POST
        channel = dic.get('channel').encode('utf-8')  # 渠道name
        start_time = dic.get("start_time")[:10]  # 查询开始时间
        end_time = dic.get("stop_time")[:10]  # 查询结束时间

        day_info = {"start_day": start_time, "end_day": end_time, "channel": channel}
        keys = 'ltv_collect:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, day_info)

        start_day = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_day = Time.str_to_datetime(end_time, '%Y-%m-%d')

        while start_day <= end_day:
            res = LtvCollect.objects.filter(day_time=start_day).first()
            cur_day = Time.datetime_to_str(start_day, '%Y-%m-%d')
            if res:
                start_day = Time.next_days(start_day)
                continue
            else:
                one_channel = "1000"
                insert_ltv_info(cur_day, cur_day, one_channel)  # 插入数据
            start_day = Time.next_days(start_day)

        start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')
        if channel == "0":
            res_info = LtvCollect.objects.filter(day_time__range=(start_date, end_date)).values('json_data').order_by("-day_time")
        else:
            res_info = LtvCollect.objects.filter(day_time__range=(start_date, end_date), channel=channel).values('json_data')
        sorted_info = []
        for data in res_info:
            sorted_info.append(Context.json_loads(data.get("json_data")))
        paginator = Paginator(sorted_info, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        day_info.update({"page": page, "number": number})

    day_info.update({"chanel_info": chanel_info, "url_date": url_date})
    return render(request, 'run_manage/ltv_collect.html', day_info)


def insert_ltv_info(start, end, one_channel):
    """ltv数据"""
    start_day = Time.str_to_datetime(start, '%Y-%m-%d')
    end_day = Time.str_to_datetime(end, '%Y-%m-%d')

    day_info = []
    visitor_info = {"1004_10": "1004_0", "1004_11": "1004_2", "1004_0": "1004_0", "1004_2": "1004_2"}
    old_data = ChannelList.objects.all().values('channel_data').first()
    all_channel = Context.json_loads(old_data['channel_data'])  # 渠道
    del all_channel['0']
    del all_channel['1000']
    add_channel = {"1004_10": "OPPO游客", "1004_11": "OPPO广告包游客"}
    for ch_id, ch_name in add_channel.items():
        all_channel.update({ch_id: ch_name})
    while start_day <= end_day:
        channel_data = []
        fmt = Time.datetime_to_str(start_day, '%Y-%m-%d')
        if one_channel == "1000":
            for channel_id, channel_name in all_channel.items():
                if visitor_info.has_key(str(channel_id)):
                    channel = visitor_info[channel_id]
                    if channel == str(channel_id):
                        only_channel = deal_visitor_ltv(fmt, channel, 0)
                    else:
                        only_channel = deal_visitor_ltv(fmt, channel, 1)
                else:
                    only_channel = channel_ltv_info(fmt, channel_id)
                if len(only_channel) > 0:
                    only_channel.update({"channel": channel_id})
                    channel_data.append({channel_id: only_channel})

            all_info, register_list, args = {}, [], {}
            new_user_count, new_pay_total = 0, 0
            for info in channel_data:
                for channel_id, channel_info in info.items():
                    new_user_count += int(channel_info["new_user_count"])
                    new_pay_total += int(channel_info["new_pay_total"])
                    register_list.extend(channel_info["register_list"])
                    for channelKey, channelValue in channel_info.items():
                        if channelKey != 'day_time' and channelKey != 'channel' and channelKey != 'new_user_count' and channelKey != 'new_pay_total' and channelKey != "register_list":
                            if not channelKey.startswith("ltv") or not channelKey.startswith("pay_total"):
                                all_info.update({channelKey: int(all_info.get(channelKey, 0)) + int(channelValue)})
                            else:
                                continue
            if len(all_info) > 0:
                args.update({"day_time": fmt, "channel": "1000", "user_list": register_list, "new_user_count": new_user_count, "new_pay_user_total": new_pay_total})
                all_info["register_list"] = register_list
                for index in range(1, 31):
                    all_info['ltv{}'.format(index)] = get_ltv(args=args, days=index, class_name=LtvCollect)
                all_info.update({"day_time": fmt, "channel": "1000", "new_user_count": new_user_count, "new_pay_total": new_pay_total})
                channel_data.append({one_channel: all_info})
        else:
            if visitor_info.has_key(str(one_channel)):
                channel = visitor_info[one_channel]
                if str(one_channel) == channel:
                    only_channel = deal_visitor_ltv(fmt, channel, 0)
                else:
                    only_channel = deal_visitor_ltv(fmt, channel, 1)
                only_channel.update({"channel": one_channel})
            else:
                only_channel = channel_ltv_info(fmt, one_channel)
            if len(only_channel) > 0:
                channel_data.append({one_channel: only_channel})
        day_info.append({fmt: channel_data})
        start_day = Time.next_days(start_day)
    create_ltv_info(day_info)


def channel_ltv_info(fmt, channel):
    channel_info, args = {}, {}
    result = Context.RedisCache.hash_getall('stat:{}:{}'.format(channel, fmt))
    user_daily = Context.RedisCache.hget_keys('user_daily:{}:{}:*'.format(channel, fmt))
    if result and user_daily:
        new_pay_total, new_user_count = 0, 0  # 新增付费额度
        new_user_list = get_new_pay_data(fmt, channel)
        channel_info['new_user_count'] = len(new_user_list)  # 新增人数
        channel_info["register_list"] = new_user_list
        args.update({"day_time": fmt, "channel": channel, "user_list": new_user_list, "new_user_count": new_user_count, "new_pay_user_total": new_pay_total})
        for index in range(1, 31):
            # day_time, days, user_list, status=None
            channel_info['ltv{}'.format(index)] = get_ltv(args=args, days=index, class_name=LtvCollect)
            user_pay_total = day_ltv_total(index, fmt, new_user_list)
            channel_info['pay_total_{}'.format(index)] = user_pay_total
            new_pay_total += user_pay_total
        channel_info.update({"day_time": fmt, "channel": channel, "new_pay_total": new_pay_total})
    return channel_info


def deal_visitor_ltv(fmt, channel, status):
    channel_info, args = {}, {}
    result = Context.RedisCache.hash_getall('stat:{}:{}'.format(channel, fmt))
    user_daily = Context.RedisCache.hget_keys('user_daily:{}:{}:*'.format(channel, fmt))
    if result and user_daily:
        new_pay_total, new_user_count = 0, 0  # 新增付费额度
        _, new_user_list = deal_visitor_user(fmt, channel, status)
        channel_info['new_user_count'] = len(new_user_list)  # 新增人数
        channel_info['register_list'] = new_user_list
        args.update({"day_time": fmt, "channel": channel, "user_list": new_user_list, "new_user_count": new_user_count, "new_pay_user_total": new_pay_total})
        for index in range(1, 31):
            channel_info['ltv{}'.format(index)] = get_ltv(args=args, days=index, class_name=LtvCollect)
            user_pay_total = day_ltv_total(index, fmt, new_user_list)
            channel_info['pay_total_{}'.format(index)] = user_pay_total
            new_pay_total += user_pay_total
        channel_info.update({"day_time": fmt, "new_pay_total": new_pay_total})
    return channel_info


def day_ltv_total(days, fmt, user_list):
    user_total = 0
    for i in range(days-1, days):
        day_time = (Time.str_to_datetime(fmt, "%Y-%m-%d") + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        for uid in user_list:
            channel_id = Context.RedisMix.hash_get('user:{}'.format(uid), 'channelid')
            pay_total = Context.RedisCache.hash_get('user_daily:{}:{}:{}'.format(channel_id, day_time, uid),
                                                    "{}.pay.user.pay_total".format(channel_id))
            if pay_total:
                user_pay = int(pay_total)
            else:
                user_pay = 0
            user_total += user_pay
    return user_total


def get_ltv_data(phone):
    """ltv"""
    keys = 'ltv_collect:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day", "channel"])  # 筛选条件
    start_time, end_time, channel = result[0], result[1], result[2]
    def_info = {"start_day": start_time, "end_day": end_time, "channel": channel}

    start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
    end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')
    if channel == "0":
        res_info = LtvCollect.objects.filter(day_time__range=(start_date, end_date)).values('json_data').order_by("-day_time")
    else:
        res_info = LtvCollect.objects.filter(day_time__range=(start_date, end_date), channel=channel).values('json_data')

    config = []
    for data in res_info:
        config.append(Context.json_loads(data.get("json_data")))
    return config, def_info


@decorator
def hardcore_channels(request):
    chanel_list = Data_Info.get_hardcore_info()  # 渠道
    url_date, number, phone = "/run_manage/hardcore_channels/", 1, request.session.get('uid')
    if request.method == 'GET':
        end_day = datetime.date.today().strftime('%Y-%m-%d')
        one_page = request.GET.get('page')
        if one_page:
            conf, day_info = get_hardcore_data(phone)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            day_info.update({"number": number, "page": page})
        else:
            day_info = {"channel": "0", "start_day": end_day, "end_day": end_day, "number": number}
    else:
        dic = request.POST
        channel = dic.get('channel').encode('utf-8')  # 渠道name
        start_time = dic.get("start_time")[:10]  # 查询开始时间
        end_time = dic.get("stop_time")[:10]  # 查询结束时间

        day_info = {"start_day": start_time, "end_day": end_time, "channel": channel}
        keys = 'hardcore:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, day_info)

        start_day = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_day = Time.str_to_datetime(end_time, '%Y-%m-%d')

        while start_day <= end_day:
            res = Hardcore.objects.filter(day_time=start_day).first()
            cur_day = Time.datetime_to_str(start_day, '%Y-%m-%d')
            if res:
                if res.day_time == res.insert_time and cur_day != Time.current_time('%Y-%m-%d'):
                    insert_hardcore_info(cur_day, channel)  # 插入数据
                else:
                    start_day = Time.next_days(start_day)
                    continue
            else:
                insert_hardcore_info(cur_day, channel)  # 插入数据
            start_day = Time.next_days(start_day)

        start_date = Time.str_to_datetime(start_time[:10], '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_time[:10], '%Y-%m-%d')
        if channel == "0":
            res_info = Hardcore.objects.filter(day_time__range=(start_date, end_date)).values('json_data').order_by("-day_time")
        else:
            if channel == "1":
                res_info = Hardcore.objects.filter(day_time__range=(start_date, end_date), channel=channel).values('json_data')
            elif channel == "2":
                res_info = Hardcore.objects.filter(day_time__range=(start_date, end_date), channel=channel).values('json_data')
            else:
                res_info = Hardcore.objects.filter(day_time__range=(start_date, end_date), channel=channel).values('json_data')

        sorted_info = []
        for data in res_info:
            sorted_info.append(Context.json_loads(data.get("json_data")))
        paginator = Paginator(sorted_info, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        day_info.update({"page":page, "number": number})

    day_info.update({"chanel_list": chanel_list, "url_date": url_date})
    return render(request, 'run_manage/hardcore_channels.html', day_info)


def get_hardcore_data(phone):
    """硬核数据"""
    keys = 'hardcore:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day", "channel"])  # 筛选条件
    start_time, end_time, channel = result[0], result[1], result[2]
    def_info = {"start_day": start_time, "end_day": end_time, "channel": channel}

    start_date = Time.str_to_datetime(start_time[:10], '%Y-%m-%d')
    end_date = Time.str_to_datetime(end_time[:10], '%Y-%m-%d')
    if channel == "0":
        res_info = Hardcore.objects.filter(day_time__range=(start_date, end_date)).values('json_data').order_by("-day_time")
    else:
        if channel == "1":
            res_info = Hardcore.objects.filter(day_time__range=(start_date, end_date), channel=channel).values('json_data')
        elif channel == "2":
            res_info = Hardcore.objects.filter(day_time__range=(start_date, end_date), channel=channel).values('json_data')
        else:
            res_info = Hardcore.objects.filter(day_time__range=(start_date, end_date), channel=channel).values('json_data')
    config = []
    for data in res_info:
        config.append(Context.json_loads(data.get("json_data")))

    return config, def_info


def insert_hardcore_info(day_time, channel):
    channel_config = {"0":["1003_0", "1004_0","1005_0", "1007_0","1007_2","1010_0", "1011_0", "1012_0","1013_0","1014_0","1015_0","1009_0"],"1":["1003_0", "1004_0","1005_0", "1007_0","1007_2"],
                      "2":  ["1010_0", "1011_0", "1012_0","1013_0","1014_0","1015_0"],"3":["1009_0"] }
    if channel == "0":
        res_game = GameCollect.objects.filter(day_time=day_time, channel__in=channel_config["0"]).values('json_data')
        day_channel = get_hardcore_info(res_game)
    else:
        if channel == "1":
            res_game = GameCollect.objects.filter(day_time=day_time,channel__in=channel_config["1"]).values('json_data')
            day_channel = get_hardcore_info(res_game)
        elif channel == "2":
            res_game = GameCollect.objects.filter(day_time=day_time,channel__in=channel_config["2"]).values('json_data')
            day_channel = get_hardcore_info(res_game)
        else:
            res_game = GameCollect.objects.filter(day_time=day_time,channel__in=channel_config["3"]).values('json_data')
            day_channel = get_hardcore_info(res_game)
    calc_channel =[]
    del channel_config["0"]
    for day, channel_data in day_channel.items():
        for key, channel_list in channel_config.items():
            channel_count = {"channel": key, "day_time": day,"channel_list":channel_list}
            for channel_id, channel_info in channel_data.items():
                if channel_id in channel_list:
                    calc_channel.append(channel_info)
                    for channelKey, channelValue in channel_info.items():
                        if channelKey != 'day_time' and channelKey != 'channel' and channelKey != 'ltv1' and channelKey != "ltv2" and channelKey != "ltv3" and channelKey != "ltv4" and channelKey != "ltv5" and channelKey != "ltv6" and channelKey != "ltv7" \
                                and channelKey != "gross_margin" and channelKey != "gross_margin_rate" and channelKey != "ltv14" and channelKey != "ltv15" and channelKey != "ltv30" and channelKey != "ltv60" and channelKey != "ltv90" and channelKey != "ltv120" \
                                and channelKey != "pay_rate" and channelKey != "new_pay_rate" and channelKey != "register_list":
                            channel_count.update({channelKey: int(channel_count.get(channelKey, 0)) + int(channelValue)})
            if channel_count.has_key("new_user_count"):
                calc_channel.append(channel_count)

    deal_list = []
    for channel_count in calc_channel:
        c_list = channel_count.get("channel_list", channel_count["channel"])
        core_info = deal_channel_info(channel_count, c_list)
        channel_count.update(core_info)
        deal_list.append(channel_count)
    create_core_channel(deal_list)


def get_hardcore_info(res_game):
    day_channel = {}
    for game in res_game:
        game_data = Context.json_loads(game.get("json_data"))
        channel_id, day_time = game_data["channel"], game_data["day_time"]
        res_run = RunCollect.objects.filter(day_time=day_time, channel=channel_id).values('json_data').first()
        if res_run:
            run_info = Context.json_loads(res_run.get("json_data"))
            barrel_500_1, barrel_500_2, barrel_3000_1, barrel_3000_2 = run_info["barrel_500_1"], run_info["barrel_500_2"], run_info["barrel_3000_1"], run_info["barrel_3000_2"]
            game_data.update({"barrel_500_1": barrel_500_1, "barrel_500_2": barrel_500_2, "barrel_3000_1": barrel_3000_1,"barrel_3000_2": barrel_3000_2})
            if not day_channel.has_key(day_time):
                day_channel[day_time] = {}
            day_channel[day_time][channel_id] = game_data
        else:
            continue
    return day_channel


def deal_channel_info(res, channel_list):
    deal_data = {}
    user_count, day_time = res["new_user_count"], res["day_time"]
    login_1,login_2,login_3,login_4 = res.get("login_level_1",0),res.get("login_level_2",0),res.get("login_level_3",0),res.get("login_level_4",0)
    login_5, login_6, login_7 = res.get("login_level_5", 0), res.get("login_level_6", 0), res.get("login_level_7", 0)
    barrel_500_1_rate = round((0 if user_count == 0 else float(res["barrel_500_1"]) / float(user_count)), 4)
    barrel_500_2_rate = round((0 if user_count == 0 else float(res["barrel_500_2"]) / float(user_count)), 4)
    barrel_3000_1_rate = round((0 if user_count == 0 else float(res["barrel_3000_1"]) / float(user_count)), 4)
    barrel_3000_2_rate = round((0 if user_count == 0 else float(res["barrel_3000_2"]) / float(user_count)), 4)
    pay_rate = round((0 if res["login_user_count"] == 0 else float(res["pay_user_count"]) / float(res["login_user_count"])), 4)
    new_pay_rate = round((0 if user_count == 0 else float(res["new_pay_user_count"]) / float(user_count)), 4)
    login_level_1_rate = round((0 if user_count == 0 else float(login_1) / float(user_count)), 4)
    login_level_2_rate = round((0 if user_count == 0 else float(login_2) / float(user_count)), 4)
    login_level_3_rate = round((0 if user_count == 0 else float(login_3) / float(user_count)), 4)
    login_level_4_rate = round((0 if user_count == 0 else float(login_4) / float(user_count)), 4)
    login_level_5_rate = round((0 if user_count == 0 else float(login_5) / float(user_count)), 4)
    login_level_6_rate = round((0 if user_count == 0 else float(login_6) / float(user_count)), 4)
    login_level_7_rate = round((0 if user_count == 0 else float(login_7) / float(user_count)), 4)
    deal_data.update({"barrel_500_1_rate": barrel_500_1_rate, "barrel_500_2_rate": barrel_500_2_rate,
                      "barrel_3000_1_rate": barrel_3000_1_rate, "barrel_3000_2_rate": barrel_3000_2_rate,
                      "pay_rate": pay_rate, "new_pay_rate": new_pay_rate,"login_level_5_rate": login_level_5_rate,
                      "login_level_1_rate": login_level_1_rate, "login_level_2_rate": login_level_2_rate,
                      "login_level_3_rate": login_level_3_rate, "login_level_4_rate": login_level_4_rate,
                      "login_level_6_rate": login_level_6_rate, "login_level_7_rate": login_level_7_rate})
    if isinstance(channel_list, list):
        user_list = deal_pay_data(day_time, channel_list)
        ltv1, ltv2, ltv3 = get_core_ltv(day_time=day_time, days=1, user_list=user_list), get_core_ltv(day_time=day_time, days=2, user_list=user_list),get_core_ltv(day_time=day_time, days=3, user_list=user_list)
        ltv4, ltv5, ltv6 = get_core_ltv(day_time=day_time, days=4, user_list=user_list), get_core_ltv(day_time=day_time, days=5, user_list=user_list), get_core_ltv(day_time=day_time, days=6, user_list=user_list)
        ltv7, ltv14, ltv15 = get_core_ltv(day_time=day_time, days=7, user_list=user_list), get_core_ltv(day_time=day_time, days=14, user_list=user_list), get_core_ltv(day_time=day_time, days=15, user_list=user_list)
        ltv30, ltv60, ltv90 = get_core_ltv(day_time=day_time, days=30, user_list=user_list), get_core_ltv(day_time=day_time, days=60, user_list=user_list), get_core_ltv(day_time=day_time, days=90, user_list=user_list)
        ltv120 = get_core_ltv(day_time=day_time, days=120, user_list=user_list)
        deal_data.update({"ltv1":ltv1,"ltv2":ltv2,"ltv3":ltv3,"ltv4":ltv4,"ltv5":ltv5,"ltv6":ltv6,"ltv7":ltv7,"ltv14":ltv14,"ltv15":ltv15,"ltv30":ltv30,"ltv60": ltv60, "ltv90": ltv90, "ltv120": ltv120})
    return deal_data


def get_core_ltv(day_time, days, user_list, status=None):
    user_count = len(user_list)
    user_total = 0
    for i in range(0, days):
        day_total = 0
        fmt = (Time.str_to_datetime(day_time, "%Y-%m-%d") + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        for uid in user_list:
            channel_id = Context.RedisMix.hash_get('user:{}'.format(uid), 'channelid')
            pay_total = Context.RedisCache.hash_get('user_daily:{}:{}:{}'.format(channel_id, fmt, uid),"{}.pay.user.pay_total".format(channel_id))
            if pay_total:
                user_pay = int(pay_total)
            else:
                user_pay = 0
            day_total += user_pay
        if status:
            user_total = day_total
        else:
            user_total += day_total
    if user_count == 0:
        ltv = 0.0
    else:
        ltv = round(user_total / float(user_count), 2)
    return ltv


def deal_pay_data(day_time, channel_list):
    user_list = []
    start_stamp = Time.str_to_timestamp(day_time + " 00:00:00")
    end_stamp = Time.str_to_timestamp(day_time + " 23:59:59")

    user_info = Context.RedisCache.hget_keys('user_daily:*:{}:*'.format(day_time))
    for user_str in user_info:
        user_id = int(user_str.split(':')[3])
        channel = str(user_str.split(':')[1])
        if user_id > 1000000 and channel in channel_list:
            channel_id = Context.RedisMix.hash_get('user:{}'.format(user_id), 'channelid')
            create_stamp = Time.str_to_timestamp(str(Context.RedisMix.hash_get('user:{}'.format(user_id), 'createTime'))[:19])
            online = Context.RedisCache.hash_get('user_daily:{}:{}:{}'.format(channel_id, day_time, user_id),"login.times")
            if online and create_stamp >= start_stamp and create_stamp <= end_stamp and str(user_id) not in user_list:
                user_list.append(user_id)
            else:
                continue
        else:
            continue
    return user_list


def insert_redis_collect(phone, start_time, end_time, channel, data_type):
    game_in_early_warning()
    if channel == "0":
        def_channel = "1000"
    else:
        def_channel = channel
    if data_type == 1:
        insert_channel_cost(phone, start_time, end_time)
        url = '/v2/shell/gm/game_data_summary'
        data_name = "game_collect"
    else:
        url = '/v2/shell/gm/run_data_summary'
        data_name = "run_collect"
    context = {"phone": phone, "start": start_time, "end": end_time, "channel": def_channel}
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.text)
    print("-------------ttbn", config)
    if "info" not in config:
        return 0
    else:
        result = config["info"]
        if data_type == 1:
            channel_info = get_game_response_data(result)
        else:
            channel_info = get_run_response_data(result)
        for info in channel_info:
            day_time = info.get("day_time", 0)
            chanel_id = info.get("channel", 0)
            Context.RedisCache.hash_mset('{}:{}:{}:{}'.format(data_name, phone, day_time, chanel_id), info)


def game_in_early_warning():
    """个人产出预警"""
    url = "/v2/shell/gm/in_early_warning"
    context = {"phone": "system"}
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.text)
    print("------game_in-------", config)


def insert_mysql_collect(start_time, end_time, data_type):
    if data_type == 1:
        insert_channel_cost("system", start_time, end_time)  # 商城成本
        result = data_summarizing(start_time, end_time, "1000")  # 数据运算
        channel_info = get_game_response_data(result)
        sorted_info = sorted(channel_info, key=lambda x: Time.str_to_timestamp(x["day_time"], '%Y-%m-%d'), reverse=True)
        create_data_collect(sorted_info, GameCollect)
    else:
        result = run_data(start_time, end_time, "1000")  # 数据运算
        channel_info = get_run_response_data(result)
        sorted_info = sorted(channel_info, key=lambda x: Time.str_to_timestamp(x["day_time"], '%Y-%m-%d'), reverse=True)
        create_data_collect(sorted_info, RunCollect)


def get_game_response_data(result):
    channel_info = []
    for info in result:
        for day_time, channel_list in info.items():
            for channel_data in channel_list:
                for channelId, channelValue in channel_data.items():
                    channelValue.update({"channel": channelId})
                    channelValue.update({"day_time": day_time})
                    pay_active = int(float(channelValue.get("daily.pay.active.player", 0)))
                    # 统计当天的商城成本
                    res_cost = ChannelCost.objects.filter(query_day=day_time).values("json_data").first()
                    if res_cost:
                        info = Context.json_loads(res_cost.get("json_data"))
                        cost = info.get("{}".format(channelId), 0)
                    else:
                        cost = 0

                    channelValue['exchange_cost'] = cost  # 商城成本
                    pay_total = int(float(channelValue.get("pay_user_total", 0)))
                    pay_user = int(float(channelValue.get("pay_user_count", 0)))
                    activity_user = int(float(channelValue.get("login_user_count", 0)))

                    ARPU = round((0 if activity_user == 0 else (pay_total / float(activity_user))), 2)
                    ARPPU = round((0 if pay_user == 0 else (pay_total / float(pay_user))), 2)
                    channelValue.update({"ARPU": ARPU, "ARPPU": ARPPU, "active_pay_player": pay_active})

                    hand_free, shop_cost, gross_margin, margin_rate = D_data_deal_with(channelValue)
                    pay_rate = D_pay_rate(channelValue)
                    new_pay_rate = D_new_pay_rate(channelValue)

                    channelValue.update({'hand_free': hand_free, 'gross_margin': gross_margin})  # 毛利
                    channelValue.update({'gross_margin_rate': margin_rate, 'pay_rate': pay_rate, 'new_pay_rate': new_pay_rate})  # 毛利率 付费率 新增付费率
                    channel_info.append(channelValue)
    return channel_info


def get_run_response_data(result):
    channel_info = []
    for info in result:
        for day_time, channel_list in info.items():
            for channel_data in channel_list:
                for channelId, channelValue in channel_data.items():
                    channelValue.update({"channel": channelId})
                    channelValue.update({"day_time": day_time})
                    channel_info.append(channelValue)
    return channel_info


def get_day_collect(phone, day_info, class_value, data_type):
    start_time, end_time, channel, day_list = day_info["start_day"], day_info["end_day"], day_info["channel"], day_info["day_list"]
    sort_info, collect_list, number = [], [], 1
    if data_type == 1:
        data_name = "game_collect"
    else:
        data_name = "run_collect"

    if channel == "0":
        res_info = class_value.objects.filter(day_time__range=(start_time, end_time)).values('json_data').order_by("-day_time")
        for every_day in day_list:
            day_order = Context.RedisCache.hget_keys('{}:{}:{}:*'.format(data_name, "system", every_day))
            for key in day_order:
                ret = Context.RedisCache.hash_getall(key)
                collect_list.append(ret)
    else:
        res_info = class_value.objects.filter(day_time__range=(start_time, end_time), channel=channel).values('json_data').order_by("-day_time")
        for every_day in day_list:
            day_order = Context.RedisCache.hget_keys('{}:{}:{}:{}'.format(data_name, "system", every_day, channel))
            for key in day_order:
                ret = Context.RedisCache.hash_getall(key)
                collect_list.append(ret)

    all_new_user = 0
    for info in res_info:
        new_data = {}
        data = json.loads(info.get("json_data"))
        all_new_user += int(data.get("new_user_count", 0))
        new_data.update({"all_new_user": all_new_user})
        new_data.update(data)
        sort_info.append(new_data)

    if sort_info:
        sort_info.extend(collect_list)
        sorted_info = sorted(sort_info, key=lambda x: Time.str_to_timestamp(x["day_time"], '%Y-%m-%d'), reverse=True)
    else:
        sorted_info = sorted(collect_list, key=lambda x: Time.str_to_timestamp(x["day_time"], '%Y-%m-%d'), reverse=True)
    return sorted_info


def get_data_collect(phone, class_value, data_type):
    """获取数据汇总"""
    if data_type == 1:
        data_name = "game_collect"
    else:
        data_name = "run_collect"
    keys = '{}:{}:{}'.format(data_name, phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day", "channel", "day_list"])  # 筛选条件
    start_time, end_time, channel, day_list = result[0], result[1], result[2], eval(result[3])
    def_info = {"start_day": start_time, "end_day": end_time, "channel": channel, "day_list": day_list}
    config = get_day_collect(phone, def_info, class_value, data_type)

    return config, def_info


def data_summarizing(start, end, one_channel):
    """游戏数据"""
    start_day = Time.str_to_datetime(start, '%Y-%m-%d')
    end_day = Time.str_to_datetime(end, '%Y-%m-%d')

    day_info = []
    visitor_info = {"1004_10": "1004_0", "1004_11": "1004_2", "1004_0": "1004_0", "1004_2": "1004_2"}
    old_data = ChannelList.objects.all().values('channel_data').first()
    all_channel = Context.json_loads(old_data['channel_data'])  # 渠道
    del all_channel['0']
    del all_channel['1000']
    add_channel = {"1004_10": "OPPO游客", "1004_11": "OPPO广告包游客"}
    for ch_id, ch_name in add_channel.items():
        all_channel.update({ch_id: ch_name})
    while start_day <= end_day:
        channel_data = []
        fmt = Time.datetime_to_str(start_day, '%Y-%m-%d')
        if one_channel == "1000":
            for channel_id, channel_name in all_channel.items():
                if visitor_info.has_key(str(channel_id)):
                    channel = visitor_info[channel_id]
                    if channel == str(channel_id):
                        only_channel = deal_visitor_channel(fmt, channel, 0)
                    else:
                        only_channel = deal_visitor_channel(fmt, channel, 1)
                else:
                    only_channel = get_each_channel_data(fmt, channel_id)

                if len(only_channel) > 1:
                    channel_data.append({channel_id: only_channel})

            all_info, register_list, args = {}, [], {}
            for info in channel_data:
                for channel_id, channel_info in info.items():
                    register_list.extend(channel_info["register_list"])
                    for channelKey, channelValue in channel_info.items():
                        if channelKey != 'day_time' and channelKey != 'channel' and channelKey != 'ltv1' and channelKey != "ltv2" and channelKey != "ltv3" and channelKey != "ltv4" and channelKey != "ltv5" \
                                and channelKey != "ltv6" and channelKey != "ltv7" and channelKey != "ltv14" and channelKey != "ltv15" and channelKey != "ltv30" and channelKey != "ltv60" and channelKey != "ltv90" \
                                and channelKey != "ltv120" and channelKey != "register_list":
                            all_info.update({channelKey: int(all_info.get(channelKey, 0)) + int(channelValue)})

            new_user_count, new_pay_user_total, all_info["register_list"] = register_list, int(all_info["new_user_count"]), int(all_info["new_user_count"])
            args.update({"day_time": fmt, "channel": one_channel, "user_list": register_list, "new_user_count": new_user_count, "new_pay_user_total": new_pay_user_total})

            ltv1, ltv2, ltv3 = get_ltv(args=args, days=1, class_name=GameCollect), get_ltv(args=args, days=2, class_name=GameCollect), get_ltv(args=args, days=3, class_name=GameCollect)
            ltv4, ltv5, ltv6 = get_ltv(args=args, days=4, class_name=GameCollect), get_ltv(args=args, days=5, class_name=GameCollect), get_ltv(args=args, days=6, class_name=GameCollect)
            ltv7, ltv14, ltv15 = get_ltv(args=args, days=7, class_name=GameCollect), get_ltv(args=args, days=14, class_name=GameCollect), get_ltv(args=args, days=15, class_name=GameCollect)
            ltv30, ltv60, ltv90 = get_ltv(args=args, days=30, class_name=GameCollect), get_ltv(args=args, days=60, class_name=GameCollect), get_ltv(args=args, days=90, class_name=GameCollect)
            ltv120 = get_ltv(args=args, days=120, class_name=GameCollect)

            all_info['ltv1'], all_info['ltv2'], all_info['ltv3'] = ltv1, ltv2, ltv3
            all_info['ltv4'], all_info['ltv5'], all_info['ltv6'], all_info['ltv7'] = ltv4, ltv5, ltv6, ltv7
            all_info['ltv14'], all_info['ltv15'], all_info['ltv30'], all_info['ltv60'] = ltv14,ltv15, ltv30, ltv60
            all_info['ltv90'], all_info['ltv120'] = ltv90, ltv120
            channel_data.append({one_channel: all_info})
        else:
            if visitor_info.has_key(str(one_channel)):
                channel = visitor_info[one_channel]
                if str(one_channel) == channel:
                    only_channel = deal_visitor_channel(fmt, channel, 0)
                else:
                    only_channel = deal_visitor_channel(fmt, channel, 1)
            else:
                only_channel = get_each_channel_data(fmt, one_channel)
            if len(only_channel) > 0:
                channel_data.append({one_channel: only_channel})
        day_info.append({fmt: channel_data})
        start_day = Time.next_days(start_day)
    return day_info


def run_data(start, end, one_channel):
    """运营数据"""
    start_day = Time.str_to_datetime(start, '%Y-%m-%d')
    end_day = Time.str_to_datetime(end, '%Y-%m-%d')

    day_info = []
    old_data = ChannelList.objects.all().values('channel_data').first()
    all_channel = Context.json_loads(old_data['channel_data'])  # 渠道
    del all_channel['0']
    del all_channel['1000']
    while start_day <= end_day:
        channel_data = []
        fmt = Time.datetime_to_str(start_day, '%Y-%m-%d')
        if one_channel == "1000":
            for channel_id, channel_name in all_channel.items():
                only_channel = get_run_channel_info(fmt, channel_id)
                if len(only_channel) > 0:
                    channel_data.append({channel_id: only_channel})

            if len(channel_data) > 0:
                all_info, register_list, args = {}, [], {}
                for info in channel_data:
                    for channel_id, channel_info in info.items():
                        register_list.extend(channel_info["register_list"])
                        for channelKey, channelValue in channel_info.items():
                            if channelKey != 'day_time' and channelKey != 'channel' and channelKey != 'dtv1' and channelKey != "dtv2" and channelKey != "dtv3" and channelKey != "dtv4" and channelKey != "dtv5" and channelKey != "dtv7" \
                                    and channelKey != "dtv15" and channelKey != "dtv30" and channelKey != "dtv60" and channelKey != "dtv90" and channelKey != "dtv120" and channelKey != "login_rate_1" and channelKey != "login_rate_2" \
                                    and channelKey != "login_rate_3" and channelKey != "login_rate_4" and channelKey != "ROI" and channelKey != "ARPPU" and channelKey != "dtv6" and channelKey != "dtv14"\
                                    and channelKey != "ARPDAU" and channelKey != "day_wastage_rate" and channelKey != "week_wastage_rate" and channelKey != "month_wastage_rate" and channelKey != "register_list":
                                all_info.update({channelKey: int(all_info.get(channelKey, 0)) + int(channelValue)})

                new_user_count, new_pay_user_total = int(all_info["new_user_count"]), int(all_info["new_pay_user_total"])
                args.update({"day_time": fmt, "channel": one_channel, "user_list": register_list, "new_user_count": new_user_count, "new_pay_user_total": new_pay_user_total})
                dtv1, dtv2 = get_ltv(args=args, days=1, class_name=RunCollect, status="day"), get_ltv(args=args, days=2, class_name=RunCollect, status="day")
                dtv3, dtv4 = get_ltv(args=args, days=3, class_name=RunCollect, status="day"), get_ltv(args=args, days=4, class_name=RunCollect, status="day")
                dtv5, dtv6 = get_ltv(args=args, days=5, class_name=RunCollect, status="day"), get_ltv(args=args, days=6, class_name=RunCollect, status="day")
                dtv7, dtv14 = get_ltv(args=args, days=7, class_name=RunCollect, status="day"), get_ltv(args=args, days=14, class_name=RunCollect, status="day")
                dtv15, dtv30 = get_ltv(args=args, days=15, class_name=RunCollect, status="day"), get_ltv(args=args, days=30, class_name=RunCollect, status="day")
                dtv60, dtv90 = get_ltv(args=args, days=60, class_name=RunCollect, status="day"), get_ltv(args=args, days=90, class_name=RunCollect, status="day")
                dtv120 = get_ltv(args=args, days=120, class_name=RunCollect, status="day")

                all_info['dtv1'], all_info['dtv2'], all_info['dtv3'] = dtv1, dtv2, dtv3
                all_info['dtv4'], all_info['dtv5'], all_info['dtv6'], all_info['dtv7'] = dtv4, dtv5, dtv6, dtv7
                all_info['dtv14'], all_info['dtv15'], all_info['dtv30'], all_info['dtv60'] = dtv14, dtv15, dtv30, dtv60
                all_info['dtv90'], all_info['dtv120'] = dtv90, dtv120
                new_user_count, DAU, WAU, MAU = all_info["new_user_count"], all_info["DAU"], all_info["WAU"], all_info["MAU"]
                login_level_1, login_level_2, login_level_3, login_level_4, login_level_5 = int(all_info["login_level_1"]), int(all_info["login_level_2"]), int(all_info["login_level_3"]), int(all_info["login_level_4"]), int(all_info["login_level_5"])
                # 次日留存率、3日留存率、7日留存率、14日留存率、30日留存率
                all_info['login_rate_1'] = round((0 if new_user_count == 0 else login_level_1 / float(new_user_count)), 2)
                all_info['login_rate_2'] = round((0 if new_user_count == 0 else login_level_2 / float(new_user_count)), 2)
                all_info['login_rate_3'] = round((0 if new_user_count == 0 else login_level_3 / float(new_user_count)), 2)
                all_info['login_rate_4'] = round((0 if new_user_count == 0 else login_level_4 / float(new_user_count)), 2)
                all_info['login_rate_5'] = round((0 if new_user_count == 0 else login_level_5 / float(new_user_count)), 2)
                active_count, pay_user_total = all_info["active_user_count"], all_info["pay_user_total"]
                register, pay_user = all_info["register_count"], all_info["pay_user_count"]

                day_time = datetime.datetime.strptime(Time.current_time('%Y-%m-%d'), "%Y-%m-%d")
                now_time = datetime.datetime.strptime(fmt, "%Y-%m-%d")
                days = (day_time - now_time).days

                pay_profit = deal_roi_info(fmt, days, register_list)

                all_info['ROI'] = round((0 if register == 0 else (pay_profit / float((register * 45)))), 2)
                #  ARPDAU = 每日总收入/APA(每日活跃用户数)
                all_info['ARPDAU'] = round((0 if active_count == 0 else (pay_user_total / float(active_count))), 2)

                # 日流失、周流失、月流失
                day_wastage, week_wastage, month_wastage = get_wastage_user(fmt, 1), get_wastage_user(fmt, 7), get_wastage_user(fmt, 30)
                all_info['day_wastage_rate'] = round((0 if DAU == 0 else (day_wastage / float(DAU))), 2)
                all_info['week_wastage_rate'] = round((0 if WAU == 0 else (week_wastage / float(WAU))), 2)
                all_info['month_wastage_rate'] = round((0 if MAU == 0 else (month_wastage / float(MAU))), 2)

                all_info["register_list"] = register_list
                channel_data.append({one_channel: all_info})
        else:
            only_channel = get_run_channel_info(fmt, one_channel)
            if len(only_channel) > 0:
                channel_data.append({one_channel: only_channel})
        day_info.append({fmt: channel_data})
        start_day = Time.next_days(start_day)
    return day_info


def get_each_channel_data(fmt, channel):
    channel_info, args = {}, {}
    result = Context.RedisCache.hash_getall('stat:{}:{}'.format(channel, fmt))
    user_daily = Context.RedisCache.hget_keys('user_daily:{}:{}:*'.format(channel, fmt))
    if result and user_daily:  # 没有数据
        channel_info["sdk_pay_total"] = result.get('{}.sdk_pay.user.pay_total'.format(channel), 0)
        channel_info["weixin_pay_total"] = result.get('{}.weixin_pay.user.pay_total'.format(channel), 0)
        channel_info["ali_pay_total"] = result.get('{}.ali_pay.user.pay_total'.format(channel), 0)
        channel_info["cdkey_pay_total"] = result.get('{}.cdkey_pay.user.pay_total'.format(channel), 0)

        channel_info["daily.pay.active.player"] = result.get('daily.pay.active.player', 0)  # 当日付费活跃
        channel_info["new_user_count"] = result.get('{}.new.user.count'.format(channel), 0)  # 新增人数
        channel_info['pay_user_count'] = result.get('{}.pay.user.count'.format(channel), 0)  # 付费人数
        channel_info['user_pay_times'] = result.get('{}.user.pay.times'.format(channel), 0)  # 付费次数
        channel_info['pay_user_total'] = result.get('{}.pay.user.pay_total'.format(channel), 0)  # 付费额度

        activity_user, register_list = everyday_user_info(fmt, channel)  # 当日活跃用户

        channel_info["login_user_count"] = len(activity_user)  # 活跃总数
        channel_info["total_new_user"] = total_new_user(fmt, channel)  # 累计新增

        new_pay_user_count, new_pay_user_times, new_pay_user_total = 0, 0, 0
        for uid in register_list:
            channel_id = Context.RedisMix.hash_get('user:{}'.format(uid), 'channelid')
            pay_total = Context.RedisCache.hash_get('user_daily:{}:{}:{}'.format(channel_id, fmt, uid),"{}.pay.user.pay_total".format(channel_id))
            user_pay = (int(pay_total) if pay_total else 0)
            new_pay_user_total += user_pay

            count_number = Context.RedisCache.hash_get('user_daily:{}:{}:{}'.format(channel_id, fmt, uid),"{}.pay.user.count".format(channel_id))
            user_count = (int(count_number) if count_number else 0)
            new_pay_user_count += user_count

            times_number = Context.RedisCache.hash_get('user_daily:{}:{}:{}'.format(channel_id, fmt, uid),"{}.user.pay.times".format(channel_id))
            pay_times = (int(times_number) if times_number else 0)
            new_pay_user_times += pay_times

        channel_info['new_pay_user_count'] = new_pay_user_count  # 新增付费人数
        channel_info['new_pay_user_times'] = new_pay_user_times  # 新增付费总次数
        channel_info['new_pay_user_total'] = new_pay_user_total  # 新增付费总额度

        args.update({"day_time": fmt, "channel": channel, "user_list": register_list, "new_user_count": int(channel_info["new_user_count"]), "new_pay_user_total": new_pay_user_total})
        login_level_1, login_level_2, login_level_3, login_level_4, login_level_5, login_level_6, login_level_7 = get_login_level(channel, fmt, register_list)

        ltv1, ltv2, ltv3 = get_ltv(args=args, days=1, class_name=GameCollect), get_ltv(args=args, days=2, class_name=GameCollect), get_ltv(args=args, days=3, class_name=GameCollect)
        ltv4, ltv5, ltv6, ltv7 = get_ltv(args=args, days=4, class_name=GameCollect), get_ltv(args=args, days=5, class_name=GameCollect), get_ltv(args=args, days=6, class_name=GameCollect), get_ltv(args=args, days=7, class_name=GameCollect)
        ltv14, ltv15, ltv30, ltv60 = get_ltv(args=args, days=14, class_name=GameCollect), get_ltv(args=args, days=15, class_name=GameCollect), get_ltv(args=args, days=30, class_name=GameCollect), get_ltv(args=args, days=60, class_name=GameCollect)
        ltv90, ltv120 = get_ltv(args=args, days=90, class_name=GameCollect), get_ltv(args=args, days=120, class_name=GameCollect)

        # 新增次留、新增三留、新增七留
        channel_info['login_level_1'], channel_info['login_level_2'], channel_info['login_level_3'] = login_level_1, login_level_2,login_level_3
        # 新增十四留、新增三十留、新增六十留
        channel_info['login_level_4'], channel_info['login_level_5'], channel_info['login_level_6'] = login_level_4, login_level_5, login_level_6
        # 新增九十留
        channel_info['login_level_7'] = login_level_7

        channel_info['ltv1'], channel_info['ltv2'], channel_info['ltv3'] = ltv1, ltv2, ltv3
        channel_info['ltv4'], channel_info['ltv5'], channel_info['ltv6'], channel_info['ltv7'] = ltv4, ltv5, ltv6, ltv7
        channel_info['ltv14'], channel_info['ltv15'], channel_info['ltv30'], channel_info['ltv60'] = ltv14, ltv15, ltv30, ltv60
        channel_info['ltv90'], channel_info['ltv120'] = ltv90, ltv120
        channel_info['register_list'] = register_list
    return channel_info


def deal_visitor_channel(fmt, channel_id, status):
    # 新增付费人数  新增付费总次数  新增付费总额度
    channel_info = {}
    channel_info['new_pay_user_count'], channel_info['new_pay_user_times'], channel_info['new_pay_user_total'] = 0, 0, 0
    channel_info["sdk_pay_total"], channel_info["weixin_pay_total"], channel_info["ali_pay_total"], channel_info["cdkey_pay_total"] = 0, 0, 0, 0
    # 当日付费活跃  新增人数  付费人数  付费次数  付费额度
    channel_info["daily.pay.active.player"], channel_info["new_user_count"], channel_info['pay_user_count'] = 0, 0, 0
    channel_info['user_pay_times'], channel_info['pay_user_total'] = 0, 0
    activity_list, visitor_list = deal_visitor_user(fmt, channel_id, status)

    for uid in activity_list:
        channel = Context.RedisMix.hash_get('user:{}'.format(uid), 'channelid')
        daily_key = "user_daily:{}:{}:{}".format(channel, fmt, uid)
        channel_info['sdk_pay_total'] += Tool.to_int(Context.RedisCache.hash_get(daily_key, "{}.sdk_pay.user.pay_total".format(channel)), 0)
        channel_info['weixin_pay_total'] += Tool.to_int(Context.RedisCache.hash_get(daily_key, "{}.weixin_pay.user.pay_total".format(channel)), 0)
        channel_info['ali_pay_total'] += Tool.to_int(Context.RedisCache.hash_get(daily_key, "{}.ali_pay.user.pay_total".format(channel)), 0)
        channel_info['cdkey_pay_total'] += Tool.to_int(Context.RedisCache.hash_get(daily_key, "{}.cdkey_pay.user.pay_total".format(channel)), 0)
        channel_info['daily.pay.active.player'] += Tool.to_int(Context.RedisCache.hash_get(daily_key, "daily.pay.active.player"), 0)
        channel_info['pay_user_count'] += Tool.to_int(Context.RedisCache.hash_get(daily_key, "{}.pay.user.count".format(channel)), 0)
        channel_info['user_pay_times'] += Tool.to_int(Context.RedisCache.hash_get(daily_key, "{}.user.pay.times".format(channel)), 0)
        channel_info['pay_user_total'] += Tool.to_int(Context.RedisCache.hash_get(daily_key, "{}.pay.user.pay_total".format(channel)), 0)

    for uid in visitor_list:
        channel = Context.RedisMix.hash_get('user:{}'.format(uid), 'channelid')
        daily_key = "user_daily:{}:{}:{}".format(channel, fmt, uid)
        channel_info['new_pay_user_total'] += Tool.to_int(Context.RedisCache.hash_get(daily_key, "{}.pay.user.pay_total".format(channel)), 0)
        channel_info['new_pay_user_count'] += Tool.to_int(Context.RedisCache.hash_get(daily_key, "{}.pay.user.count".format(channel)), 0)
        channel_info['new_pay_user_times'] += Tool.to_int(Context.RedisCache.hash_get(daily_key, "{}.user.pay.times".format(channel)), 0)

    channel_info["new_user_count"] = len(visitor_list)  # 新增人数
    channel_info["login_user_count"] = len(activity_list)  # 活跃总数
    channel_info["total_new_user"] = visitor_new_user(fmt, channel_id, status)  # 累计新增

    login_level_1, login_level_2, login_level_3, login_level_4, login_level_5, login_level_6, login_level_7 = get_visitor_level(channel_id, fmt, status)

    ltv1, ltv2, ltv3 = get_visitor_ltv(day_time=fmt, days=1, user_list=visitor_list), get_visitor_ltv(day_time=fmt, days=2, user_list=visitor_list), get_visitor_ltv(day_time=fmt, days=3, user_list=visitor_list)
    ltv4, ltv5, ltv6 = get_visitor_ltv(day_time=fmt, days=4, user_list=visitor_list), get_visitor_ltv(day_time=fmt, days=5, user_list=visitor_list), get_visitor_ltv(day_time=fmt, days=6, user_list=visitor_list)
    ltv7, ltv14, ltv15 = get_visitor_ltv(day_time=fmt, days=7, user_list=visitor_list), get_visitor_ltv(day_time=fmt, days=14, user_list=visitor_list), get_visitor_ltv(day_time=fmt, days=15, user_list=visitor_list)
    ltv30, ltv60, ltv90 = get_visitor_ltv(day_time=fmt, days=30, user_list=visitor_list), get_visitor_ltv(day_time=fmt, days=60, user_list=visitor_list), get_visitor_ltv(day_time=fmt, days=90, user_list=visitor_list)
    ltv120 = get_visitor_ltv(day_time=fmt, days=120, user_list=visitor_list)
    # 新增次留、新增三留、新增七留
    channel_info['login_level_1'], channel_info['login_level_2'], channel_info['login_level_3'] = login_level_1, login_level_2, login_level_3
    # 新增十四留、新增三十留、新增六十留
    channel_info['login_level_4'], channel_info['login_level_5'], channel_info['login_level_6'] = login_level_4, login_level_5, login_level_6
    # 新增九十留
    channel_info['login_level_7'] = login_level_7

    channel_info['ltv1'], channel_info['ltv2'], channel_info['ltv3'] = ltv1, ltv2, ltv3
    channel_info['ltv4'], channel_info['ltv5'], channel_info['ltv6'],  = ltv4, ltv5, ltv6
    channel_info['ltv7'], channel_info['ltv14'], channel_info['ltv15'] = ltv7, ltv14, ltv15
    channel_info['ltv30'], channel_info['ltv60'], channel_info['ltv90'] = ltv30, ltv60, ltv90
    channel_info['ltv120'] = ltv120

    channel_info["register_list"] = visitor_list
    return channel_info


def visitor_new_user(day_time, channel, status):
    new_user_count = 0
    start_date = Time.str_to_datetime("2020-04-30", '%Y-%m-%d')
    end_date = Time.str_to_datetime(day_time, '%Y-%m-%d')
    while start_date <= end_date:
        fmt = Time.datetime_to_str(start_date, '%Y-%m-%d')
        activity_list, visitor_list = deal_visitor_user(fmt, channel, status)
        new_user_count += len(visitor_list)
        start_date = Time.next_days(start_date)
    return new_user_count


def deal_visitor_user(day_time, channel, status):
    guid = status
    visitor_list, activity_list = [], []
    start_stamp = Time.str_to_timestamp(day_time + " 00:00:00")
    end_stamp = Time.str_to_timestamp(day_time + " 23:59:59")

    user_info = Context.RedisCache.hget_keys('user_daily:{}:{}:*'.format(channel, day_time))
    for user_str in user_info:
        user_id = int(user_str.split(':')[3])
        if user_id > 1000000:
            guid_create = Tool.to_int(Context.RedisMix.hash_get('user:{}'.format(user_id), 'guidCreate'), 0)
            create_stamp = Time.str_to_timestamp(str(Context.RedisMix.hash_get('user:{}'.format(user_id), 'createTime'))[:19])
            if guid_create == guid and user_id not in activity_list:
                activity_list.append(user_id)
                if create_stamp >= start_stamp and create_stamp <= end_stamp:
                    visitor_list.append(user_id)
            else:
                continue
        else:
            continue
    return activity_list, visitor_list


def get_run_channel_info(fmt, channel):
    channel_info, args = {}, {}
    result = Context.RedisCache.hash_getall('stat:{}:{}'.format(channel, fmt))
    user_daily = Context.RedisCache.hget_keys('user_daily:{}:{}:*'.format(channel, fmt))
    if result and user_daily:  # 没有数据
        channel_info['user_pay_times'] = result.get('{}.user.pay.times'.format(channel), 0)  # 付费次数
        new_user_count = result.get('{}.new.user.count'.format(channel), 0)  # 新增人数
        channel_info["new_user_count"] = new_user_count
        pay_user_count, all_pay_total, new_pay_user_total = 0, 0, 0
        activity_user, register_list = everyday_user_info(fmt, channel)  # 当日活跃用户
        register_count = len(register_list)  # 当日注册用户

        for uid in register_list:
            channel_id = Context.RedisMix.hash_get('user:{}'.format(uid), 'channelid')
            pay_total = Context.RedisCache.hash_get('user_daily:{}:{}:{}'.format(channel_id, fmt, uid),"{}.pay.user.pay_total".format(channel_id))
            if pay_total:
                new_pay_total = int(pay_total)
            else:
                new_pay_total = 0
            new_pay_user_total += new_pay_total

        for uid in activity_user:
            channel_id = Context.RedisMix.hash_get('user:{}'.format(uid), 'channelid')
            pay_total = Context.RedisCache.hash_get('user_daily:{}:{}:{}'.format(channel_id, fmt, uid),"{}.pay.user.pay_total".format(channel_id))
            if pay_total:
                user_pay_total = int(pay_total)
                pay_user_count += 1
            else:
                user_pay_total = 0
            all_pay_total += user_pay_total
        active_user_count = len(activity_user)
        channel_info['pay_user_count'] = pay_user_count  # 付费用户数
        channel_info['active_user_count'] = active_user_count  # 活跃用户数
        channel_info['pay_user_total'] = all_pay_total  # 付费额度
        channel_info['register_count'] = register_count  # 当天注册人数
        channel_info['new_pay_user_total'] = new_pay_user_total  # 新增付费额度

        day_time = datetime.datetime.strptime(Time.current_time('%Y-%m-%d'), "%Y-%m-%d")
        now_time = datetime.datetime.strptime(fmt, "%Y-%m-%d")
        days = (day_time - now_time).days
        pay_profit = deal_roi_info(fmt, days, register_list)
        channel_info['ROI'] = round((0 if register_count == 0 else (pay_profit / float(register_count * 45))),2)
        #  ARPPU = 每日总收入 / APA(每日付费用户数)
        channel_info['ARPPU'] = round((0 if pay_user_count == 0 else all_pay_total / float(pay_user_count)), 2)
        #  ARPDAU = 每日总收入/APA(每日活跃用户数)
        channel_info['ARPDAU'] = round((0 if active_user_count == 0 else all_pay_total / float(active_user_count)), 2)

        args.update({"day_time": fmt, "channel": channel, "user_list": register_list, "new_user_count": new_user_count, "new_pay_user_total": all_pay_total})

        login_level_1, login_level_2, login_level_3, login_level_4, login_level_5, login_level_6, login_level_7 = get_login_level(channel, fmt, register_list)

        dtv1, dtv2 = get_ltv(args=args, days=1, class_name=RunCollect, status="day"), get_ltv(args=args, days=2, class_name=RunCollect, status="day")
        dtv3, dtv4 = get_ltv(args=args, days=3, class_name=RunCollect, status="day"), get_ltv(args=args, days=4, class_name=RunCollect, status="day")
        dtv5, dtv6 = get_ltv(args=args, days=5, class_name=RunCollect, status="day"), get_ltv(args=args, days=6, class_name=RunCollect, status="day")
        dtv7, dtv14 = get_ltv(args=args, days=7, class_name=RunCollect, status="day"), get_ltv(args=args, days=14, class_name=RunCollect, status="day")
        dtv15, dtv30 = get_ltv(args=args, days=15, class_name=RunCollect, status="day"), get_ltv(args=args, days=30, class_name=RunCollect, status="day")
        dtv60, dtv90 = get_ltv(args=args, days=60, class_name=RunCollect, status="day"), get_ltv(args=args, days=90, class_name=RunCollect, status="day")
        dtv120 = get_ltv(args=args, days=120, class_name=RunCollect, status="day")

        channel_info['login_level_1'], channel_info['login_level_2'], channel_info['login_level_3'], channel_info['login_level_4'], channel_info['login_level_5'] = login_level_1, login_level_2, login_level_3, login_level_4, login_level_5
        barrel_500_1, barrel_500_2, barrel_3000_1, barrel_3000_2 = get_barrel_level(channel, fmt)

        # 500炮倍以下、500炮倍以上、3000炮倍以下、3000炮倍以上
        channel_info['barrel_500_1'], channel_info['barrel_500_2'], channel_info['barrel_3000_1'], channel_info['barrel_3000_2'] = barrel_500_1, barrel_500_2, barrel_3000_1, barrel_3000_2

        # 次日留存率、3日留存率、7日留存率、14日留存率、30日留存率、60日留存率
        channel_info['login_rate_1'] = round((0 if new_user_count == 0 else login_level_1 / float(new_user_count)), 2)
        channel_info['login_rate_2'] = round((0 if new_user_count == 0 else login_level_2 / float(new_user_count)), 2)
        channel_info['login_rate_3'] = round((0 if new_user_count == 0 else login_level_3 / float(new_user_count)), 2)
        channel_info['login_rate_4'] = round((0 if new_user_count == 0 else login_level_4 / float(new_user_count)), 2)
        channel_info['login_rate_5'] = round((0 if new_user_count == 0 else login_level_5 / float(new_user_count)), 2)
        channel_info['login_rate_6'] = round((0 if new_user_count == 0 else login_level_6 / float(new_user_count)), 2)
        channel_info['login_rate_7'] = round((0 if new_user_count == 0 else login_level_7 / float(new_user_count)), 2)

        channel_info['dtv1'], channel_info['dtv2'], channel_info['dtv3'] = dtv1, dtv2, dtv3
        channel_info['dtv4'], channel_info['dtv5'], channel_info['dtv6'], channel_info['dtv7'] = dtv4, dtv5, dtv6, dtv7
        channel_info['dtv14'], channel_info['dtv15'], channel_info['dtv30'], channel_info['dtv60'] = dtv14, dtv15, dtv30, dtv60
        channel_info['dtv90'], channel_info['dtv120'] = dtv90, dtv120

        # DAU(日活跃用户数)、WAU(周活跃用户数)、MAU(月活跃用户数)
        DAU, WAU, MAU = get_active_user(fmt, 1, channel), get_active_user(fmt, 7, channel), get_active_user(fmt, 30, channel)
        channel_info['DAU'], channel_info['WAU'], channel_info['MAU'] = DAU, WAU, MAU
        # 日流失、周流失、月流失
        day_wastage, week_wastage, month_wastage = get_wastage_user(fmt, 1, channel), get_wastage_user(fmt, 7, channel), get_wastage_user(fmt, 30, channel)
        channel_info['day_wastage_rate'] = round((0 if DAU == 0 else (day_wastage / float(DAU))), 2)
        channel_info['week_wastage_rate'] = round((0 if WAU == 0 else (week_wastage / float(WAU))), 2)
        channel_info['month_wastage_rate'] = round((0 if MAU == 0 else (month_wastage / float(MAU))), 2)

        channel_info["register_list"] = register_list

    return channel_info


def get_active_user(day_time, days, channel):
    start_day = Time.str_to_datetime(Time.yesterday_time(Time.current_ts()), '%Y-%m-%d')
    end_day = Time.str_to_datetime(day_time, '%Y-%m-%d')
    day_delta = int((start_day - end_day).days) + 1
    res = RunCollect.objects.filter(day_time=day_time, channel=channel).values("json_data").first()
    print("-active_user--:", day_time, channel, day_delta, days)
    if res:
        res_info = Context.json_loads(res.get("json_data"))
        login_user = ("DAU" if days == 1 else "WAU" if days == 7 else "MAU")
        au_info = int(res_info["{}".format(login_user)])
        print("-au_info--:", au_info)
        if au_info <= 0 and day_delta >= days:
            wastage = deal_active_user(day_time, days, channel)
        else:
            if day_delta == days:
                wastage = deal_active_user(day_time, days, channel)
            else:
                wastage = int(res_info["{}".format(login_user)])
    else:
        if day_delta >= days:
            wastage = deal_active_user(day_time, days, channel)
        else:
            wastage = 0
    return wastage


def deal_active_user(day_time, days, channel):
    wastage = 0
    for i in range(0, days):
        fmt = (Time.str_to_datetime(day_time, "%Y-%m-%d") + datetime.timedelta(days=-i)).strftime("%Y-%m-%d")
        user_info = Context.RedisCache.hget_keys('user_daily:{}:{}:*'.format(channel, fmt))
        for user_str in user_info:
            user_id = int(user_str.split(':')[3])
            if user_id > 1000000:
                online = Context.RedisCache.hash_get('user_daily:{}:{}:{}'.format(channel, day_time, user_id), "login.times")
                if online:
                    wastage += 1
                else:
                    continue
            else:
                continue
    return wastage


def get_wastage_user(day_time, days, channel=None):
    user_list = []
    for i in range(-days + 1, -days + 2):
        fmt1 = (Time.str_to_datetime(day_time, "%Y-%m-%d") + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        if channel:
            user_info = Context.RedisCache.hget_keys('user_daily:{}:{}:*'.format(channel, fmt1))
        else:
            user_info = Context.RedisCache.hget_keys('user_daily:*:{}:*'.format(fmt1))
        for user_str in user_info:
            user_id = int(user_str.split(':')[3])
            if user_id > 1000000:
                channel_id = Context.RedisMix.hash_get('user:{}'.format(user_id), 'channelid')
                online = Context.RedisCache.hash_get('user_daily:{}:{}:{}'.format(channel_id, day_time, user_id), "login.times")
                if online and user_id not in user_list:
                    user_list.append(user_id)
                else:
                    continue
            else:
                continue
    day_wastage = 0
    for i in range(days-days+1, days+1):
        fmt2 = (Time.str_to_datetime(day_time, "%Y-%m-%d") + datetime.timedelta(days=-i)).strftime("%Y-%m-%d")
        for user_id in user_list:
            channel_id = Context.RedisMix.hash_get('user:{}'.format(user_id), 'channelid')
            online = Context.RedisCache.hash_get('user_daily:{}:{}:{}'.format(channel_id, fmt2, user_id), "login.times")
            if online is None:
                day_wastage += 1
            else:
                continue

    return day_wastage


def everyday_user_info(day_time, channel=None):
    active_list, register_list = [], []
    start_stamp = Time.str_to_timestamp(day_time + " 00:00:00")
    end_stamp = Time.str_to_timestamp(day_time + " 23:59:59")
    if channel:
        user_info = Context.RedisCache.hget_keys('user_daily:{}:{}:*'.format(channel, day_time))
    else:
        user_info = Context.RedisCache.hget_keys('user_daily:*:{}:*'.format(day_time))
    for user_str in user_info:
        user_id = int(user_str.split(':')[3])
        if user_id > 1000000:
            channel_id = Context.RedisMix.hash_get('user:{}'.format(user_id), 'channelid')
            online = Context.RedisCache.hash_get('user_daily:{}:{}:{}'.format(channel_id, day_time, user_id), "login.times")
            create_stamp = Time.str_to_timestamp(str(Context.RedisMix.hash_get('user:{}'.format(user_id), 'createTime'))[:19])
            if online and user_id not in active_list:
                active_list.append(user_id)
                if create_stamp >= start_stamp and create_stamp <= end_stamp:
                    register_list.append(user_id)
            else:
                continue
        else:
            continue
    return active_list, register_list


def deal_roi_info(day_time, days, user_list):
    user_total = 0
    for i in range(0, days):
        day_total = 0
        fmt = (Time.str_to_datetime(day_time, "%Y-%m-%d") + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        for uid in user_list:
            channel_id = Context.RedisMix.hash_get('user:{}'.format(uid), 'channelid')
            pay_total = Context.RedisCache.hash_get('user_daily:{}:{}:{}'.format(channel_id, fmt, uid),"{}.pay.user.pay_total".format(channel_id))
            if pay_total:
                user_pay = int(pay_total)
            else:
                user_pay = 0
            day_total += user_pay
        user_total += day_total
    return user_total


def get_visitor_ltv(day_time, days, user_list):
    user_count = len(user_list)
    user_total = 0
    for i in range(0, days):
        day_total = 0
        fmt = (Time.str_to_datetime(day_time, "%Y-%m-%d") + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        for uid in user_list:
            channel_id = Context.RedisMix.hash_get('user:{}'.format(uid), 'channelid')
            pay_total = Context.RedisCache.hash_get('user_daily:{}:{}:{}'.format(channel_id, fmt, uid), "{}.pay.user.pay_total".format(channel_id))
            if pay_total:
                user_pay = int(pay_total)
            else:
                user_pay = 0
            day_total += user_pay
        user_total += day_total
    if user_count == 0:
        ltv = 0.0
    else:
        ltv = round(user_total / float(user_count), 2)
    return ltv


def get_ltv(args, days, class_name, status=None):
    day_time, user_list = args["day_time"],  args["user_list"]
    channel = args["channel"]
    start_day = Time.str_to_datetime(Time.yesterday_time(Time.current_ts()), '%Y-%m-%d')
    end_day = Time.str_to_datetime(day_time, '%Y-%m-%d')
    day_delta = int((start_day - end_day).days) + 1
    res = class_name.objects.filter(day_time=end_day, channel=channel).values("json_data").first()
    if res:
        ltv_info = Context.json_loads(res.get("json_data"))
        if status:
            day_ltv = float(ltv_info["dtv{}".format(days)])
        else:
            day_ltv = float(ltv_info["ltv{}".format(days)])
        if day_ltv <= 0 and day_delta >= days:
            ltv = compute_ltv_info(day_time, days, user_list, status)
        else:
            if day_delta == days:
                ltv = compute_ltv_info(day_time, days, user_list, status)
            else:
                ltv = day_ltv
    else:
        if day_delta >= days:
            ltv = compute_ltv_info(day_time, days, user_list, status)
        else:
            ltv = 0
    return ltv


def compute_ltv_info(day_time, days, user_list, status):
    user_total, user_count = 0, len(user_list)
    for i in range(0, days):
        day_total = 0
        fmt = (Time.str_to_datetime(day_time, "%Y-%m-%d") + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        for uid in user_list:
            channel_id = Context.RedisMix.hash_get('user:{}'.format(uid), 'channelid')
            pay_total = Context.RedisCache.hash_get('user_daily:{}:{}:{}'.format(channel_id, fmt, uid),"{}.pay.user.pay_total".format(channel_id))
            if pay_total:
                user_pay = int(pay_total)
            else:
                user_pay = 0
            day_total += user_pay
        if status:
            user_total = day_total
        else:
            user_total += day_total
    if user_count == 0:
        ltv = 0
    else:
        ltv = round(user_total / float(user_count), 2)
    return ltv


def get_new_pay_data(day_time, channel=None):
    user_list = []
    start_stamp = Time.str_to_timestamp(day_time + " 00:00:00")
    end_stamp = Time.str_to_timestamp(day_time + " 23:59:59")
    if channel:
        user_info = Context.RedisCache.hget_keys('user_daily:{}:{}:*'.format(channel, day_time))
    else:
        user_info = Context.RedisCache.hget_keys('user_daily:*:{}:*'.format(day_time))
    for user_str in user_info:
        user_id = int(user_str.split(':')[3])
        if user_id > 1000000:
            channel_id = Context.RedisMix.hash_get('user:{}'.format(user_id), 'channelid')
            create_stamp = Time.str_to_timestamp(str(Context.RedisMix.hash_get('user:{}'.format(user_id), 'createTime'))[:19])
            online = Context.RedisCache.hash_get('user_daily:{}:{}:{}'.format(channel_id, day_time, user_id),"login.times")
            if online and create_stamp >= start_stamp and create_stamp <= end_stamp and str(user_id) not in user_list:
                user_list.append(user_id)
            else:
                continue
        else:
            continue
    return user_list


def get_visitor_level(channel_id, day_time, status):
    login_level_1, login_level_2, login_level_3, login_level_4, login_level_5, login_level_6 = 0, 0, 0, 0, 0, 0
    login_level_7, guid = 0, status
    user_list = Context.RedisCache.hget_keys('user_daily:{}:{}:*'.format(channel_id, day_time))
    player_list = []
    start_stamp = Time.str_to_timestamp(day_time + " 00:00:00")
    end_stamp = Time.str_to_timestamp(day_time + " 23:59:59")
    for user_str in user_list:
        user_id = int(user_str.split(':')[3])
        if user_id > 1000000:
            guid_create = Tool.to_int(Context.RedisMix.hash_get('user:{}'.format(user_id), 'guidCreate'), 0)
            create_stamp = Time.str_to_timestamp(str(Context.RedisMix.hash_get('user:{}'.format(user_id), 'createTime'))[:19])
            if create_stamp >= start_stamp and create_stamp <= end_stamp and str(user_id) not in player_list and guid_create==guid:
                player_list.append(user_id)
            else:
                continue
        else:
            continue

    for uid in player_list:
        login_level = login_level_info()
        for index, days in login_level.items():
            if index == 1:
                result = get_day_login_level(day_time, channel_id, uid, days)
                login_level_1 += result
            if index == 2:
                result = get_day_login_level(day_time, channel_id, uid, days)
                login_level_2 += result
            if index == 3:
                result = get_day_login_level(day_time, channel_id, uid, days)
                login_level_3 += result
            if index == 4:
                result = get_day_login_level(day_time, channel_id, uid, days)
                login_level_4 += result
            if index == 5:
                result = get_day_login_level(day_time, channel_id, uid, days)
                login_level_5 += result
            if index == 6:
                result = get_day_login_level(day_time, channel_id, uid, days)
                login_level_6 += result
            if index == 7:
                result = get_day_login_level(day_time, channel_id, uid, days)
                login_level_7 += result

    return login_level_1, login_level_2, login_level_3, login_level_4, login_level_5,login_level_6,login_level_7


def get_login_level(channel_id, day_time, player_list):
    login_level_1, login_level_2, login_level_3 = 0, 0, 0
    login_level_4, login_level_5, login_level_6 = 0, 0, 0
    login_level_7 = 0

    for uid in player_list:
        login_level = login_level_info()
        for index, days in login_level.items():
            if index == 1:
                result = get_day_login_level(day_time, channel_id, uid, days)
                login_level_1 += result
            if index == 2:
                result = get_day_login_level(day_time, channel_id, uid, days)
                login_level_2 += result
            if index == 3:
                result = get_day_login_level(day_time, channel_id, uid, days)
                login_level_3 += result
            if index == 4:
                result = get_day_login_level(day_time, channel_id, uid, days)
                login_level_4 += result
            if index == 5:
                result = get_day_login_level(day_time, channel_id, uid, days)
                login_level_5 += result
            if index == 6:
                result = get_day_login_level(day_time, channel_id, uid, days)
                login_level_6 += result
            if index == 7:
                result = get_day_login_level(day_time, channel_id, uid, days)
                login_level_7 += result

    return login_level_1, login_level_2, login_level_3, login_level_4, login_level_5,login_level_6,login_level_7


def get_day_login_level(day_time, channel_id, uid, days):
    if days <= 1:
        for i in range(days, days + 1):
            old_day = (Time.str_to_datetime(day_time, "%Y-%m-%d") + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            user_login = Context.RedisCache.hash_get('user_daily:{}:{}:{}'.format(channel_id, old_day, uid),"login.times")
            if user_login:
                return 1
            else:
                return 0
    else:
        for i in range(days-1, days):
            old_day = (Time.str_to_datetime(day_time, "%Y-%m-%d") + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            user_login = Context.RedisCache.hash_get('user_daily:{}:{}:{}'.format(channel_id, old_day, uid),"login.times")
            if user_login:
                return 1
            else:
                return 0


def get_barrel_level(channel_id, day_time):
    player_list = []
    user_list = Context.RedisCache.hget_keys('user_daily:{}:{}:*'.format(channel_id, day_time))
    start_stamp = Time.str_to_timestamp(day_time + " 00:00:00")
    end_stamp = Time.str_to_timestamp(day_time + " 23:59:59")
    for user_str in user_list:
        user_id = int(user_str.split(':')[3])
        if user_id > 1000000:
            create_stamp = Time.str_to_timestamp(str(Context.RedisMix.hash_get('user:{}'.format(user_id), 'createTime'))[:19])
            if create_stamp >= start_stamp and create_stamp <= end_stamp and str(user_id) not in player_list:
                player_list.append(user_id)
            else:
                continue
        else:
            continue
    url ="/v2/shell/gm/day_barrel_total"
    context = {"phone": "system", "player_list": player_list}
    ret = Context.Controller.request(url, context)
    ret_dict = Context.json_loads(ret.content)
    if "info" not in ret_dict:
        barrel_500_1, barrel_500_2, barrel_3000_1, barrel_3000_2 = 0, 0, 0, 0
    else:
        barrel = ret_dict["info"]
        barrel_500_1, barrel_500_2, barrel_3000_1, barrel_3000_2 = barrel["barrel_500_1"], barrel["barrel_500_2"], barrel["barrel_3000_1"], barrel["barrel_3000_2"]
    return barrel_500_1, barrel_500_2, barrel_3000_1, barrel_3000_2


def login_level_info():
    level = {
        1: 1,
        2: 3,
        3: 7,
        4: 14,
        5: 30,
        6: 60,
        7: 90,
    }
    return level


def login_level_list():
    level = {
        1: 1,
        2: 3,
        3: 4,
        4: 5,
        5: 6,
        6: 7,
        7: 8,
        8: 9,
        9: 10,
        10: 11,
        11: 12,
        12: 13,
        13: 14,
        14: 15,
        15: 16,
        16: 17,
        17: 18,
        18: 19,
        19: 20,
        20: 21,
        21: 22,
        22: 23,
        23: 24,
        24: 25,
        25: 26,
        26: 27,
        27: 28,
        28: 29,
        29: 30,
    }
    return level


def total_new_user(day_time, channel):
    last_time = Time.yesterday_time(Time.str_to_timestamp(day_time, "%Y-%m-%d"))
    res = Context.RedisCache.hash_getall('stat:{}:{}'.format(channel, last_time))
    ret = Context.RedisCache.hash_getall('stat:{}:{}'.format(channel, day_time))
    new_user = Tool.to_int(ret.get('{}.new.user.count'.format(channel)), 0)
    if res:
        total_user = res.get('{}.total.new.user'.format(channel))
        new_user_count = Tool.to_int(total_user, 0) + new_user
    else:
        last_count = deal_total_user(last_time, channel)
        new_user_count = int(last_count) + new_user

    return new_user_count


def deal_total_user(day_time, channel):
    new_user_count = 0
    start_date = Time.str_to_datetime("2019-12-23", '%Y-%m-%d')
    end_date = Time.str_to_datetime(day_time, '%Y-%m-%d')
    while start_date <= end_date:
        fmt = Time.datetime_to_str(start_date, '%Y-%m-%d')
        result = Context.RedisCache.hash_getall('stat:{}:{}'.format(channel, fmt))
        user_daily = Context.RedisCache.hget_keys('user_daily:{}:{}:*'.format(channel, fmt))
        if result and user_daily:
            new_user_count += int(result.get('{}.new.user.count'.format(channel), 0))  # 新增人数
            start_date = Time.next_days(start_date)
        else:
            start_date = Time.next_days(start_date)
            continue
    Context.RedisCache.hash_mset('stat:{}:{}'.format(channel, day_time), {"{}.total.new.user".format(channel): new_user_count})
    return new_user_count


@decorator
def order_query(request):
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info['1000']
    phone, pay_info = request.session.get('uid'), Data_Info.get_pay_status()
    number, url_date, order_list = 1, "/run_manage/order_query/", Data_Info.get_order_status()  # 翻页
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page:
            conf, order_info = get_order_query(phone)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            order_info.update({"number": number, "page": page})
        else:
            end_day = datetime.date.today().strftime('%Y-%m-%d')
            order_info = {"channel": "0", "start_day": end_day, "end_day": end_day, "pay_status": "0", "order_status": "user_id",  "param_id": "", "page": []}
    else:
        dic = request.POST
        param_id = dic.get('param_id').encode('utf-8').strip()
        pay_status = dic.get('pay_status').encode('utf-8')
        order_status = dic.get('order_status').encode('utf-8')  # 用户ID或订单号或商品ID
        channel = dic.get('channel').encode('utf-8')
        start_day = dic.get("start_time")[:10]
        end_day = dic.get("stop_time")[:10]

        ret = Context.RedisCache.hget_keys('pay_order:{}:*:*'.format(phone))  # 删除数据
        for del_key in ret:
            Context.RedisCache.delete(del_key)

        start_date = Time.str_to_datetime(start_day, '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_day, '%Y-%m-%d')

        day_list = []
        while start_date <= end_date:
            res = OrderQuery.objects.filter(day_time=start_date).first()
            every_day = Time.datetime_to_str(start_date, '%Y-%m-%d')
            if res:
                start_date = Time.next_days(start_date)
                continue
            else:
                day_order = Context.RedisCache.hget_keys('pay_order:{}:{}:*'.format(phone, every_day))
                if day_order:
                    day_list.append(every_day)
                    if every_day == datetime.datetime.now().strftime('%Y-%m-%d'):
                        query_redis_order(phone, every_day, every_day)  # 插入数据
                    else:
                        start_date = Time.next_days(start_date)
                        continue
                else:
                    day_list.append(every_day)
                    query_redis_order(phone, every_day, every_day)  # 插入数据
            start_date = Time.next_days(start_date)

        order_info = {"start_day": start_day, "end_day": end_day, "channel": channel, "pay_status": pay_status,"order_status": order_status,"param_id": param_id, "day_list": day_list}
        keys = 'pay_order:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, order_info)

        start_date = Time.str_to_datetime(start_day, '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_day, '%Y-%m-%d')
        sorted_info = order_screen(phone, channel, pay_status, order_status, param_id, start_date, end_date, day_list)  # 条件筛选

        paginator = Paginator(sorted_info, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        order_info.update({"page": page, "number": number})
    order_info.update({"chanel_info": chanel_info, "pay_info": pay_info,"order_list": order_list, "url_date": url_date})
    return render(request, 'run_manage/order_query.html', order_info)


def query_redis_order(phone, start_time, end_time):
    url = '/v1/shell/order/order_query'
    context = {"start_time": start_time, "end_time": end_time}
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    ret_dict = Context.json_loads(ret.content)
    if "order" not in ret_dict:
        return 0
    else:
        for info in ret_dict["order"]:
            for key, value in info.items():
                state = int(value.get("state"))
                product = value.get("productId")
                price = int(float(value.get("cost")))
                product_name = ProcessInfo.verify_productId(product, price)
                create_time = value.get("createTime").encode('utf-8')[:19]
                value.update({'product_name': product_name, 'cost': price, 'createTime': create_time, 'deliverTime': value.get("deliverTime", 0), 'state': state, 'order_id': key})
                Context.RedisCache.hash_mset('pay_order:{}:{}:{}'.format(phone, create_time[:10], key), value)


def get_order_query(phone):
    keys = 'pay_order:{}:{}'.format(phone,'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day","channel", "pay_status","order_status", "param_id","day_list"])
    start_day, end_day, channel, pay_status, order_status,param_id,day_list = result[0],result[1],result[2],result[3],result[4],result[5],eval(result[6])
    start_time = Time.str_to_datetime(start_day, '%Y-%m-%d')
    end_time = Time.str_to_datetime(end_day, '%Y-%m-%d')
    sorted_info = order_screen(phone,channel,pay_status,order_status,param_id,start_time,end_time,day_list) #条件筛选

    default_info = {"start_day": start_day, "end_day": end_day, "channel": channel, "pay_status": pay_status,"order_status": order_status,"param_id": param_id}
    return sorted_info, default_info


# 定时器插入订单数据
def insert_order_info(phone,start_time,end_time):
    url = '/v1/shell/order/order_query'
    context = {"start_time": start_time, "end_time": end_time}
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    ret_dict = Context.json_loads(ret.content)
    if "order" not in ret_dict:
        return 0
    else:
        record_info = []
        for info in ret_dict["order"]:
            for key, value in info.items():
                user_id = value.get("userId")
                pay_total = value.get("pay_total")
                state = int(value.get("state"))
                product = value.get("productId")
                price = int(float(value.get("cost")))
                product_name = ProcessInfo.verify_productId(product, price)
                create_time = value.get("createTime").encode('utf-8')[:19]
                value.update({'product_name': product_name, 'cost': price, 'createTime': create_time, 'deliverTime': value.get("deliverTime", 0), 'state': state, 'order_id': key})
                OrderQuery.objects.filter(user_id=user_id).update(pay_total=pay_total)
                record_info.append(value)
        sorted_info = sorted(record_info, key=lambda x: Time.str_to_timestamp(x['createTime']))
        create_order_data(sorted_info)


def order_screen(phone, channel,pay_status,order_status,param_id,start_date,end_date, day_list):
    order_list = []
    if channel == "0" and pay_status == "0":
        res_info = OrderQuery.objects.filter(day_time__range=[start_date, end_date]).values('json_data', 'pay_total')
        for every_day in day_list:
            day_order = Context.RedisCache.hget_keys('pay_order:{}:{}:*'.format(phone, every_day))
            for key in day_order:
                ret = Context.RedisCache.hash_getall(key)
                order_list.append(ret)

    elif channel == "0" and pay_status == "1":
        res_info = OrderQuery.objects.filter(day_time__range=[start_date, end_date]).exclude(pay_status="6").values('json_data', 'pay_total')
        for every_day in day_list:
            day_order = Context.RedisCache.hget_keys('pay_order:{}:{}:*'.format(phone, every_day))
            for key in day_order:
                ret = Context.RedisCache.hash_getall(key)
                if ret["state"].encode('utf-8') != "6":
                    order_list.append(ret)
                else:
                    continue

    elif channel == "0" and pay_status == "6":
        res_info = OrderQuery.objects.filter(day_time__range=[start_date, end_date], pay_status=pay_status).values('json_data', 'pay_total')
        for every_day in day_list:
            day_order = Context.RedisCache.hget_keys('pay_order:{}:{}:*'.format(phone, every_day))
            for key in day_order:
                ret = Context.RedisCache.hash_getall(key)

                if ret["state"].encode('utf-8') == pay_status:
                    order_list.append(ret)
                else:
                    continue
    elif channel != "0" and pay_status == "0":
        res_info = OrderQuery.objects.filter(day_time__range=[start_date, end_date],channel=channel).values('json_data', 'pay_total')
        for every_day in day_list:
            day_order = Context.RedisCache.hget_keys('pay_order:{}:{}:*'.format(phone, every_day))
            for key in day_order:
                ret = Context.RedisCache.hash_getall(key)
                if ret["channelid"].encode('utf-8') == channel:
                    order_list.append(ret)
                else:
                    continue
    elif channel != "0" and pay_status == "1":
        res_info = OrderQuery.objects.filter(day_time__range=[start_date, end_date],channel=channel).exclude(pay_status="6").values('json_data', 'pay_total')
        for every_day in day_list:
            day_order = Context.RedisCache.hget_keys('pay_order:{}:{}:*'.format(phone, every_day))
            for key in day_order:
                ret = Context.RedisCache.hash_getall(key)
                if ret["state"].encode('utf-8') != "6" and ret["channelid"].encode('utf-8') == channel:
                    order_list.append(ret)
                else:
                    continue
    else:
        res_info = OrderQuery.objects.filter(day_time__range=[start_date, end_date],channel=channel, pay_status=pay_status).values('json_data', 'pay_total')
        for every_day in day_list:
            day_order = Context.RedisCache.hget_keys('pay_order:{}:{}:*'.format(phone, every_day))
            for key in day_order:
                ret = Context.RedisCache.hash_getall(key)
                if ret["state"].encode('utf-8') == pay_status and ret["channelid"].encode('utf-8') == channel:
                    order_list.append(ret)
                else:
                    continue

    if param_id != "":
        param_list = []
        if order_status == "product_id":
            result = res_info.filter(productId=param_id)
            for rid in order_list:
                if rid["productId"].encode('utf-8') == param_id:
                    param_list.append(rid)
                else:
                    continue
        elif order_status == "user_id":
            result = res_info.filter(user_id=param_id)
            for rid in order_list:
                if rid["userId"].encode('utf-8') == param_id:
                    param_list.append(rid)
                else:
                    continue
        else:
            result = res_info.filter(order_id=param_id)
            for rid in order_list:
                if rid["order_id"].encode('utf-8') == param_id:
                    param_list.append(rid)
                else:
                    continue
    else:
        param_list = order_list
        result = res_info

    order_info = []
    for data in result:
        order_json = json.loads(data.get("json_data"))
        order_json.update({"pay_total": data.get("pay_total")})
        order_info.append(order_json)

    order_info.extend(param_list)

    period_pay, order_data = {}, []
    res_info.order_by("day_time")
    for info in order_info:
        pay_total = info.get("pay_total")
        if int(info["state"]) == 6:
            if info["userId"] in period_pay:
                period_pay[info["userId"]] += int(float(info["cost"]))
            else:
                period_pay[info["userId"]] = int(float(info["cost"]))
        else:
            if not info["userId"] in period_pay:
                period_pay[info["userId"]] = 0

        pay_type = str(info.get("paytype", 5))
        info.update({"pay_total": pay_total, "state": int(info["state"]), "paytype": pay_type, "period_pay": period_pay[info["userId"]], "createTime": info["createTime"].encode('utf-8')})
        order_data.append(info)
    sorted_info = sorted(order_data, key=lambda x: Time.str_to_timestamp(x["createTime"]), reverse=True)
    return sorted_info


def create_core_channel(result):
    """硬核渠道"""
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d')
    core_data = []
    for m_info in result:
        day_time,channel = m_info["day_time"],m_info["channel"]
        res = Hardcore.objects.filter(day_time=day_time, channel=channel)
        if res:
            Hardcore.objects.filter(day_time=day_time, channel=channel).update(
                day_time=day_time,
                channel=channel,
                json_data=Context.json_dumps(m_info),
                insert_time=insert_time,
            )
        else:
            mysql_info = Hardcore(
                day_time=day_time,
                channel=channel,
                json_data=Context.json_dumps(m_info),
                insert_time=insert_time,
            )
            core_data.append(mysql_info)

        if len(core_data) > 1000:
            Hardcore.objects.bulk_create(core_data)
            core_data = []
    Hardcore.objects.bulk_create(core_data)


def create_order_data(result):
    """新--创建数据"""
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d')
    order_data = []
    for m_info in result:
        day_time = Time.str_to_datetime(m_info["createTime"][:10], '%Y-%m-%d')
        order_id, channel, product_id, user_id, pay_status = m_info["order_id"], m_info["channelid"], m_info["productId"], m_info["userId"], m_info["state"]
        res = OrderQuery.objects.filter(day_time=day_time, order_id=order_id)
        if res:
            OrderQuery.objects.filter(day_time=day_time, order_id=order_id).update(
                day_time=day_time,
                channel=channel,
                productId=product_id,
                order_id=order_id,
                user_id=user_id,
                pay_total=m_info["pay_total"],
                pay_status=pay_status,
                json_data=json.dumps(m_info),
                insert_time=insert_time
            )
        else:
            new_order = OrderQuery(
                day_time=day_time,
                channel=channel,
                productId=product_id,
                order_id=order_id,
                user_id=user_id,
                pay_total=m_info["pay_total"],
                pay_status=pay_status,
                json_data=json.dumps(m_info),
                insert_time=insert_time
            )
            order_data.append(new_order)

        if len(order_data) > 1000:
            OrderQuery.objects.bulk_create(order_data)
            order_data = []

    OrderQuery.objects.bulk_create(order_data)


# ==========================数据汇总==============================
def D_data_deal_with(channel_data):
    """毛利率"""
    weixin_pay = int(channel_data.get("weixin_pay_total", 0))
    ali_pay = int(channel_data.get("ali_pay_total", 0))
    total_data = weixin_pay + ali_pay + int(channel_data.get("cdkey_pay_total", 0)) + int(channel_data.get("sdk_pay_total",0))
    if weixin_pay == 0 and ali_pay == 0:
        hand_free = 0.0
    else:
        hand_free = round((float(weixin_pay) * 0.01 + float(ali_pay) * 0.01), 2)  # 手续费

    shop_cost = float(channel_data.get("exchange_cost"))  # 商城成本
    gross_margin = round(round(float(total_data), 2) - round(float(shop_cost), 2) - float(hand_free), 2)  # 毛利
    if total_data == 0:
        gross_margin_ratio = 0
    else:
        gross_margin_ratio = float(gross_margin) / float(total_data)
    gross_margin_rate = round(gross_margin_ratio * 100, 2)
    f_shop_cost = round(shop_cost, 2)
    return hand_free, f_shop_cost, gross_margin, gross_margin_rate


def D_pay_rate(channel_data):
    """付费率"""
    login_user_count = int(channel_data.get("login_user_count", 0))
    pay_rate = (0 if login_user_count == 0 else round((int(channel_data.get("pay_user_count", 0)) / float(login_user_count)), 2))
    return pay_rate


def D_new_pay_rate(channel_data):
    """新增付费率"""
    new_user_count = int(channel_data.get("new_user_count", 0))
    new_pay_user_count = int(channel_data.get("new_pay_user_count", 0))
    new_pay_rate = (0 if new_user_count == 0 else round((new_pay_user_count / float(new_user_count)), 2))
    return new_pay_rate


def create_data_collect(result, class_name):
    """新--创建数据"""
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d')
    data_collect = []
    for m_info in result:
        day_time = m_info["day_time"]
        channel = m_info["channel"]
        del m_info["register_list"]
        res = class_name.objects.filter(day_time=day_time, channel=channel)
        if res:
            class_name.objects.filter(day_time=day_time, channel=channel).update(
                day_time=day_time,
                channel=channel,
                json_data=Context.json_dumps(m_info),
                insert_time=insert_time,
            )

        else:
            new_data = class_name(
                day_time=day_time,
                channel=channel,
                json_data=Context.json_dumps(m_info),
                insert_time=insert_time,
            )
            data_collect.append(new_data)

        if len(data_collect) > 1000:
            class_name.objects.bulk_create(data_collect)
            data_collect = []

    class_name.objects.bulk_create(data_collect)


def create_retention_info(result):
    """创建数据"""
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d')
    data_collect = []
    for m_info in result:
        for day_time, day_info in m_info.items():
            for channel_info in day_info:
                for channel, value in channel_info.items():
                    res = Retention.objects.filter(day_time=day_time, channel=channel)
                    if res:
                        Retention.objects.filter(day_time=day_time, channel=channel).update(
                            day_time=day_time,
                            channel=channel,
                            json_data=Context.json_dumps(value),
                            insert_time=insert_time,
                        )

                    else:
                        new_data = Retention(
                            day_time=day_time,
                            channel=channel,
                            json_data=Context.json_dumps(value),
                            insert_time=insert_time,
                        )
                        data_collect.append(new_data)

                    if len(data_collect) > 1000:
                        Retention.objects.bulk_create(data_collect)
                        data_collect = []

    Retention.objects.bulk_create(data_collect)


def create_ltv_info(result):
    """创建数据"""
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d')
    data_collect = []
    for m_info in result:
        for day_time, day_info in m_info.items():
            for channel_info in day_info:
                for channel, value in channel_info.items():
                    del value["register_list"]
                    res = LtvCollect.objects.filter(day_time=day_time, channel=channel)
                    if res:
                        LtvCollect.objects.filter(day_time=day_time, channel=channel).update(
                            day_time=day_time,
                            channel=channel,
                            json_data=Context.json_dumps(value),
                            insert_time=insert_time,
                        )

                    else:
                        new_data = LtvCollect(
                            day_time=day_time,
                            channel=channel,
                            json_data=Context.json_dumps(value),
                            insert_time=insert_time,
                        )
                        data_collect.append(new_data)

                    if len(data_collect) > 1000:
                        LtvCollect.objects.bulk_create(data_collect)
                        data_collect = []

    LtvCollect.objects.bulk_create(data_collect)


@decorator
def deal_xls(request):
    phone = request.session.get('uid')
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    dic = request.GET
    pid = int(dic.get('pid').encode('utf-8'))
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=run_data.xls'
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
    if pid == 1:  # 订单数据
        sheet.write(0, 0, '序号', style)
        sheet.write(0, 1, '订单号', style)
        sheet.write(0, 2, '渠道', style)
        sheet.write(0, 3, '用户ID', style)
        sheet.write(0, 4, '用户昵称', style)
        sheet.write(0, 5, '支付方式', style)
        sheet.write(0, 6, '支付状态', style)
        sheet.write(0, 7, '商品ID', style)
        sheet.write(0, 8, '商品名称', style)
        sheet.write(0, 9, '金额', style)
        sheet.write(0, 10, '生成订单日期', style)
        sheet.write(0, 11, '个人期间充值', style)
        sheet.write(0, 12, '累计充值', style)
        sheet.write(0, 13, '订单到账日期', style)

        order_info, _ = get_order_query(phone)
        data_row = 1
        for info in order_info:
            sheet.write(data_row, 0, data_row)
            sheet.write(data_row, 1, info.get("order_id", 0))
            channel = info.get("channelid", "")
            new_channel = (chanel_info[channel] if channel in chanel_info else channel)
            sheet.write(data_row, 2, new_channel)
            sheet.write(data_row, 3, info.get("userId", 0))
            sheet.write(data_row, 4, info.get("nick", 0))
            pay_type = info.get("paytype", "5").encode('utf-8')
            pay_way = ("微信" if pay_type == "1" else "支付宝" if pay_type == "2" else "sdk支付" if pay_type == "3" else "其他")
            sheet.write(data_row, 5, pay_way)
            pay_state = int(info.get("state", 0))
            state = ("已支付" if pay_state == 6 else "未发货" if pay_state == 5 else "支付失败" if pay_state == 7 else "未支付")

            sheet.write(data_row, 6, state)
            sheet.write(data_row, 7, info.get("productId", 0))
            sheet.write(data_row, 8, info.get("product_name", 0))
            sheet.write(data_row, 9, info.get("cost", 0))
            sheet.write(data_row, 10, info.get("createTime", 0))
            sheet.write(data_row, 11, info.get("period_pay", 0))
            sheet.write(data_row, 12, info.get("pay_total", 0))
            sheet.write(data_row, 13, info.get("deliverTime", 0))
            data_row = data_row + 1
    elif pid == 2:  # 游戏数据
        sheet.write(0, 0, '序号', style)
        sheet.write(0, 1, '日期', style)
        sheet.write(0, 2, '渠道', style)
        sheet.write(0, 3, '毛利率', style)
        sheet.write(0, 4, '毛利', style)
        sheet.write(0, 5, 'sdk支付', style)
        sheet.write(0, 6, '微信', style)
        sheet.write(0, 7, '支付宝', style)
        sheet.write(0, 8, '兑换码', style)
        sheet.write(0, 9, '商城成本', style)
        sheet.write(0, 10, '手续费', style)
        sheet.write(0, 11, '新增人数', style)
        sheet.write(0, 12, '累计新增', style)
        sheet.write(0, 13, '活跃总数', style)
        sheet.write(0, 14, '活跃付费人数', style)
        sheet.write(0, 15, '付费人数', style)
        sheet.write(0, 16, '付费次数', style)
        sheet.write(0, 17, '付费额度', style)
        sheet.write(0, 18, '付费率', style)
        sheet.write(0, 19, 'ARPU', style)
        sheet.write(0, 20, 'ARPPU', style)
        sheet.write(0, 21, '新增付费人数', style)
        sheet.write(0, 22, '新增付费次数', style)
        sheet.write(0, 23, '新增付费额度', style)
        sheet.write(0, 24, '新增付费率', style)
        sheet.write(0, 25, '新增次留', style)
        sheet.write(0, 26, '新增三留', style)
        sheet.write(0, 27, '新增七留', style)
        sheet.write(0, 28, '新增十四留', style)
        sheet.write(0, 29, '新增三十留', style)

        sheet.write(0, 30, '新增六十留', style)
        sheet.write(0, 31, '新增九十留', style)
        sheet.write(0, 32, 'LTV1', style)
        sheet.write(0, 33, 'LTV2', style)
        sheet.write(0, 34, 'LTV3', style)
        sheet.write(0, 35, 'LTV4', style)
        sheet.write(0, 36, 'LTV5', style)
        sheet.write(0, 37, 'LTV6', style)
        sheet.write(0, 38, 'LTV7', style)
        sheet.write(0, 39, 'LTV14', style)
        sheet.write(0, 40, 'LTV15', style)
        sheet.write(0, 41, 'LTV30', style)
        sheet.write(0, 42, 'LTV60', style)
        sheet.write(0, 43, 'LTV90', style)
        sheet.write(0, 44, 'LTV120', style)

        game_info, _ = get_data_collect(phone, GameCollect, 1)
        data_row = 1
        for info in game_info:
            sheet.write(data_row, 0, data_row)
            sheet.write(data_row, 1, info["day_time"])
            channel = info["channel"]
            if channel in chanel_info:
                channel_name = chanel_info[channel]
            else:
                channel_name = channel
            sheet.write(data_row, 2, channel_name)
            sheet.write(data_row, 3, str(info["gross_margin_rate"]) + "%")
            sheet.write(data_row, 4, info.get("gross_margin", 0))
            sheet.write(data_row, 5, info.get("sdk_pay_total", 0))
            sheet.write(data_row, 6, info.get("weixin_pay_total", 0))
            sheet.write(data_row, 7, info.get("ali_pay_total", 0))
            sheet.write(data_row, 8, info.get("cdkey_pay_total", 0))
            sheet.write(data_row, 9, info.get("exchange_cost", 0))
            sheet.write(data_row, 10, info.get("hand_free", 0))
            sheet.write(data_row, 11, info.get("new_user_count", 0))
            sheet.write(data_row, 12, info.get("total_new_user", 0))
            sheet.write(data_row, 13, info.get("login_user_count", 0))
            sheet.write(data_row, 14, info.get("active_pay_player", 0))
            sheet.write(data_row, 15, info.get("pay_user_count", 0))
            sheet.write(data_row, 16, info.get("user_pay_times", 0))
            sheet.write(data_row, 17, info.get("pay_user_total", 0))
            sheet.write(data_row, 18, str(info["pay_rate"]) + "%")
            sheet.write(data_row, 19, info.get("ARPU", 0))
            sheet.write(data_row, 20, info.get("ARPPU", 0))
            sheet.write(data_row, 21, info.get("new_pay_user_count", 0))
            sheet.write(data_row, 22, info.get("new_pay_user_times", 0))
            sheet.write(data_row, 23, info.get("new_pay_user_total", 0))
            sheet.write(data_row, 24, str(info["new_pay_rate"]) + "%")
            sheet.write(data_row, 25, info.get("login_level_1", 0))
            sheet.write(data_row, 26, info.get("login_level_2", 0))
            sheet.write(data_row, 27, info.get("login_level_3", 0))
            sheet.write(data_row, 28, info.get("login_level_4", 0))
            sheet.write(data_row, 29, info.get("login_level_5", 0))
            sheet.write(data_row, 30, info.get("login_level_6", 0))
            sheet.write(data_row, 31, info.get("login_level_7", 0))

            sheet.write(data_row, 32, info["ltv1"])
            sheet.write(data_row, 33, info["ltv2"])
            sheet.write(data_row, 34, info["ltv3"])
            sheet.write(data_row, 35, info["ltv4"])
            sheet.write(data_row, 36, info["ltv5"])
            sheet.write(data_row, 37, info["ltv6"])
            sheet.write(data_row, 38, info["ltv7"])
            sheet.write(data_row, 39, info["ltv14"])
            sheet.write(data_row, 40, info["ltv15"])
            sheet.write(data_row, 41, info["ltv30"])
            sheet.write(data_row, 42, info["ltv60"])
            sheet.write(data_row, 43, info["ltv90"])
            sheet.write(data_row, 44, info["ltv120"])
            data_row = data_row + 1
    elif pid == 3:  # 运营汇总
        sheet.write(0, 0, '序号', style)
        sheet.write(0, 1, '日期', style)
        sheet.write(0, 2, '渠道', style)
        sheet.write(0, 3, '投资回报率', style)
        sheet.write(0, 4, '日活跃用户平均收益', style)
        sheet.write(0, 5, '次日留存率', style)
        sheet.write(0, 6, '3日留存率', style)
        sheet.write(0, 7, '7日留存率', style)
        sheet.write(0, 8, '14日留存率', style)
        sheet.write(0, 9, '30日留存率', style)
        sheet.write(0, 10, '60日留存率', style)
        sheet.write(0, 11, '90日留存率', style)

        sheet.write(0, 12, '500炮倍以下', style)
        sheet.write(0, 13, '500炮倍以上', style)
        sheet.write(0, 14, '3000炮倍以下', style)
        sheet.write(0, 15, '3000炮倍以上', style)
        sheet.write(0, 16, 'DAU', style)
        sheet.write(0, 17, 'WAU', style)
        sheet.write(0, 18, 'MAU', style)
        sheet.write(0, 19, '日流失率', style)
        sheet.write(0, 20, '周流失率', style)
        sheet.write(0, 21, '月流失率', style)
        sheet.write(0, 22, 'DTV1', style)
        sheet.write(0, 23, 'DTV2', style)
        sheet.write(0, 24, 'DTV3', style)
        sheet.write(0, 25, 'DTV4', style)
        sheet.write(0, 26, 'DTV5', style)
        sheet.write(0, 27, 'DTV6', style)
        sheet.write(0, 28, 'DTV7', style)
        sheet.write(0, 29, 'DTV14', style)
        sheet.write(0, 30, 'DTV15', style)
        sheet.write(0, 31, 'DTV30', style)
        sheet.write(0, 32, 'DTV60', style)
        sheet.write(0, 33, 'DTV90', style)
        sheet.write(0, 34, 'DTV120', style)

        run_info, _ = get_data_collect(phone, RunCollect, 2)
        data_row = 1
        for info in run_info:
            sheet.write(data_row, 0, data_row)
            sheet.write(data_row, 1, info["day_time"])
            channel = info["channel"]
            if channel in chanel_info:
                channel_name = chanel_info[channel]
            else:
                channel_name = channel
            sheet.write(data_row, 2, channel_name)
            sheet.write(data_row, 3, info["ROI"])
            sheet.write(data_row, 4, info["ARPDAU"])
            sheet.write(data_row, 5, info["login_rate_1"])
            sheet.write(data_row, 6, info["login_rate_2"])
            sheet.write(data_row, 7, info["login_rate_3"])
            sheet.write(data_row, 8, info["login_rate_4"])
            sheet.write(data_row, 9, info["login_rate_5"])
            sheet.write(data_row, 10, info["login_rate_6"])
            sheet.write(data_row, 11, info["login_rate_7"])
            sheet.write(data_row, 12, info["barrel_500_1"])
            sheet.write(data_row, 13, info["barrel_500_2"])
            sheet.write(data_row, 14, info["barrel_3000_1"])
            sheet.write(data_row, 15, info["barrel_3000_2"])
            sheet.write(data_row, 16, info["DAU"])
            sheet.write(data_row, 17, info["WAU"])
            sheet.write(data_row, 18, info["MAU"])
            sheet.write(data_row, 19, info["day_wastage_rate"])
            sheet.write(data_row, 20, info["week_wastage_rate"])
            sheet.write(data_row, 21, info["month_wastage_rate"])
            sheet.write(data_row, 22, info["dtv1"])
            sheet.write(data_row, 23, info["dtv2"])
            sheet.write(data_row, 24, info["dtv3"])
            sheet.write(data_row, 25, info["dtv4"])
            sheet.write(data_row, 26, info["dtv5"])
            sheet.write(data_row, 27, info["dtv6"])
            sheet.write(data_row, 28, info["dtv7"])
            sheet.write(data_row, 29, info["dtv14"])
            sheet.write(data_row, 30, info["dtv15"])
            sheet.write(data_row, 31, info["dtv30"])
            sheet.write(data_row, 32, info["dtv60"])
            sheet.write(data_row, 33, info["dtv90"])
            sheet.write(data_row, 34, info["dtv120"])
            data_row = data_row + 1
    elif pid == 4:  # 硬核汇总
        sheet.write(0, 0, '序号', style)
        sheet.write(0, 1, '日期', style)
        sheet.write(0, 2, '渠道', style)
        sheet.write(0, 3, '500炮倍以下', style)
        sheet.write(0, 4, '500炮倍以下占比', style)
        sheet.write(0, 5, '500炮倍以上', style)
        sheet.write(0, 6, '500炮倍以上占比', style)
        sheet.write(0, 7, '3000炮倍以下', style)
        sheet.write(0, 8, '3000炮倍以下占比', style)
        sheet.write(0, 9, '3000炮倍以上', style)
        sheet.write(0, 10, '3000炮倍以上占比', style)
        sheet.write(0, 11, '新增人数', style)
        sheet.write(0, 12, '活跃总数', style)
        sheet.write(0, 13, '付费人数', style)
        sheet.write(0, 14, '付费次数', style)
        sheet.write(0, 15, '付费额度', style)
        sheet.write(0, 16, '付费率', style)
        sheet.write(0, 17, '新增付费人数', style)
        sheet.write(0, 18, '新增付费次数', style)
        sheet.write(0, 19, '新增付费额度', style)
        sheet.write(0, 20, '新增付费率', style)
        sheet.write(0, 21, '新增次留', style)
        sheet.write(0, 22, '次留占比', style)
        sheet.write(0, 23, '新增三留', style)
        sheet.write(0, 24, '三留占比', style)
        sheet.write(0, 25, '新增七留', style)
        sheet.write(0, 26, '七留占比', style)
        sheet.write(0, 27, '新增十四留', style)
        sheet.write(0, 28, '十四留占比', style)
        sheet.write(0, 29, '新增三十留', style)
        sheet.write(0, 30, '三十留占比', style)
        sheet.write(0, 31, '新增六十留', style)
        sheet.write(0, 32, '六十留占比', style)
        sheet.write(0, 33, '新增九十留', style)
        sheet.write(0, 34, '九十留占比', style)
        sheet.write(0, 35, 'LTV1', style)
        sheet.write(0, 36, 'LTV2', style)
        sheet.write(0, 37, 'LTV3', style)
        sheet.write(0, 38, 'LTV4', style)
        sheet.write(0, 39, 'LTV5', style)
        sheet.write(0, 40, 'LTV6', style)
        sheet.write(0, 41, 'LTV7', style)
        sheet.write(0, 42, 'LTV14', style)
        sheet.write(0, 43, 'LTV15', style)
        sheet.write(0, 44, 'LTV30', style)
        sheet.write(0, 45, 'LTV60', style)
        sheet.write(0, 46, 'LTV90', style)
        sheet.write(0, 47, 'LTV120', style)

        storage_info, _ = get_hardcore_data(phone)
        data_row = 1
        for info in storage_info:
            sheet.write(data_row, 0, data_row)
            day_time = str(info["day_time"]).replace("-", "/")
            sheet.write(data_row, 1, day_time)
            channel = info["channel"]
            if channel in chanel_info:
                channel_name = chanel_info[channel]
            else:
                channel = str(channel)
                if channel == "1":
                    channel_name = "硬核渠道汇总"
                elif channel == "2":
                    channel_name = "CPL渠道汇总"
                elif channel == "3":
                    channel_name = "CPS渠道汇总"
                else:
                    channel_name = channel
            sheet.write(data_row, 2, channel_name)
            sheet.write(data_row, 3, info["barrel_500_1"])
            sheet.write(data_row, 4, info["barrel_500_1_rate"])
            sheet.write(data_row, 5, info["barrel_500_2"])
            sheet.write(data_row, 6, info["barrel_500_2_rate"])
            sheet.write(data_row, 7, info["barrel_3000_1"])
            sheet.write(data_row, 8, info["barrel_3000_1_rate"])
            sheet.write(data_row, 9, info["barrel_3000_2"])
            sheet.write(data_row, 10, info["barrel_3000_2_rate"])
            sheet.write(data_row, 11, info["new_user_count"])
            sheet.write(data_row, 12, info["login_user_count"])
            sheet.write(data_row, 13, info["pay_user_count"])
            sheet.write(data_row, 14, info["user_pay_times"])
            sheet.write(data_row, 15, info["pay_user_total"])
            sheet.write(data_row, 16, info["pay_rate"])
            sheet.write(data_row, 17, info["new_pay_user_count"])
            sheet.write(data_row, 18, info["new_pay_user_times"])
            sheet.write(data_row, 19, info["new_pay_user_total"])
            sheet.write(data_row, 20, info["new_pay_rate"])

            login_level_1 = ("" if int(info["login_level_1"]) == 0 else info["login_level_1"])
            sheet.write(data_row, 21, login_level_1)
            login_level_1_rate = ("" if float(info["login_level_1_rate"]) == 0.0 else info["login_level_1_rate"])
            sheet.write(data_row, 22, login_level_1_rate)
            login_level_2 = ("" if int(info["login_level_2"]) == 0 else info["login_level_2"])
            sheet.write(data_row, 23, login_level_2)
            login_level_2_rate = ("" if float(info["login_level_2_rate"]) == 0.0 else info["login_level_2_rate"])
            sheet.write(data_row, 24, login_level_2_rate)
            login_level_3 = ("" if int(info["login_level_3"]) == 0 else info["login_level_3"])
            sheet.write(data_row, 25, login_level_3)
            login_level_3_rate = ("" if float(info["login_level_3_rate"]) == 0.0 else info["login_level_3_rate"])
            sheet.write(data_row, 26, login_level_3_rate)
            login_level_4 = ("" if int(info["login_level_4"]) == 0 else info["login_level_4"])
            sheet.write(data_row, 27, login_level_4)
            login_level_4_rate = ("" if float(info["login_level_4_rate"]) == 0.0 else info["login_level_4_rate"])
            sheet.write(data_row, 28, login_level_4_rate)
            login_level_5 = ("" if int(info["login_level_5"]) == 0 else info["login_level_5"])
            sheet.write(data_row, 29, login_level_5)
            login_level_5_rate = ("" if float(info["login_level_5_rate"]) == 0.0 else info["login_level_5_rate"])
            sheet.write(data_row, 30, login_level_5_rate)
            login_level_6 = ("" if int(info["login_level_6"]) == 0 else info["login_level_6"])
            sheet.write(data_row, 31, login_level_6)
            login_level_6_rate = ("" if float(info["login_level_6_rate"]) == 0.0 else info["login_level_6_rate"])
            sheet.write(data_row, 32, login_level_6_rate)
            login_level_7 = ("" if int(info["login_level_7"]) == 0 else info["login_level_7"])
            sheet.write(data_row, 33, login_level_7)
            login_level_7_rate = ("" if float(info["login_level_7_rate"]) == 0.0 else info["login_level_7_rate"])
            sheet.write(data_row, 34, login_level_7_rate)

            ltv1 = ("" if float(info["ltv1"]) == 0.0 else info["ltv1"])
            sheet.write(data_row, 35, ltv1)
            ltv2 = ("" if float(info["ltv2"]) == 0.0 else info["ltv2"])
            sheet.write(data_row, 36, ltv2)
            ltv3 = ("" if float(info["ltv3"]) == 0.0 else info["ltv3"])
            sheet.write(data_row, 37, ltv3)
            ltv4 = ("" if float(info["ltv4"]) == 0.0 else info["ltv4"])
            sheet.write(data_row, 38, ltv4)
            ltv5 = ("" if float(info["ltv5"]) == 0.0 else info["ltv5"])
            sheet.write(data_row, 39, ltv5)
            ltv6 = ("" if float(info["ltv6"]) == 0.0 else info["ltv6"])
            sheet.write(data_row, 40, ltv6)
            ltv7 = ("" if float(info["ltv7"]) == 0.0 else info["ltv7"])
            sheet.write(data_row, 41, ltv7)
            ltv14 = ("" if float(info["ltv14"]) == 0.0 else info["ltv14"])
            sheet.write(data_row, 42, ltv14)
            ltv15 = ("" if float(info["ltv15"]) == 0.0 else info["ltv15"])
            sheet.write(data_row, 43, ltv15)
            ltv30 = ("" if float(info["ltv30"]) == 0.0 else info["ltv30"])
            sheet.write(data_row, 44, ltv30)
            ltv60 = ("" if float(info["ltv60"]) == 0.0 else info["ltv60"])
            sheet.write(data_row, 45, ltv60)
            ltv90 = ("" if float(info["ltv90"]) == 0.0 else info["ltv90"])
            sheet.write(data_row, 46, ltv90)
            ltv120 = ("" if float(info["ltv120"]) == 0.0 else info["ltv120"])
            sheet.write(data_row, 47, ltv120)
            data_row = data_row + 1
    elif pid == 5:  # 留存汇总
        sheet.write(0, 0, '序号', style)
        sheet.write(0, 1, '日期', style)
        sheet.write(0, 2, '渠道', style)
        sheet.write(0, 3, '次日留存率', style)
        sheet.write(0, 4, '3日留存率', style)
        sheet.write(0, 5, '4日留存率', style)
        sheet.write(0, 6, '5日留存率', style)
        sheet.write(0, 7, '6日留存率', style)
        sheet.write(0, 8, '7日留存率', style)
        sheet.write(0, 9, '8日留存率', style)
        sheet.write(0, 10, '9日留存率', style)
        sheet.write(0, 11, '10日留存率', style)
        sheet.write(0, 12, '11日留存率', style)
        sheet.write(0, 13, '12日留存率', style)
        sheet.write(0, 14, '13日留存率', style)
        sheet.write(0, 15, '14日留存率', style)
        sheet.write(0, 16, '15日留存率', style)
        sheet.write(0, 17, '16日留存率', style)
        sheet.write(0, 18, '17日留存率', style)
        sheet.write(0, 19, '18日留存率', style)
        sheet.write(0, 20, '19日留存率', style)
        sheet.write(0, 21, '20日留存率', style)
        sheet.write(0, 22, '21日留存率', style)
        sheet.write(0, 23, '22日留存率', style)
        sheet.write(0, 24, '23日留存率', style)
        sheet.write(0, 25, '24日留存率', style)
        sheet.write(0, 26, '25日留存率', style)
        sheet.write(0, 27, '26日留存率', style)
        sheet.write(0, 28, '27日留存率', style)
        sheet.write(0, 29, '28日留存率', style)
        sheet.write(0, 30, '29日留存率', style)
        sheet.write(0, 31, '30日留存率', style)

        storage_info, _ = get_remain_data(phone)
        data_row = 1
        for info in storage_info:
            sheet.write(data_row, 0, data_row)
            day_time = str(info["day_time"]).replace("-", "/")
            sheet.write(data_row, 1, day_time)
            channel = info["channel"]
            if channel in chanel_info:
                channel_name = chanel_info[channel]
            else:
                channel = str(channel)
                if channel == "1":
                    channel_name = "硬核渠道汇总"
                elif channel == "2":
                    channel_name = "CPL渠道汇总"
                elif channel == "3":
                    channel_name = "CPS渠道汇总"
                else:
                    channel_name = channel
            sheet.write(data_row, 2, channel_name)
            sheet.write(data_row, 3, info["login_rate_1"])
            sheet.write(data_row, 4, info["login_rate_2"])
            sheet.write(data_row, 5, info["login_rate_3"])
            sheet.write(data_row, 6, info["login_rate_4"])
            sheet.write(data_row, 7, info["login_rate_5"])
            sheet.write(data_row, 8, info["login_rate_6"])
            sheet.write(data_row, 9, info["login_rate_7"])
            sheet.write(data_row, 10, info["login_rate_8"])
            sheet.write(data_row, 11, info["login_rate_9"])
            sheet.write(data_row, 12, info["login_rate_10"])
            sheet.write(data_row, 13, info["login_rate_11"])
            sheet.write(data_row, 14, info["login_rate_12"])
            sheet.write(data_row, 15, info["login_rate_13"])
            sheet.write(data_row, 16, info["login_rate_14"])
            sheet.write(data_row, 17, info["login_rate_15"])
            sheet.write(data_row, 18, info["login_rate_16"])
            sheet.write(data_row, 19, info["login_rate_17"])
            sheet.write(data_row, 20, info["login_rate_18"])
            sheet.write(data_row, 21, info["login_rate_19"])
            sheet.write(data_row, 22, info["login_rate_20"])
            sheet.write(data_row, 23, info["login_rate_21"])
            sheet.write(data_row, 24, info["login_rate_22"])
            sheet.write(data_row, 25, info["login_rate_23"])
            sheet.write(data_row, 26, info["login_rate_24"])
            sheet.write(data_row, 27, info["login_rate_25"])
            sheet.write(data_row, 28, info["login_rate_26"])
            sheet.write(data_row, 29, info["login_rate_27"])
            sheet.write(data_row, 30, info["login_rate_28"])
            sheet.write(data_row, 31, info["login_rate_29"])
            data_row = data_row + 1
    else:  # ltv汇总
        sheet.write(0, 0, '序号', style)
        sheet.write(0, 1, '日期', style)
        sheet.write(0, 2, '渠道', style)
        sheet.write(0, 3, '新增人数', style)
        sheet.write(0, 4, '累计充值', style)
        sheet.write(0, 5, 'LTV1', style)
        sheet.write(0, 6, 'LTV2', style)
        sheet.write(0, 7, 'LTV3', style)
        sheet.write(0, 8, 'LTV4', style)
        sheet.write(0, 9, 'LTV5', style)
        sheet.write(0, 10, 'LTV5', style)
        sheet.write(0, 11, 'LTV6', style)
        sheet.write(0, 12, 'LTV7', style)
        sheet.write(0, 13, 'LTV8', style)
        sheet.write(0, 14, 'LTV9', style)
        sheet.write(0, 15, 'LTV10', style)
        sheet.write(0, 16, 'LTV11', style)
        sheet.write(0, 17, 'LTV12', style)
        sheet.write(0, 18, 'LTV13', style)
        sheet.write(0, 19, 'LTV14', style)
        sheet.write(0, 20, 'LTV15', style)
        sheet.write(0, 21, 'LTV16', style)
        sheet.write(0, 22, 'LTV17', style)
        sheet.write(0, 23, 'LTV18', style)
        sheet.write(0, 24, 'LTV19', style)
        sheet.write(0, 25, 'LTV20', style)
        sheet.write(0, 26, 'LTV21', style)
        sheet.write(0, 27, 'LTV22', style)
        sheet.write(0, 28, 'LTV23', style)
        sheet.write(0, 29, 'LTV24', style)
        sheet.write(0, 30, 'LTV25', style)
        sheet.write(0, 31, 'LTV26', style)
        sheet.write(0, 32, 'LTV27', style)
        sheet.write(0, 33, 'LTV28', style)
        sheet.write(0, 34, 'LTV29', style)
        sheet.write(0, 35, 'LTV30', style)

        ltv_info, _ = get_ltv_data(phone)
        data_row = 1
        for info in ltv_info:
            sheet.write(data_row, 0, data_row)
            day_time = str(info["day_time"]).replace("-", "/")
            sheet.write(data_row, 1, day_time)
            channel = info["channel"]
            if channel in chanel_info:
                channel_name = chanel_info[channel]
            else:
                channel = str(channel)
                if channel == "1":
                    channel_name = "硬核渠道汇总"
                elif channel == "2":
                    channel_name = "CPL渠道汇总"
                elif channel == "3":
                    channel_name = "CPS渠道汇总"
                else:
                    channel_name = channel
            sheet.write(data_row, 2, channel_name)
            sheet.write(data_row, 3, info["new_user_count"])
            sheet.write(data_row, 4, info["new_pay_total"])
            sheet.write(data_row, 5, info["ltv1"])
            sheet.write(data_row, 6, info["ltv2"])
            sheet.write(data_row, 7, info["ltv3"])
            sheet.write(data_row, 8, info["ltv4"])
            sheet.write(data_row, 9, info["ltv5"])
            sheet.write(data_row, 10, info["ltv6"])
            sheet.write(data_row, 11, info["ltv7"])
            sheet.write(data_row, 12, info["ltv8"])
            sheet.write(data_row, 13, info["ltv9"])
            sheet.write(data_row, 14, info["ltv10"])
            sheet.write(data_row, 15, info["ltv11"])
            sheet.write(data_row, 16, info["ltv12"])
            sheet.write(data_row, 17, info["ltv13"])
            sheet.write(data_row, 18, info["ltv14"])
            sheet.write(data_row, 19, info["ltv15"])
            sheet.write(data_row, 20, info["ltv16"])
            sheet.write(data_row, 21, info["ltv17"])
            sheet.write(data_row, 22, info["ltv18"])
            sheet.write(data_row, 23, info["ltv19"])
            sheet.write(data_row, 24, info["ltv20"])
            sheet.write(data_row, 25, info["ltv21"])
            sheet.write(data_row, 26, info["ltv22"])
            sheet.write(data_row, 27, info["ltv23"])
            sheet.write(data_row, 28, info["ltv24"])
            sheet.write(data_row, 29, info["ltv25"])
            sheet.write(data_row, 30, info["ltv26"])
            sheet.write(data_row, 31, info["ltv27"])
            sheet.write(data_row, 32, info["ltv28"])
            sheet.write(data_row, 33, info["ltv29"])
            sheet.write(data_row, 34, info["ltv30"])

            data_row = data_row + 1
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response


@csrf_exempt
def deal_game_info(request):
    dic = request.POST
    channel_list = ["1022_0"]
    channel = dic.get('channel').encode('utf-8')
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # 真实的ip
    else:
        ip = request.META.get('REMOTE_ADDR')  # 代理ip
    print("------ip------", ip)

    if ip == "39.101.212.129" and channel in channel_list:
        start_time = dic.get("start_time")
        end_time = dic.get("end_time")
        res_info = GameCollect.objects.filter(day_time__range=(start_time, end_time), channel=channel).values('json_data').order_by("-day_time")
        sort_info = []
        for info in res_info:
            json_data = json.loads(info.get("json_data"))
            sort_info.append(json_data)
    else:
        sort_info = []
    return JsonResponse({"res": sort_info})


# ==========================普通玩家炮倍池填分设置(新)==============================
# @decorator
# def barrel_pool_config(request):
#     """普通玩家炮倍池填分--配置"""
#     phone = request.session.get('uid')
#     if request.method == 'GET':
#         url = '/v1/shell/gm/barrel_pool_config'
#         context = {}
#         new_info,common_info = [], []
#         msg, pool_data = Context.get_server_data(url, context, phone)
#         if msg:
#             for index, info in enumerate(pool_data["common_barrel"]):
#                 common_info.append({"index": index+1, "level_chip": info["level_chip"], "banker_chip": info["banker_chip"], "start":info["{}".format(index)][0], "end": info["{}".format(index)][len(info["{}".format(index)])-1]})
#             for index, info in enumerate(pool_data["new_barrel"]):
#                 new_info.append({"index": index+1, "level_chip": info["new_level_chip"], "banker_chip": info["new_banker_chip"], "start": info["{}".format(index+1001)][0], "end": info["{}".format(index+1001)][len(info["{}".format(index+1001)])-1]})
#         else:
#             common_info = [{"start":0,"end":250},{"start":300,"end":1500},{"start":2000,"end":5000}]
#             new_info = [{"start": 0, "end": 250}, {"start": 300, "end": 1500}, {"start": 2000, "end": 5000}]
#         return render(request, 'run_manage/barrel_pool_point.html', {"barrel": common_info, "new_barrel": new_info})
#     else:
#         dic = request.POST
#         barrel_pool = dic.getlist("add_barrel_pool")
#         old_data = TempData.objects.all().values('barrel_data_chip_list').first()
#         arr_barrel_pool_chip = json.loads(old_data['barrel_data_chip_list'])
#
#         length = len(barrel_pool)
#         barrel_info = []
#         for i in range(length):
#             barrel_info.append(long(barrel_pool[i]) - long(arr_barrel_pool_chip[i + 2]))
#         url = '/v1/shell/gm/alter_barrel_pool_config'
#         context = {"barrel_info": barrel_info}
#         msg, pool_info = Context.get_server_data(url, context, phone)
#         if msg:
#             code = True
#             info = "炮倍池填分修改成功!"
#         else:
#             code = False
#             info = "炮倍池填分修改失败!"
#         return JsonResponse({'code': code, 'info': info})

# ==========================普通玩家鸟蛋池填分设置(新)==============================
# @decorator
# def chip_pool_config(request):
#     """普通玩家鸟蛋池填分--配置"""
#     phone = request.session.get('uid')
#     if request.method == 'GET':
#         url = '/v2/shell/gm/chip_pool_config'
#         context = {}
#         context.update({"phone": phone, "pid": 1})
#         ret = Context.Controller.request(url, context)
#         result = Context.json_loads(ret.text)
#         if "common_chip_pool" not in result or "new_chip_pool" not in result or "all_pool" not in result:
#             return render(request, 'run_manage/fill_point.html')
#         common_chip_pool = result['common_chip_pool']
#         new_chip_pool = result['new_chip_pool']
#         all_pool_info = result["all_pool"]
#
#         data_chip,new_chip = [], []
#         for data in common_chip_pool:
#             data_chip.append(data['pool_chip'])
#
#         for pool in new_chip_pool:
#             new_chip.append(pool['new_pool_chip'])
#
#         TempData.objects.all().delete()
#         TempData.objects.create(
#             barrel_data_play_shot_gift_list=json.dumps(data_chip),
#             new_shot_gift_list=json.dumps(new_chip),
#             all_pool=Context.json_dumps(all_pool_info),
#         )
#         common_chip_info, new_chip_info = [], []
#         for chip in common_chip_pool:
#             chip.update({"start": chip["barrel_multis"][0], "end": chip["barrel_multis"][len(chip["barrel_multis"])-1]})
#             del chip["barrel_multis"]
#             common_chip_info.append(chip)
#
#         for sl in new_chip_pool:
#             sl.update({"start": sl["barrel_multis"][0], "end": sl["barrel_multis"][len(sl["barrel_multis"])-1]})
#             del sl["barrel_multis"]
#             new_chip_info.append(sl)
#
#         barrel_info = {"page": common_chip_info, "new_page": new_chip_info, "all_pool": all_pool_info}
#         return render(request, 'run_manage/fill_point.html', barrel_info)
#     else:
#         dic = request.POST
#         chip_pool = []
#         cid = int(dic.get("cid"))
#         if cid == 1:
#             name = "新手玩家"
#             new_add_chip = dic.getlist("new_add_chip")
#             old_data = TempData.objects.all().values('new_shot_gift_list').first()
#             original_chip = json.loads(old_data['new_shot_gift_list'])
#             for i in range(len(new_add_chip)):
#                 chip_pool.append(long(new_add_chip[i]) - long(original_chip[i]))
#         else:
#             name = "普通玩家"
#             barrel_pool = dic.getlist("add_chip")
#             old_data = TempData.objects.all().values('barrel_data_play_shot_gift_list').first()
#             arr_barrel_pool_chip = json.loads(old_data['barrel_data_play_shot_gift_list'])
#             for i in range(len(barrel_pool)):
#                 chip_pool.append(long(barrel_pool[i]) - long(arr_barrel_pool_chip[i]))
#
#         url = '/v2/shell/gm/chip_pool_config'
#         context = {"barrel_pool": chip_pool, "pid": 2, "fill": cid}
#         msg, pool_info = Context.get_server_data(url, context, phone)
#         if msg:
#             code = True
#             info = "{}的鸟蛋池填分修改成功!".format(name)
#         else:
#             code = False
#             info = "{}的鸟蛋池填分修改失败!".format(name)
#         return JsonResponse({'code': code, 'info': info})
#
# @decorator
# def alter_chip_trigger_give(request):
#     """普通玩家修改--赠送比"""
#     dic = request.POST
#     give_info = []
#     phone = request.session.get('uid')
#     gid = int(dic.get("gid"))
#     if gid == 1:
#         name = "新手玩家"
#         new_trigger = dic.getlist("new_triggle_count")
#         new_gift = dic.getlist("new_gift_count")
#         for trig, gift in zip(new_trigger, new_gift):
#             give_info.append({"triggle": trig, "gift": gift})
#     else:
#         name = "普通玩家"
#         triggle_count = dic.getlist("triggle_count")
#         gift_count = dic.getlist("gift_count")
#         for trig, gift in zip(triggle_count, gift_count):
#             give_info.append({"triggle": trig, "gift": gift})
#
#     url = '/v2/shell/gm/chip_pool_config'
#     context = {"count_data": give_info, "pid": 3, "give": gid}
#     context.update({"phone": phone})
#     ret = Context.Controller.request(url, context)
#     if ret.status_code == 200:
#         code = True
#         info = "{}的赠送比修改成功!".format(name)
#     else:
#         code = False
#         info = "{}的赠送比修改失败!".format(name)
#     return JsonResponse({'code': code, 'info': info})


# ==========================核心算法配置==============================
# @decorator
# def core_algorithm_config(request):
#     """核心算法配置"""
#     url = '/v2/shell/gm/loop_wave_protected'
#     if request.method == 'GET':
#         loop,protected = {"pid": 1}, {"pid": 3}
#         phone = request.session.get('uid')
#         l_msg, l_config = Context.get_server_data(url,loop,phone)
#         p_msg, p_config = Context.get_server_data(url, protected, phone)
#         if l_msg and p_msg:
#             pool_loop = l_config
#             player_protected = p_config
#         elif not l_msg and p_msg:
#             pool_loop = {}
#             player_protected = p_config
#         elif l_msg and not p_msg:
#             pool_loop = l_config
#             player_protected = {}
#         else:
#             pool_loop = {}
#             player_protected = {}
#         return render(request, 'run_manage/loop_wave_protected.html', {"pool_loop":pool_loop,"protected":player_protected})
#     else:
#         dic = request.POST
#         phone = request.session.get('uid')
#         pid = int(dic.get("pid"))
#         if pid == 2:
#             show = "池子循环被动处理"
#             config = {
#                 'store_triggle_rate': float(dic.get("store_triggle_rate",0)), # 蓄水状态下触发蓄水进度概率
#                 'store_cost_add': int(dic.get("store_cost_add",0)),# 蓄水状态下蓄水进度加成子弹数比率* 分数
#                 'out_triggle_rate': float(dic.get("out_triggle_rate",0)),# 放水状态下触发放水进度概率
#                 'out_cost_add': float(dic.get("out_cost_add",0)),# 放水状态下放水进度加成子弹数比率* 分数
#                 'wave_time_store': [int(dic.get("start_time_store",0)), int(dic.get("end_time_store",0))],# 蓄水状态下间隔时间
#                 'wave_time_out': [int(dic.get("start_time_out",0)), int(dic.get("end_time_out",0))],# 放水状态下起伏间隔随机时间
#                 'wave_time_still_store': [int(dic.get("start_still_store",0)), int(dic.get("start_still_store",0))],# 持续蓄水状态下起伏间隔时间
#                 'max_wave_still_time': int(dic.get("max_wave_still_time",0)), # 水池最大蓄水持续时间
#                 'min_store_time': int(dic.get("min_store_time",0)), # 最小蓄水需要时间
#                 'pool_wave_min_chip': [int(dic.get("one_pool_wave",0)), int(dic.get("two_pool_wave",0)), int(dic.get("three_pool_wave",0))],   # 水池起效地址额度为10w
#                 'store_full_rate': float(dic.get("store_full_rate",0)), # 蓄的鸟蛋相对于洗码的比例，满足则蓄满
#                 'out_chip_rate': [float(dic.get("start_out_chip_rate",0)), float(dic.get("end_out_chip_rate",0))], # 放水放出鸟蛋随机比例  总蓄水量*比例
#                 'enable_out_shot_per_sec': float(dic.get("enable_out_shot",0)),   # 每秒发射x次子弹及以上才拥有参与放水权限
#                 # ----- 庄家
#                 #'banker_add_space_time': 120,       # 庄家对赌时间间隔
#                 'banker_add_total_chip': int(dic.get("banker_total_chip",0)),      # 庄家最大拥有鸟蛋
#                 'banker_add_win_rate': float(dic.get("banker_win_rate",0)),             # 庄家赢率
#                 'banker_add_out_rate': int(dic.get("banker_out_rate",0)),                   # 庄家赔率
#                 'banker_add_bet_rate': [float(dic.get("start_banker_bet_rate",0)), float(dic.get("end_banker_bet_rate",0))],# 与庄家对赌时的赌注占蓄水额度的比例
#                 'banker_add_max_bet': [int(dic.get("one_banker_max_bet",0)), int(dic.get("two_banker_max_bet",0)), int(dic.get("three_banker_max_bet",0))],      # 一次对赌最大赌注
#             }
#         else:
#             show = "玩家游戏体验保护机制"
#             config = {
#                     'check_shot_count': int(dic.get("check_shot_count",0)),# 状态判断间隔子弹数
#                     'big_up_count': int(dic.get("big_up_count",0)),    # 大起的参考值 输赢最大子弹数目
#                     'big_down_count': int(dic.get("big_down_count",0)),  # 大落的参考值 输赢最大子弹数目
#                     'big_up_or_down_rate': float(dic.get("big_up_or_down_rate",0)),# 大起/大落的占比,(最低或者最高值相对于初始值差值)与(最大相对于最高的差值)比例
#                     'big_up_or_down_triggle_rate': float(dic.get("big_up_or_down_triggle_rate",0)),   # 保护被拉触发概率
#                     'triggle_big_up_or_down_rate': float(dic.get("triggle_big_up_or_down_rate",0)),   # 触发大起或者大落的概率
#                     'not_enough_up_or_down_count': int(dic.get("not_enough_up_or_down_count",0)),     # 平淡状态参考值  输赢最大子弹数目
#                     'lit_down_count': int(dic.get("lit_down_count",0)),                  # 大于该子弹数为小落
#                     'lit_up_kill_rate': float(dic.get("lit_up_kill_rate",0)),             # 小起击杀概率
#                     'big_up_kill_rate': float(dic.get("big_up_kill_rate",0)),             # 大起击杀概率
#                     'lit_down_not_kill_rate': float(dic.get("lit_down_not_kill_rate",0)), # 小落本被击杀鸟不击杀概率
#                     'big_down_not_kill_rate': float(dic.get("big_down_not_kill_rate",0)), # 大落本被击杀鸟不击杀概率
#                     'max_init_loan_chip': int(dic.get("max_init_loan_chip",0)),           # 最大可借贷额度
#                 }
#
#         context = {"config": config, "pid": pid,"phone": phone}
#         ret = Context.Controller.request(url, context)
#         if ret.status_code == 200:
#             code = True
#             info = "{}设置成功!".format(show)
#         else:
#             code = False
#             info = "{}设置失败!".format(show)
#         return JsonResponse({'code': code, 'info': info})

# ==========================活动怪池填分设置==============================
# @decorator
# def monster_pool_info(request):
#     """修改--活动怪池"""
#     if request.method == 'GET':
#         year_url = '/v2/shell/year_monster_pool_query'
#         dragon_url = '/v2/shell/activity/dragon_boat'
#         year_context,dragon_context = {}, {"pid": 3}
#         phone = request.session.get('uid')
#         year_msg, year_info = Context.get_server_data(year_url,year_context,phone)
#         dragon_msg, dragon_info = Context.get_server_data(dragon_url, dragon_context, phone)
#         if year_msg and dragon_msg:
#             year_count = year_info
#             dragon_count = dragon_info
#         elif not year_msg and dragon_msg:
#             year_count = 0
#             dragon_count = dragon_info
#         elif year_msg and not dragon_msg:
#             year_count = year_info
#             dragon_count = 0
#         else:
#             year_count = 0
#             dragon_count = 0
#
#         MonsterPool.objects.all().delete()
#         MonsterPool.objects.create(
#             year_pool=year_count,
#             dragon_boat_pool=dragon_count,
#         )
#         return render(request, 'run_manage/nian_pool_point.html', {"nian_count":year_count,"dragon_count":dragon_count})
#     else:
#         dic = request.POST
#         old_data = MonsterPool.objects.all().values('year_pool', 'dragon_boat_pool').first()
#         year_pool = old_data.get("year_pool", 0)
#         dragon_boat_pool = old_data.get("dragon_boat_pool", 0)
#         phone = request.session.get('uid')
#
#         pid = int(dic.get("pid").encode('utf-8'))
#         if pid == 1:
#             show = "金猪池"
#             year_count = int(dic.get("nian_count"),0)
#             oper_type,operation_data = show,year_count
#             new_year_count = year_count - int(year_pool)
#             url = '/v2/shell/year_monster_pool_modify'
#             context = {"ret": new_year_count}
#         else:
#             show = "龙舟怪池"
#             dragon_boat = int(dic.get("dragon_boat", 0))
#             oper_type,operation_data = show,dragon_boat
#             new_dragon_boat = dragon_boat - int(dragon_boat_pool)
#             url = '/v2/shell/activity/dragon_boat'
#             context = {"ret": new_dragon_boat,"pid": 4}
#
#         msg, result = Context.get_server_data(url, context, phone)
#         if msg:
#             nian_record_info(request,{"oper_type": oper_type, "operation_data": "数量:{}".format(operation_data)})
#             code = msg
#             info = "{}设置成功!".format(show)
#         else:
#             code = msg
#             info = "{}设置失败!".format(show)
#         return JsonResponse({'code': code, 'info': info})


# ==========================邮件总览==============================

@decorator
def query_mail_info(request):
    phone, url_date, number = request.session.get('uid'), "/run_manage/query_mail_info/", 1
    mail_list = Data_Info.get_mail_status()  # 筛选条件
    give_reward = Activity_Info.give_props_data()  # 道具
    weapon_list = Activity_Info.give_weapon_data()  # 武器
    give_reward.extend(weapon_list)

    user_limit = Context.get_user_limit(phone)  # 获取管理员权限
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page:
            conf, mail_info = get_mail_info(phone)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            mail_info.update({"number": number, "page": page})
        else:
            end_day = datetime.date.today().strftime('%Y-%m-%d')
            mail_info = {"start_day": end_day, "end_day": end_day, "number": number, "page": []}
    else:
        dic = request.POST
        status = int(dic.get("status"))
        start_time = dic.get("start_time")[:10]
        end_time = dic.get("stop_time")[:10]

        mail_info = {"start_day": start_time, "end_day": end_time, "status": status}
        keys = 'send_mail:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, mail_info)

        start_date = Time.str_to_datetime(start_time + " 00:00:00")
        end_date = Time.str_to_datetime(end_time + " 23:59:59")

        if status == 0:
            res_info = MailGeneral.objects.filter(create_time__range=[start_date, end_date]).order_by("-create_time")
        else:
            res_info = MailGeneral.objects.filter(create_time__range=[start_date, end_date], status=status).order_by("-create_time")
        paginator = Paginator(res_info, 30)
        page, plist = Context.paging(paginator, 1)
        mail_info.update({"number": number, "page": page})
    mail_info.update({"url_date": url_date, "mail_info": mail_list, "user_limit": user_limit, "give_reward":give_reward,"give_list":Context.json_dumps(give_reward)})
    return render(request, 'run_manage/send_mail.html', mail_info)


@decorator
def insert_mail_info(request):
    phone = request.session.get('uid')
    dic = request.POST
    mail_type = int(dic.get('mail_type'))
    user_id = dic.get('player_id')
    all_serve = dic.get('all_server')  # 0 全服邮件 1 个人邮件
    subject = dic.get("subject")  # 邮件标题
    reason = dic.get("reason")  # 发放缘由

    if mail_type == 0:
        reward_info = dic.get("mail_content").encode('utf-8')  # 邮件内容
    else:
        # bound_list = dic.getlist("bound")  # 锁定状态 1 锁定 2 未锁定
        reward_name = dic.getlist("reward_name")
        reward_number = dic.getlist("reward_number")
        barrel_day = dic.getlist("barrel_day")

        gift_name, gift_number = [], []
        for g_name, g_value in zip(reward_name, reward_number):
            g_value = g_value.encode('utf-8')
            if g_value == "":
                continue
            else:
                g_name = g_name.encode('utf-8')
                gift_name.append(g_name)
                gift_number.append(g_value)
        if len(gift_name) != len(set(gift_name)):
            info, msg = "奖励内容数据重复!", False
            return JsonResponse({'code': msg, 'info': info})
        print("--------gift_name------------", gift_name, gift_number, barrel_day)
        reward = ProcessInfo.deal_props_reward(gift_name, gift_number, barrel_day)
        if isinstance(reward, list):
            reward_info = reward[0]
        else:
            reward_info = reward
        print("--------reward_info------------", reward_info)

    sender, send_type, recipients = get_login_name(phone), (0 if all_serve else 1), ("全服" if all_serve else user_id)
    MailGeneral.objects.create(
        create_time=datetime.datetime.now(),
        mail_type=mail_type,
        nType=send_type,
        sender=sender,  # 发件人
        recipients=recipients,  # 收件人
        subject=subject,  # 邮件标题
        reason=reason,  # 发放缘由
        reward=reward_info,  # 奖品内容
        status=1,  # 审核状态
    )
    record_data = {"status_type": "生成邮件", "grant_type": recipients, "info": reward_info}
    insert_record_data(phone, MailRecord, record_data)
    info, msg = "邮件已经生成请管理员审核!", True
    return JsonResponse({'code': msg, 'info': info})


def get_user_limit(phone):
    user_date = LoginInfo.objects.filter(phone=phone).values('nid')
    nid = user_date[0].get("nid")
    user = Account.objects.filter(nid=nid, phone=phone).values("control_list").first()
    if user:
        control_info = Context.json_loads(user.get("control_list"))
        control_list = [str(n) for n in control_info]
    else:
        control_list = []
    return control_list


def get_mail_info(phone):
    """邮件"""
    keys = 'send_mail:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day", "status"])  # 筛选条件
    start_time, end_time, status = result[0], result[1], int(result[2])
    def_info = {"start_day": start_time, "end_day": end_time, "status": status}
    start_date = Time.str_to_datetime(start_time + " 00:00:00")
    end_date = Time.str_to_datetime(end_time + " 23:59:59")
    if status == 0:
        res_info = MailGeneral.objects.filter(create_time__range=[start_date, end_date]).order_by("-create_time")
    else:
        res_info = MailGeneral.objects.filter(create_time__range=[start_date, end_date], status=status).order_by("-create_time")
    return res_info, def_info


@decorator
def alter_mail_status(request):
    """修改--邮件审核状态"""
    phone = request.session.get('uid')
    update_time = Time.current_time('%Y-%m-%d %H:%M:%S')
    dic = request.POST
    mid = dic.get("mid")
    verifier = get_login_name(phone)
    result = MailGeneral.objects.filter(id=mid).values("nType", "mail_type", "recipients", "subject", "reward", "reason").first()
    send_type = int(result.get("nType"))
    mail_type = int(result.get("mail_type"))
    recipients = result.get("recipients")
    subject = result.get("subject")
    tl = result.get("reward")
    # reason = result.get("reason")
    if mail_type == 0:
        mail_led = tl.encode('utf-8').replace("\\n", "\n")
        if send_type == 1:
            context = {'t': send_type, "r":  {"tips": mail_led}, "u": int(recipients), "tl": subject}
        else:
            context = {'t': send_type, "r": {"tips": mail_led}, "u": 0, "tl": subject}
    else:
        if send_type == 1:
            context = {'t': send_type, "r":  eval(tl), "u": int(recipients), "tl": subject}
        else:
            context = {'t': send_type, "r": eval(tl), "u": 0, "tl": subject}

    print("--------context2020--------", context)
    record_data = {"status_type": "发送邮件", "grant_type": recipients, "verifier_user": verifier, "info": tl}
    insert_record_data(phone, MailRecord, record_data)
    url = '/v1/shell/gm/reward/add_mail'
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    if ret.status_code == 200:
        info, code = "邮件发送成功!", True
        MailGeneral.objects.filter(id=mid).update(status=2, verifier=verifier, verifier_time=update_time)
    else:
        info, code = "邮件发送失败!", False
    mail_info = {'code': code, 'info': info, "verifier": verifier, "update_time": update_time}
    return JsonResponse(mail_info)


def get_login_name(phone):
    result = LoginInfo.objects.filter(phone=phone).values("account_name").first()
    account_name = result.get("account_name")
    return account_name

# ==========================广播总览==============================
@decorator
def send_broadcast(request):
    phone = request.session.get('uid')
    dic = request.POST
    stamp_id = dic.get('stamp_id')
    if stamp_id:
        led = dic.get('led')
        broad_type = str(dic.get('broad_type'))
        broadcast_id = int(stamp_id)
        context = {'keys': int(stamp_id)}
        broad_info = "删除广播"
        BroadcastData.objects.filter(broadcast_id=broadcast_id).delete()
        broad_name = ("普通广播" if broad_type == "0" else "循环广播")
        record_data = {"status_type": broad_info, "broad_name": broad_name, "info": "广播内容:{}".format(led)}
        insert_record_data(phone, BroadcastRecord, record_data)
    else:
        send_type = int(dic.get('ntype'))
        bulletin = int(dic.get('bulletin'))  # 发布范围
        start_hour = dic.get('day_start').encode('utf-8')[:16] + ":00"
        led = dic.get('led')
        start_time = Context.Time.str_to_timestamp(start_hour)
        if send_type == 1:
            broad_name = "普通广播"
            context = {'start': start_time, 'end': start_time, 'led': led, "bulletin": bulletin, "interval": 0}
        else:
            broad_name = "循环广播"
            end_hour = dic.get('day_end').encode('utf-8')[:16] + ":00"
            stop_time = Context.Time.str_to_timestamp(end_hour)
            interval = int(dic.get('interval'))  # 重复间隔
            context = {'start': start_time, 'end': stop_time, 'led': led, "bulletin": bulletin, "interval": interval * 60}

        record_data = {"status_type": "发送广播", "info": "广播内容:{}".format(led), "broad_name": broad_name}
        insert_record_data(phone, BroadcastRecord, record_data)
        broad_info = "广播发送"
    url = '/v2/shell/gm/broadcast_set'
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    if ret.status_code == 200:
        info = "{}成功！".format(broad_info)
        msg = True
    else:
        info = "{}失败！".format(broad_info)
        msg = False
    return JsonResponse({'code': msg, 'info': info})


@decorator
def query_broadcast(request):
    """广播总览"""
    number, url_date, phone = 1, "/run_manage/query_broadcast/", request.session.get('uid')
    very_day = datetime.date.today().strftime('%Y-%m-%d %H:%M:%S')
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page:
            conf, query_info = get_broadcast_info(phone)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            query_info.update({"number": number, "page": page})
        else:
            end_day = datetime.date.today().strftime('%Y-%m-%d')
            query_info = {"start_day": end_day, "end_day": end_day, "number": number, "page": []}
    else:
        dic = request.POST
        start_day = dic.get('start_time').encode('utf-8')[:10]
        end_day = dic.get('stop_time').encode('utf-8')[:10]

        url = '/v2/shell/gm/broadcast_query'
        context = {"phone": phone}
        ret = Context.Controller.request(url, context)
        ret_dict = Context.json_loads(ret.text)
        if len(ret_dict) < 1 or "ret" not in ret_dict:
            query_info = {"start_day": end_day, "end_day": end_day, "number": number, "page": []}
        else:
            broadcast_info = ret_dict["ret"]
            query_info = {"start_day": start_day, "end_day": end_day}
            keys = 'broadcast:{}:{}'.format(phone, 'query')
            Context.RedisMatch.hash_mset(keys, query_info)
            broadcast_list = []
            for key, value in broadcast_info.items():
                day_time = int(key) / 1000
                value.update({"stamp_id": key, "day_time": day_time, "start": Time.timestamp_to_str(int(value["start"])),"end": Time.timestamp_to_str(int(value["end"]))})
                broadcast_list.append(value)

            create_broadcast_data(broadcast_list)
            start_stamp = Time.str_to_timestamp(start_day + " 00:00:00")
            end_stamp = Time.str_to_timestamp(end_day + " 23:59:59")

            res_info = BroadcastData.objects.filter(day_time__range=(start_stamp, end_stamp)).values('json_data').order_by("-day_time")
            sorted_list = []
            for info in res_info:
                sorted_list.append(json.loads(info.get("json_data")))
            paginator = Paginator(sorted_list, 30)
            page, plist = Context.paging(paginator, 1)  # 翻页
            query_info.update({"number": number, "page": page})
    query_info.update({"url_date": url_date, "very_day": very_day})
    return render(request, 'run_manage/broadcast_General.html', query_info)


def get_broadcast_info(phone):
    """获取广播信息"""
    keys = 'broadcast:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day"])  # 筛选条件
    start_time, end_time = result[0], result[1]
    def_info = {"start_day": start_time, "end_day": end_time}
    start_stamp = Time.str_to_timestamp(start_time + " 00:00:00")
    end_stamp = Time.str_to_timestamp(end_time + " 23:59:00")

    res_info = BroadcastData.objects.filter(day_time__range=(start_stamp, end_stamp)).values('json_data').order_by("-day_time")
    sorted_list = []
    for info in res_info:
        sorted_list.append(json.loads(info.get("json_data")))
    return sorted_list, def_info


def create_broadcast_data(result):
    """广播--总览"""
    broad_data = []
    for m_info in result:
        day_time = int(m_info["day_time"])
        interval = int(m_info["interval"])
        broadcast_id = int(m_info["stamp_id"])
        broadcast_type = (1 if interval == 0 else 0)
        res = BroadcastData.objects.filter(day_time=day_time)
        if res:
            BroadcastData.objects.filter(day_time=day_time).update(
                broadcast_id=broadcast_id,
                broadcast_type=broadcast_type,
                day_time=day_time,
                json_data=json.dumps(m_info),
            )
        else:
            new_broad = BroadcastData(
                broadcast_id=broadcast_id,
                broadcast_type=broadcast_type,
                day_time=day_time,
                json_data=json.dumps(m_info),
            )
            broad_data.append(new_broad)

        if len(broad_data) > 1000:
            BroadcastData.objects.bulk_create(broad_data)
            broad_data = []
    BroadcastData.objects.bulk_create(broad_data)

# ==========================公告总览==============================

@decorator
def proclamation_general(request):
    """公告总览"""
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info['0']
    del chanel_info['1000']
    phone = request.session.get('uid')
    if request.method == "GET":
        dic = request.GET
        channel = dic.get('channel', "1001_0").encode("utf-8")
        url = '/v2/shell/gm/reward/get_notice'
        context = {"phone": phone,"cid":channel}
        ret = Context.Controller.request(url, context)
        config = Context.json_loads(ret.content)
        notice_info = {"chanel_info":chanel_info}
        if "ret" not in config:
            notice_info.update({"page":[],"channel":channel})
            return render(request, 'run_manage/proclamation_general.html', notice_info)
        else:
            if not config["ret"].has_key("c"):
                notice_info.update({"page": [],"channel":channel})
                return render(request, 'run_manage/proclamation_general.html', notice_info)
            else:
                notice = config["ret"]["c"]
                notice_info.update({"page": notice,"channel":channel})
                return render(request, 'run_manage/proclamation_general.html', notice_info)
    else:
        if request.method == 'POST':
            dic = request.POST
            channel = dic.get('channel').encode("utf-8")
            files = request.FILES.get('select_file')
            excel_type = files.name.split('.')[1]
            if excel_type in ['xlsx', 'xls']:
                upload_path = settings.MEDIA_ROOT + "/upload_files"
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)
                file_name = settings.MEDIA_ROOT + "/upload_files/" + files.name
                with open(file_name, 'wb') as f:
                    for c in files.chunks():
                        f.write(c)
                f.close()
                df = pd.read_excel(file_name)
                deal_list = []
                for i in df.index.values:
                    row_data = df.loc[i, ['title', 'data', 'channel']].to_dict()
                    # print("最终获取数据：{0}".format(row_data))
                    deal_list.append(row_data)

                result = import_xls_data(deal_list, channel)
                if result:
                    reward = []
                    for info in deal_list:
                        title = info['title']
                        content = info['data']
                        reward.append([title, content])

                    url = '/v1/shell/gm/reward/add_notice'
                    context = {"phone": phone, 'cid': channel, 'c': reward}
                    ret = Context.Controller.request(url, context)
                    if ret.status_code == 200:
                        info = "公告信息发布成功！"
                        status = True
                    else:
                        info = "公告信息发布失败！"
                        status = False
                    return JsonResponse({'msg': info, "status": status})
                else:
                    return JsonResponse({'msg': '上传数据不能为空!', "status": False})
            else:
                return JsonResponse({'msg': '上传文件类型错误', "status": False})
        else:
            return JsonResponse({'msg': '请求方式错误!', "status": False})


def import_xls_data(notice_info, channel):
    """插入xls--数据"""
    notice_list = []
    # Notice.objects.all().delete() # 删除数据
    insert_time = Time.current_time('%Y-%m-%d %H:%M:%S')
    for info in notice_info:
        # channel_list = []
        title, content = info["title"], info["data"]
        if not isinstance(title, float) and not isinstance(content, float):
            # channel = channel_str.encode('utf-8')
            # channel_info = channel_str.split(",")
            # for channel in channel_info:
            #     channel = channel.encode('utf-8')
            #     channel_list.append(channel)
            result = Notice.objects.filter(title=title, channel=channel).first()
            if result:
                Notice.objects.filter(title=title, channel=channel).update(
                    day_time=Time.current_time('%Y-%m-%d'),
                    insert_time=insert_time,
                    channel=channel,
                    title=title,
                    content=content,
                )
            else:
                new_info = Notice(
                    day_time=Time.current_time('%Y-%m-%d'),
                    insert_time=insert_time,
                    channel=channel,
                    title=title,
                    content=content,
                )
                notice_list.append(new_info)
        else:
            return False
    Notice.objects.bulk_create(notice_list)
    return True

# ==========================充值加赠==============================
@decorator
def recharge_add_gift(request):
    """充值加赠"""
    if request.method == "GET":
        url = '/v2/shell/gm/recharge/get_add'
        context = {}
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.content)
        if "ret" not in gift:
            return render(request, 'run_manage/recharge_add_gift.html', {"info_dict": {}})
        else:
            recharge = gift["ret"]
            del recharge['0']
            del recharge['1000']
            return render(request, 'run_manage/recharge_add_gift.html',{"info_dict":recharge})
    else:
        dic = request.POST  # 2 支付宝 1微信
        channel_info = dic.getlist("channel")
        wechat = dic.getlist("wechat")
        alipay = dic.getlist("alipay")

        old_data = ChannelList.objects.all().values('channel_data').first()
        chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道

        gift_info = {}
        for index, channel in enumerate(channel_info):
            if channel in chanel_info:
                new_channel = chanel_info[channel]
            else:
                new_channel = channel
            gift_info.update({new_channel:{"zhifubao":float(alipay[index])/100.0, "weixin": float(wechat[index])/100.0}})
        url = '/v2/shell/gm/recharge/add_gift'
        context = {'ret': gift_info}
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)
        if ret.status_code == 200:
            code = True
            msg = "充值加赠成功！"
        else:
            code = True
            msg = "充值加赠失败！"
        return JsonResponse({'code': code, 'msg': msg})


# ==========================金币池配置==============================
@decorator
def coin_energy_config(request):
    phone = request.session.get('uid')
    url = '/v2/shell/gm/control_power_pool'
    if request.method == 'GET':
        pool_info = {}
        context = {"pid": 1, "phone": phone, "t": 1}
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.text)
        print("-------------gift", gift)
        if "info" not in gift or "value" not in gift:
            coin_list, power_list = [], []
            pool_info.update({"coin_list": coin_list, "power_list": power_list})
        else:
            config = gift["info"]
            if config:
                coin_list, power_list, coin_index, power_index = [], [], 1, 1
                for info in config:
                    room_type = int(info.get("room_type", 2))
                    if room_type == 2:
                        deal_info = copy.deepcopy(info)
                        deal_info.update({"index": coin_index})
                        coin_list.append(deal_info)
                        coin_index += 1
                    else:
                        deal_info = copy.deepcopy(info)
                        deal_info.update({"index": power_index})
                        power_list.append(deal_info)
                        power_index += 1
            else:
                coin_list, power_list = [], []
            print("-0----------------", coin_list, power_list)
            pool_info.update({"coin_list": coin_list, "power_list": power_list})
        return render(request, 'run_manage/coin_energy_config.html', pool_info)
    else:
        dic = request.POST
        barrel_list, n = [], 4
        pid = int(dic.get("pid"))
        room_type = int(dic.get("room_type"))
        if room_type == 1:
            room = "鸟蛋场"
        else:
            room = "金币场"
        if pid == 2:  # 全服修改  正数：送分 负数：抽分
            start_list = dic.getlist("start_barrel")
            end_list = dic.getlist("end_barrel")
            rate_list = dic.getlist("rate")
            kill_list = dic.getlist("kill")
            total_list = dic.getlist("total")
            point_list = dic.getlist("point")
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
                    control.update({"room_type": room_type, "area": barrel_info, "rate": rate, "kill": kill, "total": total, "point": point})
                    all_control.append(control)

            print("---------all_control", all_control)

            for info in all_control:
                update_str = "{}-{}倍".format(info["area"][0], info["area"][1]) + "   " + "抽/送分的比率:{}".format(info["rate"]) + \
                             "   " + "控制概率纠正:{}".format(info["kill"]) + "   " + "抽/送分的额度:{}".format(info["total"]) + \
                             "   " + "最低分鸟控制:{}".format(info["point"])
                record_data = {"status_type": "设置{}炮倍池".format(room), "info": update_str}
                insert_record_data(phone, "----", record_data)

            context = {'phone': phone, 'pid': pid, 't': 1, 'ac': all_control}  # t:1 全服 2 个人
            ret = Context.Controller.request(url, context)
            if ret.status_code == 200:
                status = True
                msg = "{}炮倍池设置成功!".format(room)
            else:
                status = False
                msg = "{}炮倍池设置失败!".format(room)
            return JsonResponse({"status": status, "info": msg})
        else:  # 删除
            barrel_info = dic.get("barrel_list").encode("utf-8").split(",", 1)
            barrel_1, barrel_2 = int(barrel_info[0]), int(barrel_info[1])

            update_str = "{}-{}倍".format(barrel_1, barrel_2)
            record_data = {"status_type": "设置{}炮倍池".format(room), "info": update_str}
            insert_record_data(phone, "----", record_data)

            context = {'phone': phone, 'pid': 3, 't': 1, 'area1': barrel_1, 'area2': barrel_2, "room_type": room_type}  # t:1 全服 2 个人
            ret = Context.Controller.request(url, context)
            result = Context.json_loads(ret.content)
            if "t" in result:
                status = True
                msg = "{}-{}倍删除成功!".format(barrel_info[0], barrel_info[1])
            else:
                status = False
                msg = "{}-{}倍删除失败!".format(barrel_info[0], barrel_info[1])
            return JsonResponse({"status": status, "info": msg})


# ==========================房间池控制配置==============================
@decorator
def room_control_config(request):
    phone = request.session.get('uid')
    url = '/v2/shell/gm/room_control_config'
    if request.method == 'GET':
        pool_info = {}
        context = {"pid": 1, "phone": phone}
        ret = Context.Controller.request(url, context)
        room_pool = Context.json_loads(ret.text)
        # print("-------------room_pool", room_pool)
        if "res" not in room_pool:
            zero_list, one_list, two_list, three_list = [], [], [], []
        else:
            zero_list, one_list, two_list, three_list = [], [], [], []
            config = room_pool["res"]
            for site, room_info in config.items():
                site = str(site)
                if site == "400":
                    for rid, value in room_info.items():
                        value.update({"room_id": rid})
                        zero_list.append(value)
                elif site == "401":
                    for rid, value in room_info.items():
                        value.update({"room_id": rid})
                        one_list.append(value)
                elif site == "402":
                    for rid, value in room_info.items():
                        value.update({"room_id": rid})
                        two_list.append(value)
                else:
                    for rid, value in room_info.items():
                        value.update({"room_id": rid})
                        three_list.append(value)
        pool_info.update({"zero_list": zero_list, "one_list": one_list, "two_list": two_list, "three_list": three_list})
        return render(request, 'run_manage/room_pool_config.html', pool_info)
    else:
        dic = request.POST
        room, table = int(dic.get("room")), int(dic.get("table"))
        table_pool = int(dic.get("table_pool"))
        add_pool = int(dic.get("add_pool"))
        context = {'phone': phone, 'pid': 2, 'room': room, 'table': table, 'add_pool': add_pool}
        room_name = ("刺激战场-体验场" if room == 400 else "刺激战场-猎龙峡谷" if room == 401 else "刺激战场-绝境炼狱" if room == 402 else "刺激战场-极度魔界")
        record_str = "{}_房间池额度:{}_添加额度:{}".format(room_name, table_pool, add_pool)
        record_data = {"status_type": "修改{}房间池额度".format(table), "info": record_str}
        insert_record_data(phone, PowerPoolRecord, record_data)
        print("----context2020----", context)
        ret = Context.Controller.request(url, context)
        result = Context.json_loads(ret.content)
        if "res" in result:
            status, msg = True, "修改成功!"
        else:
            status, msg = False, "修改失败!"
        return JsonResponse({"status": status, "msg": msg})


def insert_channel_cost(phone, start_time, end_time):
    """查询服务器 将每一天每个渠道的成本存进数据库 """
    day_time = datetime.datetime.now().strftime('%Y-%m-%d')
    screen_info, input_data = "", ""
    res = ExchangeInfo.objects.filter(day_time=end_time).first()
    if not res:
        insert_redis_exchange(phone, start_time, end_time, screen_info, input_data)
        add_channel_cost(phone, end_time)
    else:
        if end_time == day_time:
            insert_redis_exchange(phone, start_time, end_time, screen_info, input_data) #今天
            add_channel_cost(phone, end_time)
        else:
            add_channel_cost(phone,end_time)


def add_channel_cost(phone,day_time):
    day_info,all_channel = {},0
    channel_list = ExchangeInfo.objects.filter(day_time=day_time).values("channel", "json_data")
    if channel_list:
        for u_info in channel_list:
            channel = u_info.get("channel",0)
            json_info = Context.json_loads(u_info.get("json_data", {}))
            c_status = int(json_info["stat"])
            shop_cost, good_type = int(json_info["cost"]), int(json_info["good_type"])
            if c_status == 2 and (good_type != 3 or good_type != 5):
                day_info[channel] = day_info.get(channel, 0) + shop_cost
                all_channel += shop_cost
    else:
        day_record = Context.RedisCache.hget_keys('day_shop_record:{}:{}:*:*'.format(phone, day_time))
        for key in day_record:
            result = Context.RedisCache.hash_getall(key)
            channel = result.get("channelid", "0")
            c_status = int(result.get("stat", 0))
            shop_cost, good_type = int(result.get("cost", 0)), int(result.get("good_type", 0))
            if c_status == 2 and (good_type != 3 or good_type != 5):
                day_info[channel] = day_info.get(channel, 0) + shop_cost
                all_channel += shop_cost

    day_info.update({"1000": all_channel})

    cost_list = []
    res = ChannelCost.objects.filter(query_day=day_time)
    if res:
        ChannelCost.objects.filter(query_day=day_time).update(
            query_day=day_time,
            json_data=Context.json_dumps(day_info),
        )
    else:
        new_data = ChannelCost(
            query_day=day_time,
            json_data=Context.json_dumps(day_info),
        )
        cost_list.append(new_data)

    ChannelCost.objects.bulk_create(cost_list)


# ==========================邮件一键发送==============================
# @decorator
# def one_key_send(request):
#     if request.method == 'GET':
#         return render(request,'run_manage/one_key_send.html')
#
#     elif request.method == 'POST':
#         dic = request.POST
#         upload_name = dic.get("file_name")
#         url = '/v1/shell/gm/reward/add_mail'
#         file_name = settings.MEDIA_ROOT + "/upload_files/" + upload_name
#         status = True
#         fo = open(file_name, "r")
#         uid = 0
#         for line in fo.readlines():
#             try:
#                 uid = int(line)
#                 if uid <= 1000000 or uid > 9999999:
#                     status = False
#                     break
#             except:
#                 uid = line
#                 status = False
#                 break
#             context = {'t': 1,'r': {'chip': 50000},'u': uid,'tl': u"端午活跃大赠送"}
#             context.update({"phone": request.session.get('uid')})
#             ret = Context.Controller.request(url, context)
#             result = Context.json_loads(ret.text)
#             if ret.status_code != 200:
#                 status = False
#                 break
#         if status:
#             msg = "邮件发送成功!"
#         else:
#             msg = "邮件发送失败!"
#         return JsonResponse({"status": status,"msg":msg,'error_uid': uid})

# ==========================邮件一键上传玩家ID==============================
# @decorator
# def upload_user_id(request):
#     phone = request.session.get('uid')
#     if request.method == 'GET':
#         return render(request, 'run_manage/one_key_send.html')
#
#     elif request.method == 'POST':
#         dic = request.POST
#         upload_name = dic.get("file_name")
#         file_name = settings.MEDIA_ROOT + "/upload_files/" + upload_name
#         import pandas as pd
#         df = pd.read_excel(file_name)
#         deal_list = []
#         for i in df.index.values.tolist():
#             row_data = df.loc[i, ['user_id']][0]
#             deal_list.append(row_data)
#         print("最终获取到的数据是：{0}".format(deal_list))
#
#         url = '/v2/shell/gm/user_insert_redis'
#         context = {'phone': phone, 'user_list': deal_list}
#         ret = Context.Controller.request(url, context)
#         if ret.status_code == 200:
#             code = True
#             msg = "玩家ID成功！"
#         else:
#             code = True
#             msg = "玩家ID失败！"
#         return JsonResponse({'status': code, 'msg': msg})


# @decorator
# def upload_file(request):
#     if request.method == 'POST':
#         file_obj = request.FILES.get('file')
#         upload_path = settings.MEDIA_ROOT + "/upload_files"
#         if not os.path.exists(upload_path):
#             os.makedirs(upload_path)
#         file_name = settings.MEDIA_ROOT + "/upload_files/" + file_obj.name
#         with open(file_name, 'wb') as f:
#             for c in file_obj.chunks():
#                 f.write(c)
#         f.close()
#
#         upload_name = file_obj.name
#         msg = "上传成功!"
#         status = True
#     else:
#         msg = "上传方式异常!"
#         status = False
#         upload_name = ""
#     return JsonResponse({"status": status, "msg": msg,"file_name":upload_name})


@decorator
def early_warning_signal(request):
    phone = request.session.get('uid')
    pay_list = Data_Info.get_user_pay_total()
    url = '/v2/shell/gm/deal_white_list'
    context = {'phone': phone, 'pid': 1, 'user_status': 1}
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.text)
    if "info" not in config:
        user_list = []
    else:
        if config["info"]:
            user_list = config["info"]
        else:
            user_list = []
    res_over = EarlyWarning.objects.filter(user_status=3).values("user_list").first()
    if res_over:
        player_list = Context.json_loads(res_over.get("user_list", []))
    else:
        player_list = []
    for uid in user_list:
        if uid not in player_list:
            _, _, _ = add_forbid(phone, uid, 3)
        else:
            continue

    if request.method == 'GET':
        res_over = EarlyWarning.objects.filter(user_status=1).values("user_list", "user_length").first()
        if res_over:
            o_list = Context.json_loads(res_over.get("user_list", []))
            o_length = res_over.get("user_length", 0)
        else:
            o_list, o_length = [], 0
        res_for = EarlyWarning.objects.filter(user_status=3).values("user_list", "user_length").first()
        if res_for:
            f_list = Context.json_loads(res_for.get("user_list", []))
            f_length = res_for.get("user_length", 0)
        else:
            f_list, f_length = [], 0
        early_info = {"o_list": o_list, "o_leg": o_length, "f_list": f_list, "f_leg": f_length, "pay_list": pay_list}
        return render(request, 'run_manage/early_warning_signal.html', early_info)
    else:
        dic = request.POST
        pid = int(dic.get('pid'))
        if pid == 1:  # 添加预警忽略ID
            o_uid = int(dic.get('o_id'))
            status, msg, o_length = add_overlook(phone, o_uid, pid)
        elif pid == 2:  # 删除预警忽略ID
            o_uid = int(dic.get('o_id'))
            status, msg, o_length = del_overlook(phone, o_uid, 1)
        elif pid == 3:   # 添加禁止发货ID
            o_uid = int(dic.get('f_id'))
            status, msg, o_length = add_forbid(phone, o_uid, pid)
        elif pid == 4:  # 删除禁止发货ID
            o_uid = int(dic.get('f_id'))
            status, msg, o_length = del_forbid(phone, o_uid, 3)
        else:
            o_uid, status, point = int(dic.get('user_id')), int(dic.get('status')), int(dic.get('point'))
            o_length = 0
            url = '/v2/shell/gm/deal_white_list'
            context = {'phone': phone, 'pid': 4, "uid": o_uid, "status": status, "point": point}
            ret = Context.Controller.request(url, context)
            config = Context.json_loads(ret.text)
            if "ret" in config:
                status = True
                msg = "添加额度成功!"
            else:
                status = False
                msg = "服务器添加数据异常!"
        return JsonResponse({"status": status, "msg": msg, "uid": o_uid, "leg": o_length})


def add_overlook(phone, o_uid, pid):
    overlook_list = []
    res_for = EarlyWarning.objects.filter(user_status=3).values("user_list", "user_length").first()
    if res_for:
        f_list = Context.json_loads(res_for.get("user_list", []))
    else:
        f_list = []

    res = EarlyWarning.objects.filter(user_status=pid).values("user_list", "user_length").first()
    if res:
        over_list = res.get("user_list", [])
        over_leg = res.get("user_length", 0)
        o_list = Context.json_loads(over_list)
        o_length = over_leg
        if o_uid not in o_list and o_uid not in f_list:
            o_list.append(o_uid)
            o_length = len(o_list)
            EarlyWarning.objects.filter(user_status=pid).update(
                user_list=Context.json_dumps(o_list),
                user_length=o_length
            )
            status = True
            msg = "添加忽略预警ID成功!"
        else:
            status = False
            msg = "忽略预警ID已存在!"
    else:
        overlook_list.append(o_uid)
        o_length = len(overlook_list)
        EarlyWarning.objects.create(
            user_status=pid,
            user_list=Context.json_dumps(overlook_list),
            user_length=o_length
        )
        status = True
        msg = "添加忽略预警ID成功!"
    if status:
        record_data = {"status_type": "添加忽略预警ID", "uid": o_uid}
        insert_record_data(phone, EarlyRecord, record_data)
    return status, msg, o_length


def del_overlook(phone, uid, pid):
    res = EarlyWarning.objects.filter(user_status=pid).values("user_list", "user_length").first()
    o_list = Context.json_loads(res.get("user_list", []))
    o_length = res.get("user_length", 0)
    if uid in o_list:
        index = [i for i, x in enumerate(o_list) if x == uid][0]
        del o_list[index]
        o_length = len(o_list)
        EarlyWarning.objects.filter(user_status=pid).update(
            user_list=Context.json_dumps(o_list),
            user_length=o_length
        )
        record_data = {"status_type": "删除忽略预警ID", "uid": uid}
        insert_record_data(phone, EarlyRecord, record_data)
        status = True
        msg = "删除忽略预警ID成功!"
    else:
        status = False
        msg = "忽略预警ID不存在!"

    return status, msg, o_length


def add_forbid(phone, o_uid, pid):
    overlook_list, user_status = [], 2
    url = '/v2/shell/gm/deal_white_list'
    res_over = EarlyWarning.objects.filter(user_status=1).values("user_list", "user_length").first()
    if res_over:
        o_list = Context.json_loads(res_over.get("user_list", []))
    else:
        o_list = []
    res = EarlyWarning.objects.filter(user_status=pid).values("user_list", "user_length").first()
    if res:
        for_list = res.get("user_list", [])
        for_leg = res.get("user_length", 0)
        f_list = Context.json_loads(for_list)
        f_length = for_leg
        if o_uid not in f_list and o_uid not in o_list:
            f_list.append(o_uid)
            f_length = len(f_list)
            context = {'phone': phone, 'pid': 1, 'user_list': f_list, "user_status": user_status}
            ret = Context.Controller.request(url, context)
            config = Context.json_loads(ret.text)
            if "ret" in config:
                EarlyWarning.objects.filter(user_status=pid).update(
                    user_list=Context.json_dumps(f_list),
                    user_length=f_length
                )
                status = True
                msg = "添加禁止发货ID成功!"
            else:
                status = False
                msg = "服务器添加数据异常!"
        else:
            status = False
            msg = "禁止发货ID已存在!"
    else:
        overlook_list.append(o_uid)
        f_length = len(overlook_list)
        context = {'phone': phone, 'pid': 1, 'user_list': overlook_list, "user_status": user_status}
        ret = Context.Controller.request(url, context)
        config = Context.json_loads(ret.text)
        if "ret" in config:
            EarlyWarning.objects.create(
                user_status=pid,
                user_list=Context.json_dumps(overlook_list),
                user_length=f_length
            )
            status = True
            msg = "添加禁止发货ID成功!"
        else:
            status = False
            msg = "服务器添加数据异常!"

    if status:
        record_data = {"status_type": "添加禁止发货ID", "uid": o_uid}
        insert_record_data(phone, EarlyRecord, record_data)

    return status, msg, f_length


def del_forbid(phone, uid, pid):
    res = EarlyWarning.objects.filter(user_status=pid).values("user_list", "user_length").first()
    o_list = Context.json_loads(res.get("user_list", []))
    o_length = res.get("user_length", 0)
    if uid in o_list:
        index = [i for i, x in enumerate(o_list) if x == uid][0]
        del o_list[index]
        o_length = len(o_list)
        url = '/v2/shell/gm/deal_white_list'
        context = {'phone': phone, 'pid': 1, 'user_list': o_list, "user_status": 2}
        ret = Context.Controller.request(url, context)
        config = Context.json_loads(ret.text)
        if "ret" in config:
            EarlyWarning.objects.filter(user_status=pid).update(
                user_list=Context.json_dumps(o_list),
                user_length=o_length
            )
            status = True
            msg = "删除禁止发货ID成功!"
            record_data = {"status_type": "删除禁止发货ID", "uid": uid}
            insert_record_data(phone, EarlyRecord, record_data)
        else:
            status = False
            msg = "服务器删除数据异常!"
    else:
        status = False
        msg = "禁止发货ID不存在!"

    return status, msg, o_length


@decorator
def look_record(request):
    url_date = "/run_manage/all_record/"
    index, number = 1, 1
    dic = request.GET
    pid = dic.get('pid').encode('utf-8')
    one_page = dic.get('page')
    if pid == "broadcast_record":
        result_list = BroadcastRecord.objects.all().values("insert_time", "login_user", "record_data").order_by("-insert_time")
    elif pid == "mail_record":
        result_list = MailRecord.objects.all().values("insert_time", "login_user", "record_data").order_by("-insert_time")
    elif pid == "power_pool_control":
        result_list = PowerPoolRecord.objects.all().values("insert_time", "login_user", "record_data").order_by("-insert_time")
    else:
        result_list = EarlyRecord.objects.all().values("insert_time", "login_user", "record_data").order_by("-insert_time")

    if one_page:
        one_page = int(one_page.encode('utf-8'))
        number, index = one_page, one_page

    record_list = []
    for info in result_list:
        insert_time, login_user = info.get("insert_time"), info.get("login_user")
        record_data = Context.json_loads(info.get("record_data"))
        record_data.update({"insert_time":insert_time, "login_user":login_user})
        record_list.append(record_data)

    paginator = Paginator(record_list, 30)
    page, plist = Context.paging(paginator, index)
    num_page = paginator.num_pages
    if one_page > num_page:
        number = num_page

    record_info = {'page': page, "number": number, "url_date": url_date, "pid": pid}
    return render(request, 'record/{}.html'.format(pid), record_info)


def insert_record_data(phone, Record, record_data):
    """操作记录"""
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    Record.objects.create(
        insert_time=insert_time,
        login_user=phone,
        record_data=Context.json_dumps(record_data),
    )
