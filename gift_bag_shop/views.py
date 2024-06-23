# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from xlwt import *
from io import BytesIO
import random
from util.process import ProcessInfo
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.http import JsonResponse,HttpResponse
from util.process import ProcessInfo
from util.gamedate import *
from login_manage.models import *
from gift_bag_shop.models import *
from login_manage.views import decorator
import datetime
from django.shortcuts import render_to_response, render, redirect
from util.context import Context
from util.tool import Time
from hashlib import sha1
from django.conf import settings
import os


@decorator
def gift_shop(request):
    """礼包商城"""
    old_data = ChannelList.objects.all().values('channel_data').first()
    channel_list = Context.json_loads(old_data['channel_data'])  # 渠道
    del channel_list['0']
    del channel_list['1000']
    give_reward = Activity_Info.give_props_data()  # 道具
    weapon_list = Activity_Info.give_weapon_data()  # 武器
    give_reward.extend(weapon_list)
    level_list = Shop.vip_grade()  # 商品vip等级
    gift_shop_type = Shop.gift_shop_type()
    hot_name = Activity_Info.get_hot_type()
    url_date = "/gift_bag_shop/gift_shop/"
    phone = request.session.get('uid')

    if request.method == "GET":
        one_pages = request.GET.get('page')
        day_time = datetime.date.today().strftime('%Y-%m-%d')
        range_list = range(0, 6)
        extra_list = range(0, 3)
        gift_info = {"channel_list": channel_list, "hot_name": hot_name, "range_list": range_list, "extra_list": extra_list, "give_reward": give_reward,"gift_shop_type": gift_shop_type, "vip_level": level_list, "url_date": url_date}
        if one_pages:
            one_pages = int(one_pages.encode('utf-8'))
            number, index = one_pages, one_pages
        else:
            index, number = 1, 1
        shop_list = GiftInfo.objects.all().order_by("online_state")
        paginator = Paginator(shop_list, 30)
        page, plist = Context.paging(paginator, index)
        num_page = paginator.num_pages
        if one_pages > num_page:
            number = num_page
        else:
            number = number
        gift_info.update({"start_day": day_time, "end_day": day_time, "number": number, "page": page})
        return render(request, 'gift_bag_shop/gift_info.html', gift_info)
    else:
        dic = request.POST
        pid = int(dic.get('pid'))
        if pid == 1:  # 更新礼包
            gift_online = int(dic.get('gift_online'))  # 1 上架 2下架
            if gift_online == 1:
                status = 2
            else:  # 2下架
                status = 1
            gift_conf, msg, info = update_gift_good(dic)
            if msg:
                gift_id = gift_conf["gift_id"]
                url = '/v2/shell/activity/gift_shop'
                del gift_conf["gift_id"]
                context = {"pid": status, "product_id": str(gift_id), "info": gift_conf, "phone": phone}
                ret = Context.Controller.request(url, context)
                game_info = Context.json_loads(ret.text)
                if "pid" not in game_info and "product_id" not in game_info:
                    info = "更新礼包失败!"
                    msg = False
                else:
                    open_type = int(gift_conf["open_type"])
                    update_gift_shop(open_type, gift_online, gift_id, gift_conf)
                    info = "更新礼包成功!"
                    msg = True
            else:
                info = info
                msg = msg
            return JsonResponse({'status': msg, 'show': info})
        elif pid == 2:  # 添加
            gift_conf, msg, info = add_gift_good(dic)
            if msg:
                url = '/v2/shell/activity/gift_shop'
                context = {"pid": pid, "info": gift_conf, "phone": phone}
                ret = Context.Controller.request(url, context)
                game_info = Context.json_loads(ret.text)
                if "pid" not in game_info and "product_id" not in game_info:
                    info = "礼包添加设置失败!"
                    msg = False
                else:
                    # gift_online = int(dic.get('add_gift_data'))
                    gift_id = game_info["product_id"]
                    open_type = int(gift_conf["open_type"])
                    create_gift_shop(open_type, 1, gift_id, gift_conf)
                    info = "礼包添加设置成功!"
                    msg = True
            else:
                info = info
                msg = msg
            return JsonResponse({'status': msg, 'info': info})
        elif pid == 3:  # 显示更新
            gift_id = dic.get('gift_id').encode('utf-8')
            result = GiftInfo.objects.filter(gift_id=gift_id).values("gift_id", "gift_name", "version_id", "hot",
                                                                     "index", "start_time", "end_time", "icon_type",
                                                                     "worth", "open_type", "limit_num", "vip_type",
                                                                     "vip_level", "detail_1", "detail_2", "price",
                                                                     "detail_3", "online_state", "reward", "skip",
                                                                     "add_time", "add_reward", "channel_list").first()
            if result:
                reward_list = ProcessInfo.deal_gift_reward(eval(result.get("reward")))
                len_reward = len(reward_list)
                for i in range(0, 5 - len_reward):
                    prop = {"option": "chip", "value": "", "name": "鸟蛋"}
                    reward_list.append(prop)
                vip_level = eval(result.get("vip_level"))
                channel_list = (eval(result.get("channel_list")) if result.get("channel_list") else [])
                start_time = Time.datetime_to_str(result.get("start_time"))
                end_time = Time.datetime_to_str(result.get("end_time"))
                gift_id = result.get("gift_id")
                gift_name = result.get("gift_name")
                hot = result.get("hot")
                skip = result.get("skip", "")
                index = result.get("index", 10000)
                icon_type = result.get("icon_type")
                price = result.get("price")
                worth = result.get("worth")
                limit_num = result.get("limit_num")
                vip_type = result.get("vip_type")
                detail_1 = result.get("detail_1")
                detail_2 = result.get("detail_2")
                detail_3 = result.get("detail_3")
                online_state = result.get("online_state")
                open_type = str(result.get("open_type"))
                gift_info = {"gift_id": gift_id, "gift_name": gift_name, "skip": skip, "index": index, "hot": hot, "icon_type": icon_type,
                             "price": price, "worth": worth, "open_type": open_type, "limit_num": limit_num, "vip_type": vip_type,
                             "detail_1": detail_1, "detail_2": detail_2, "detail_3": detail_3, "online_state": online_state,
                             "start_time": start_time, "end_time": end_time, "reward": reward_list, "vip_level": vip_level , "channel_list": channel_list}
                if open_type == "5":
                    add_reward = ProcessInfo.deal_gift_reward(eval(result.get("add_reward")))
                    add_time = result.get("add_time")
                    gift_info.update({"add_reward": add_reward, "add_time": add_time})

                msg = True
                show = "礼包显示成功!"
            else:
                msg = False
                show = "数据查询异常!"
                gift_info = {}
            gift_info.update({'status': msg, 'show': show})

            return JsonResponse(gift_info)
        else:  # 批量 1 上架 2下架
            gift_list = dic.getlist('gift_id')
            if gift_list:
                if pid == 4:
                    show = "礼包上架失败!"
                    msg = False
                    for gid in gift_list:
                        gift_conf, msg, show = gift_Racking(gid)
                        if msg:
                            status = 2
                            url = '/v2/shell/activity/gift_shop'
                            context = {"pid": status, "product_id": str(gid), "info": gift_conf, "phone": phone}
                            ret = Context.Controller.request(url, context)
                            game_info = Context.json_loads(ret.text)
                            if "pid" not in game_info and "product_id" not in game_info:
                                show = "礼包上架失败!"
                                msg = False
                            else:
                                show = "礼包上架成功!"
                                msg = True
                                open_type = int(gift_conf["open_type"])
                                update_gift_shop(open_type, 1, gid, gift_conf)
                        else:
                            show = show
                            msg = msg
                    return JsonResponse({'status': msg, 'info': show})
                else:
                    show = "礼包下架失败!"
                    msg = False
                    for gid in gift_list:
                        gift_conf, msg, show = gift_sold_out(gid)
                        if msg:
                            status = 1
                            url = '/v2/shell/activity/gift_shop'  # 1 下架  2 上架
                            context = {"pid": status, "product_id": str(gid), "info": gift_conf, "phone": phone}
                            ret = Context.Controller.request(url, context)
                            game_info = Context.json_loads(ret.text)
                            if "pid" not in game_info and "product_id" not in game_info:
                                show = "礼包下架失败!"
                                msg = False
                            else:
                                show = "礼包下架成功!"
                                msg = True
                                open_type = int(gift_conf["open_type"])
                                update_gift_shop(open_type, 2, gid, gift_conf)
                        else:
                            show = show
                            msg = msg
                    return JsonResponse({'status': msg, 'info': show})
            else:
                show = "请选择礼包!"
                msg = False
                return JsonResponse({'status': msg, 'info': show})


def create_gift_shop(open_type, online_state, gift_id, gift_conf):
    if open_type == 5:
        channel_list = gift_conf.get("channel", [])
        GiftInfo.objects.create(
            channel_list=channel_list,
            gift_id=gift_id,
            skip=gift_conf["skip"],
            gift_name=gift_conf["name"],
            version_id="1000",  # 版本号
            index=gift_conf["index"],  # 排序
            hot=gift_conf["hot"],  # 热度
            start_time=gift_conf["start"],  # 开启时间
            end_time=gift_conf["end"],  # 结束时间
            icon_type=gift_conf["icon_type"],  # icon类型
            price=gift_conf["price"],  # 价格
            worth=gift_conf["worth"],  # 价值
            open_type=gift_conf["open_type"],  # 开放类型
            limit_num=gift_conf["limit_num"],  # 限制数量
            vip_type=gift_conf["vip_type"],  # vip类型
            vip_level=gift_conf["vip_level"],  # vip 等级
            detail_1=gift_conf["detail_1"],
            detail_2=gift_conf["detail_2"],
            detail_3=gift_conf["detail_3"],
            online_state=online_state,  # 1 上架 2下架
            reward=gift_conf["reward"],
            add_time=gift_conf["add_time"],
            add_reward=gift_conf["add_reward"],
        )
    else:
        channel_list = gift_conf.get("channel", [])
        GiftInfo.objects.create(
            channel_list=channel_list,
            gift_id=gift_id,
            skip=gift_conf["skip"],
            gift_name=gift_conf["name"],
            version_id="1000",  # 版本号
            index=gift_conf["index"],  # 排序
            hot=gift_conf["hot"],  # 热度
            start_time=gift_conf["start"],  # 开启时间
            end_time=gift_conf["end"],  # 结束时间
            icon_type=gift_conf["icon_type"],  # icon类型
            price=gift_conf["price"],  # 价格
            worth=gift_conf["worth"],  # 价值
            open_type=gift_conf["open_type"],  # 开放类型
            limit_num=gift_conf["limit_num"],  # 限制数量
            vip_type=gift_conf["vip_type"],  # vip类型
            vip_level=gift_conf["vip_level"],  # vip 等级
            detail_1=gift_conf["detail_1"],
            detail_2=gift_conf["detail_2"],
            detail_3=gift_conf["detail_3"],
            online_state=online_state,  # 1 上架 2下架
            reward=gift_conf["reward"],
        )


def update_gift_shop(open_type, online_state, gift_id, gift_conf):
    if open_type == 5:
        channel_list = gift_conf.get("channel", [])
        GiftInfo.objects.filter(gift_id=gift_id).update(
            channel_list=channel_list,
            gift_id=gift_id,
            skip=gift_conf["skip"],
            gift_name=gift_conf["name"],
            version_id=gift_conf["version"],  # 版本号
            index=gift_conf["index"],  # 排序
            hot=gift_conf["hot"],  # 热度
            start_time=gift_conf["start"],  # 开启时间
            end_time=gift_conf["end"],  # 结束时间
            icon_type=gift_conf["icon_type"],  # icon类型
            price=gift_conf["price"],  # 价格
            worth=gift_conf["worth"],  # 价值
            open_type=gift_conf["open_type"],  # 开放类型
            limit_num=gift_conf["limit_num"],  # 限制数量
            vip_type=gift_conf["vip_type"],  # vip类型
            vip_level=gift_conf["vip_level"],  # vip 等级
            detail_1=gift_conf["detail_1"],
            detail_2=gift_conf["detail_2"],
            detail_3=gift_conf["detail_3"],
            online_state=online_state,  # 1 上架 2下架
            reward=gift_conf["reward"],
            add_time=gift_conf["add_time"],
            add_reward=gift_conf["add_reward"],
        )
    else:
        channel_list = gift_conf.get("channel", [])
        GiftInfo.objects.filter(gift_id=gift_id).update(
            channel_list=channel_list,
            gift_id=gift_id,
            skip=gift_conf["skip"],
            gift_name=gift_conf["name"],
            version_id=gift_conf["version"],  # 版本号
            index=gift_conf["index"],  # 排序
            hot=gift_conf["hot"],  # 热度
            start_time=gift_conf["start"],  # 开启时间
            end_time=gift_conf["end"],  # 结束时间
            icon_type=gift_conf["icon_type"],  # icon类型
            price=gift_conf["price"],  # 价格
            worth=gift_conf["worth"],  # 价值
            open_type=gift_conf["open_type"],  # 开放类型
            limit_num=gift_conf["limit_num"],  # 限制数量
            vip_type=gift_conf["vip_type"],  # vip类型
            vip_level=gift_conf["vip_level"],  # vip 等级
            detail_1=gift_conf["detail_1"],
            detail_2=gift_conf["detail_2"],
            detail_3=gift_conf["detail_3"],
            online_state=online_state,  # 1 上架 2下架
            reward=gift_conf["reward"],
        )


def add_gift_good(dic):
    info, msg = "", True
    hot = int(dic.get('add_hot'))
    channel_info = dic.getlist('add_channel')  # 渠道列表
    skip = dic.get('add_skip', "").encode('utf-8')
    index = int(dic.get('add_index'))
    gift_name = dic.get('add_gift_name').encode('utf-8')
    icon_type = int(dic.get('add_icon_type'))
    price = float(dic.get('add_price'))
    worth = int(dic.get('add_worth'))
    open_type = int(dic.get('add_open_type'))
    limit_num = int(dic.get('add_limit_num'))
    vip_level = int(dic.get('add_vip_level'))  # vip限制类型
    vip_grade = dic.getlist('add_vip_grade')
    detail_1 = dic.get('detail_1')
    detail_2 = dic.get('detail_2')
    detail_3 = dic.get('detail_3')
    start_time = dic.get('start_time').encode('utf-8')[:10] + " 00:00:00"
    end_time = dic.get('stop_time').encode('utf-8')[:10] + " 23:59:59"
    good_name = dic.getlist('add_good_name')
    good_number = dic.getlist('add_number')

    gift_list, gift_number = [], []
    for g_name, g_value in zip(good_name, good_number):
        g_value = g_value.encode('utf-8')
        if g_value == "":
            continue
        else:
            g_name = g_name.encode('utf-8')
            gift_list.append(g_name)
            gift_number.append(g_value)

    channel_list = []
    for channel in channel_info:
        channel = channel.encode('utf-8')
        channel_list.append(channel)

    if len(gift_list) != len(set(gift_list)):
        info, msg = "商品数据重复!", False

    reward = ProcessInfo.deal_auto_shot_reward(gift_list, gift_number)
    grade_list = [int(vip) for vip in vip_grade]
    gift_conf = {
        'hot': hot,  # 活动热度
        'index': index,  # 排序
        'version': 1000,
        'name': gift_name,  # 活动名称
        'icon_type': icon_type,  # icon类型
        'price': price,  # 价格（如果为0则显示免费）
        'worth': worth,  # 价值（如果为0则不显示）
        'open_type': open_type,  # 开放类型（1：日开放，2：周开放，3：月开放，4：指定时间开放）
        # 'limit_type': 1,  # 限制类型（1：日限制，2：时段限制）
        'limit_num': limit_num,  # 限制数量
        'start': start_time,  # 开启时间
        'end': end_time,  # 结束时间
        'vip_level': grade_list,  # vip等级
        'vip_type': vip_level,  # vip限制类型(1:某个vip等级以上可以购买，2：某些vip可以购买)
        'detail_1': detail_1,  # 明细1
        'detail_2': detail_2,  # 明细2
        'detail_3': detail_3,  # 明细3
        'reward': reward,
    }

    if skip != "":
        gift_conf.update({"skip": int(skip)})
    else:
        gift_conf.update({"skip": ""})

    if len(channel_info) > 0:
        channel_list = []
        for channel in channel_info:
            channel = channel.encode('utf-8')
            channel_list.append(channel)
        gift_conf.update({"channel": channel_list})

    if open_type == 5:
        extra_name = dic.getlist('extra_name')
        extra_number = dic.getlist('extra_number')
        add_time = int(dic.get('add_time'))
        gift_conf, msg, info = add_open_type(gift_conf,extra_name,extra_number,add_time)

    return gift_conf, msg, info


def update_gift_good(dic):
    info, msg, gift_conf = "", True, {}
    channel_info = dic.getlist('channel')  # 渠道列表
    gift_id = dic.get('gift_id').encode('utf-8')
    hot = int(dic.get('hot'))
    skip = dic.get('skip', "").encode('utf-8')
    index = int(dic.get('index'))
    gift_data = int(dic.get('gift_data'))
    gift_name = dic.get('gift_name').encode('utf-8')
    icon_type = int(dic.get('icon_type'))
    price = float(dic.get('price'))
    worth = int(dic.get('worth'))
    open_type = int(dic.get('open_type'))
    limit_num = int(dic.get('limit_num'))
    vip_level = int(dic.get('vip_level'))  # vip限制类型
    vip_grade = dic.getlist('vip_grade')
    detail_1 = dic.get('detail_1')
    detail_2 = dic.get('detail_2')
    detail_3 = dic.get('detail_3')
    start_time = dic.get('start_time').encode('utf-8')[:10] + " 00:00:00"
    end_time = dic.get('stop_time').encode('utf-8')[:10] + " 23:59:59"
    good_name = dic.getlist('good_name')
    good_number = dic.getlist('good_number')

    gift_list, gift_number = [], []
    for g_name, g_value in zip(good_name, good_number):
        g_value = g_value.encode('utf-8')
        if g_value == "":
            continue
        else:
            g_name = g_name.encode('utf-8')
            gift_list.append(g_name)
            gift_number.append(g_value)

    if len(gift_list) != len(set(gift_list)):
        info, msg = "商品数据重复!", False

    reward = ProcessInfo.deal_auto_shot_reward(gift_list, gift_number)
    grade_list = [int(vip) for vip in vip_grade]
    result = GiftInfo.objects.filter(gift_id=gift_id).values("version_id").first()
    version_id = int(result.get("version_id", 1000))
    if gift_data == 0:
        version = version_id
    else:
        version = version_id + 1

    gift_conf = {
        "gift_id": gift_id,
        'index': index,  # 排序
        'hot': hot,  # 活动热度
        'version': version,
        'name': gift_name,  # 活动名称
        'icon_type': icon_type,  # icon类型
        'price': price,  # 价格（如果为0则显示免费）
        'worth': worth,  # 价值（如果为0则不显示）
        'open_type': open_type,  # 开放类型（1：日开放，2：周开放，3：月开放，4：指定时间开放）
        'limit_num': limit_num,  # 限制数量
        'start': start_time,  # 开启时间
        'end': end_time,  # 结束时间
        'vip_level': grade_list,  # vip等级
        'vip_type': vip_level,  # vip限制类型(1:某个vip等级以上可以购买，2：某些vip可以购买)
        'detail_1': detail_1,  # 明细1
        'detail_2': detail_2,  # 明细2
        'detail_3': detail_3,  # 明细3
        'reward': reward,
    }

    if skip != "":
        gift_conf.update({"skip": int(skip)})
    else:
        gift_conf.update({"skip": ""})

    if len(channel_info) > 0:
        channel_list = []
        for channel in channel_info:
            channel = channel.encode('utf-8')
            channel_list.append(channel)
        gift_conf.update({"channel": channel_list})

    if open_type == 5:
        extra_name = dic.getlist('extra_name')
        extra_number = dic.getlist('extra_number')
        add_time = int(dic.get('add_time'))
        gift_conf, msg, info = add_open_type(gift_conf,extra_name,extra_number,add_time)

    return gift_conf, msg, info


def gift_Racking(gift_id):  # 上架
    info, msg, gift_conf = "", True, {}
    ret = GiftInfo.objects.filter(gift_id=gift_id).values("gift_id", "gift_name", "version_id", "hot", "index", "skip",
                                                          "start_time", "end_time", "icon_type", "price", "worth",
                                                          "open_type", "limit_num", "vip_type", "vip_level", "detail_1",
                                                          "detail_2", "detail_3", "online_state", "reward", "add_reward",
                                                          "add_time", "channel_list").first()
    gift_conf = {
        'hot': int(ret["hot"]),  # 活动热度
        'index': int(ret["index"]),  # 排序
        'skip': ret["skip"],  # 跳转设置
        'version': int(ret["version_id"]),
        'name': ret["gift_name"],  # 活动名称
        'icon_type': int(ret["icon_type"]),  # icon类型
        'price': ret["price"],  # 价格（如果为0则显示免费）
        'worth': ret["worth"],  # 价值（如果为0则不显示）
        'open_type': int(ret["open_type"]),  # 开放类型（1：日开放，2：周开放，3：月开放，4：指定时间开放）
        'limit_num': ret["limit_num"],  # 限制数量
        'start': Time.datetime_to_str(ret["start_time"]),  # 开启时间
        'end': Time.datetime_to_str(ret["end_time"]),  # 结束时间
        'vip_level': eval(ret["vip_level"]),  # vip等级
        'vip_type': int(ret["vip_type"]),  # vip限制类型(1:某个vip等级以上可以购买，2：某些vip可以购买)
        'detail_1': ret["detail_1"],  # 明细1
        'detail_2': ret["detail_2"],  # 明细2
        'detail_3': ret["detail_3"],  # 明细3
        'reward': eval(ret["reward"]),
    }

    open_type = int(ret.get("open_type", 1))
    if open_type == 5:
        add_reward = eval(ret.get('add_reward'))
        add_time = int(ret.get('add_time'))
        gift_conf.update({"add_reward": add_reward, "add_time": add_time})

    channel_info = eval(ret["channel_list"])
    if len(channel_info) > 0:
        channel_list = []
        for channel in channel_info:
            channel = channel.encode('utf-8')
            channel_list.append(channel)
        gift_conf.update({"channel": channel_list})

    return gift_conf, msg, info


def gift_sold_out(gift_id):
    info, msg, gift_conf = "", True, {}
    ret = GiftInfo.objects.filter(gift_id=gift_id).values("gift_id", "gift_name", "version_id", "hot", "index", "skip",
                                                          "start_time", "end_time", "icon_type", "price", "worth",
                                                          "open_type", "limit_num", "vip_type","vip_level", "detail_1",
                                                          "detail_2", "detail_3", "online_state", "reward", "add_reward",
                                                          "add_time", "channel_list").first()
    gift_conf = {
        'hot': int(ret["hot"]),  # 活动热度
        'skip': ret["skip"],  # 跳转设置
        'index': int(ret["index"]),  # 排序
        'version': int(ret["version_id"]),
        'name': ret["gift_name"],  # 活动名称
        'icon_type': int(ret["icon_type"]),  # icon类型
        'price': ret["price"],  # 价格（如果为0则显示免费）
        'worth': ret["worth"],  # 价值（如果为0则不显示）
        'open_type': int(ret["open_type"]),  # 开放类型（1：日开放，2：周开放，3：月开放，4：指定时间开放）
        'limit_num': ret["limit_num"],  # 限制数量
        'start': Time.datetime_to_str(ret["start_time"]),  # 开启时间
        'end': Time.datetime_to_str(ret["end_time"]),  # 结束时间
        'vip_level': eval(ret["vip_level"]),  # vip等级
        'vip_type': int(ret["vip_type"]),  # vip限制类型(1:某个vip等级以上可以购买，2：某些vip可以购买)
        'detail_1': ret["detail_1"],  # 明细1
        'detail_2': ret["detail_2"],  # 明细2
        'detail_3': ret["detail_3"],  # 明细3
        'reward': eval(ret["reward"]),
    }

    open_type = int(ret.get("open_type", 1))
    if open_type == 5:
        add_reward = eval(ret.get('add_reward'))
        add_time = int(ret.get('add_time'))
        gift_conf.update({"add_reward": add_reward, "add_time": add_time})

    channel_info = eval(ret["channel_list"])
    if len(channel_info) > 0:
        channel_list = []
        for channel in channel_info:
            channel = channel.encode('utf-8')
            channel_list.append(channel)
        gift_conf.update({"channel": channel_list})

    return gift_conf, msg, info


def add_open_type(gift_conf,extra_name,extra_number,add_time):
    name_list, number_list = [], []
    for g_name, g_value in zip(extra_name, extra_number):
        g_value = g_value.encode('utf-8')
        if g_value == "":
            continue
        else:
            g_name = g_name.encode('utf-8')
            name_list.append(g_name)
            number_list.append(g_value)

    if len(name_list) != len(set(name_list)):
        info, msg = "额外奖励商品数据重复!", False
    else:
        info, msg = "", True

    add_reward = ProcessInfo.deal_auto_shot_reward(name_list, number_list)
    gift_conf.update({"add_reward": add_reward, "add_time": add_time})
    return gift_conf, msg, info