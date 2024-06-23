# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from util.context import Context
from util.tool import Time
from django.core.paginator import Paginator
from util.gamedate import *
from .models import *
import datetime
import calendar
import json
from util.process import ProcessInfo
from xlwt import *
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from login_manage.models import ProductList
from hashlib import sha1
from login_manage.models import ChannelList
from login_manage.views import decorator
import re
from django.conf import settings
import os
from util.Props import BirdProps
import random
import logging

import sys
reload(sys)
sys.setdefaultencoding('utf8')


@decorator
def red_packet_query(request):
    red_info = Activity_Info.get_red_packet_type()  # 红包筛选条件
    number, url_date, phone = 1, "/activity_manage/red_packet/", request.session.get('uid')
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page:
            conf, red_packet_info = get_red_packet(phone)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            red_packet_info.update({"number": number, "page": page, "online_users": len(conf)})
        else:
            end_day = datetime.date.today().strftime('%Y-%m-%d')
            red_packet_info = {"start_day": end_day, "end_day": end_day, "red_type": "0", "number": number, "page": []}
    else:
        dic = request.POST
        red_packet = int(dic.get('red_packet_type'))
        start_time = dic.get('start_time').encode('utf-8')[:10]
        end_time = dic.get('stop_time').encode('utf-8')[:10]

        red_packet_info = {"start_day": start_time, "end_day": end_time, "red_type": str(red_packet)}
        keys = 'red_packet:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, red_packet_info)

        start_day,end_day = Time.str_to_datetime(start_time, '%Y-%m-%d'), Time.str_to_datetime(end_time, '%Y-%m-%d')

        while start_day <= end_day:
            res = RedPacketInfo.objects.filter(day_time=start_day).last()
            cur_day = Time.datetime_to_str(start_day, '%Y-%m-%d')
            red_start,red_end = cur_day + " 00:00:00",cur_day + " 23:59:59"
            if res:
                if red_packet == 1:
                    result = RedPacketInfo.objects.filter(day_time=start_day, red_packet_type=red_packet).last()
                    if result:
                        now_stamp,end_stamp = Time.current_ts(),int(result.special_end_time)
                        insert_stamp = Time.datetime_to_timestamp(result.insert_time)
                        if end_stamp <= now_stamp and insert_stamp >= end_stamp:
                            start_day = Time.next_days(start_day)
                            continue
                        else:
                            insert_red_packet_info(phone, red_start, red_end, red_packet)  # 插入数据
                    else:
                        insert_red_packet_info(phone, red_start, red_end, red_packet)  # 插入数据
                else:
                    result = RedPacketInfo.objects.filter(day_time=start_day, red_packet_type=red_packet).last()
                    if result:
                        if result.day_time == result.insert_time:
                            day_stamp = Time.timestamp_to_str(result.day_stamp)
                            insert_red_packet_info(phone, day_stamp, red_end, red_packet)  # 插入数据
                    else:
                        insert_red_packet_info(phone, red_start, red_end, red_packet)  # 插入数据
                start_day = Time.next_days(start_day)
                continue
            else:
                insert_red_packet_info(phone, red_start, red_end, red_packet)  # 插入数据
            start_day = Time.next_days(start_day)

        start_date,end_date = Time.str_to_datetime(start_time, '%Y-%m-%d'),Time.str_to_datetime(end_time, '%Y-%m-%d')

        res_info = RedPacketInfo.objects.filter(day_time__range=[start_date, end_date],red_packet_type=red_packet).values('json_data').order_by("-day_stamp")

        sorted_info,order = [],1
        for r_data in res_info:
            red_data = Context.json_loads(r_data.get("json_data"))
            packet_info = []
            for packet in red_data["packet_list"]:
                packet_id = str(packet)
                info = RedGetData.objects.filter(red_packet_id=packet_id).values("uid", "nick", "packet", "time")
                if len(info) > 0:
                    data_list = info[:]  # queryset转为list
                    packet_info.append(data_list)
                else:
                    continue
            red_data.update({"order": order, "user_info": packet_info})
            sorted_info.append(red_data)
            order = order + 1
        paginator = Paginator(sorted_info, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        red_packet_info.update({'number': number, "page": page})

    red_packet_info.update({"url_date": url_date,"red_info": red_info})
    return render(request, 'activity_manage/send_red_packet.html',red_packet_info)


@decorator
def deal_red_packet(request):
    phone = request.session.get('uid')
    dic = request.POST
    pid = int(dic.get("pid"))
    if pid == 1:
        red_type = int(dic.get("red_type"))  # 0 普通红包  1定时红包
        number, total_price = dic.get("number"),dic.get("total_price")
        if red_type == 0:
            status_type = "普通红包(生成)"
            operation = "数额:{}".format(total_price) + "数量:{}".format(number)
            record_data = {"status_type": status_type, "info": operation}
            context = {"total_price": total_price, "number": number, "type": red_type}
        else:
            status_type = "定时红包(生成)"
            operation = "数额:{}".format(total_price) + "数量:{}".format(number)
            record_data = {"status_type": status_type, "info": operation}

            start_time, end_time = dic.get('start_time'), dic.get('stop_time')
            start_days = Time.str_to_timestamp(start_time[:10], '%Y-%m-%d')
            end_days = Time.str_to_timestamp(end_time[:10], '%Y-%m-%d')
            start_hour, end_hour, interval_time = start_time[11:], end_time[11:], int(dic.get('interval_time')) * 60
            start_hours = int(start_hour[0:2]) * 3600 + int(start_hour[3:5]) * 60
            end_hours = int(end_hour[0:2]) * 3600 + int(end_hour[3:5]) * 60
            context = {"total_price": total_price, "number": number, "type": red_type, "st": start_days, "nt": end_days,"sh": start_hours, "eh": end_hours, "it": interval_time}
        url = '/v1/shell/gm/special/red_packet'
        red_info = "红包发送"
        context.update({"phone": phone})
        ret = Context.Controller.request(url, context)
        if ret.status_code == 200:
            insert_record_data(phone, RedPacketRecord, record_data)
            info = "{}成功!".format(red_info)
            status = True
        else:
            info = "{}失败!".format(red_info)
            status = False
        return JsonResponse({'status': status, 'info': info})
    else:
        special_id = int(dic.get("special_id"))
        url = '/v1/shell/gm/special/remove_red_packet'
        context = {"special_id": special_id}
        red_info = "终止定时红包"

        context.update({"phone": phone})
        ret = Context.Controller.request(url, context)
        if ret.status_code == 200:
            result = RedPacketInfo.objects.filter(special_id=special_id).values('json_data').first()
            json_info = Context.json_loads(result.get("json_data"))
            json_info["stop_state"] = 2
            RedPacketInfo.objects.filter(special_id=special_id).update(
                json_data=Context.json_dumps(json_info),
            )
            info = "{}成功!".format(red_info)
            status = True
        else:
            info = "{}失败!".format(red_info)
            status = False
        return JsonResponse({'status': status, 'info': info})


# ==========================充值翻倍==============================
@decorator
def player_pay_double(request):
    phone = request.session.get('uid')
    if request.method == 'GET':
        url = '/v2/shell/shop/first_recharge_query'
        day_time = datetime.date.today().strftime('%Y-%m-%d')
        double_info = {"start_day": day_time, "end_day": day_time}
        context = {"phone": phone}
        ret = Context.Controller.request(url, context)
        config = Context.json_loads(ret.text)
        if "ret" not in config:
            return render(request, 'activity_manage/new_user_pay_double.html',double_info)
        else:
            double = config["ret"]
            double_list, welfare_list = [], []
            for key, vales in double["conf"].items():
                welfare_dict = {}
                keys = str(Context.json_loads(key))
                welfare_dict.update({"good_id": keys, "good_name": vales.get("name")})
                vales.update({"product": keys})
                double_list.append(vales)
                welfare_list.append(welfare_dict)
            double_list = Context.json_dumps(double_list)

            pay_double = double["rdd"]
            if pay_double.has_key("pd"):
                pay_info = []
                start_day,end_day = pay_double["start"],pay_double["end"]
                act_name,act_desc = pay_double["name"],pay_double["desc"]
                tips,order = pay_double.get("tips", 0),pay_double.get("order", "")
                for key, vales in pay_double["pd"].items():
                    pay_dict = {}
                    pay_dict.update({"key": key, "vales": int(vales * 100)})
                    pay_info.append(pay_dict)
                double_info.update({"start_day": start_day, "end_day": end_day})
            else:
                pay_info,act_desc,act_name,order,tips = [],"","","",0

            double_info.update({"page": double_list, "pay_info": pay_info,"act_name": act_name, "act_desc": act_desc, "tips": tips, "order": order,"welfare": welfare_list})
            return render(request, 'activity_manage/new_user_pay_double.html', double_info)
    else:
        dic = request.POST
        tips = int(dic.get("tips", 0))
        order = int(dic.get("order", 1))
        chip_name = dic.getlist("chip_name")
        input_info = dic.getlist("input_info")
        activity_name = dic.get("activity_name")
        activity_desc = dic.get("activity_desc")
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]

        chip_repetition = (False if len(chip_name) != len(set(chip_name)) else True)
        if chip_repetition:
            product_info = {}
            operation = ""
            for key, percent in zip(chip_name, input_info):
                chip_info = ProcessInfo.verify_productId(key)
                show_data = "{}".format(chip_info) + "    " + "翻倍比例{}%".format(percent)
                operation = operation + show_data
                percent = float(int(percent) / 100.0)
                product_info.update({key: percent})

            start_day = start_time + " 00:00:00"
            end_day = end_time + " 23:59:59"
            operation_data = "开始时间:{}".format(start_day) + "  " + "结束时间:{}".format(end_day)

            pay_double = {
                'id': '801_2018-12-29',
                'model': 8,
                'type': 1,
                'tips': tips,  # 0不显示 1 显示
                'order': order,  # 活动显示顺序
                'hot': 3,
                'show': 0,
                'name': activity_name,
                'start': start_day,
                'end': end_day,
                'desc': activity_desc,
                'pd': product_info,
            }
            record_data = {"status_type": "福利商品", "info": operation}
            insert_record_data(phone, DoubleOperation, record_data)
            record_data = {"status_type": "更新时间", "info": operation_data}
            insert_record_data(phone, DoubleOperation, record_data)
            url = '/v2/shell/shop/first_recharge_modify'
            context = {"rdd": pay_double}
            context.update({"phone": request.session.get('uid')})
            ret = Context.Controller.request(url, context)
            if ret.status_code == 200:
                info = "充值翻倍设置成功！"
                msg = True
            else:
                info = "充值翻倍设置失败！"
                msg = False
            return JsonResponse({'code': msg, 'info': info})
        else:
            info = "数据重复修改失败！"
            msg = False
            return JsonResponse({'code': msg, 'info': info})


# ==========================新手大礼包==============================
@decorator
def the_novice_gift(request):
    phone = request.session.get('uid')
    give_reward = Activity_Info.give_props_data()
    if request.method == 'GET':
        time_info = datetime.date.today().strftime('%Y-%m-%d')
        url = '/v2/shell/wx/new_player_gift'
        context = {"phone": phone}
        ret = Context.Controller.request(url, context)
        gift_data = {"start_day": time_info, "end_day": time_info, "give_reward": give_reward}
        gift = Context.json_loads(ret.text)
        if "ret" not in gift:
            gift_data.update({"mail_det": "", "mail_name": "", "mail_desc": "","tips": 0, "order": 20, "reward": []})
            return render(request, 'activity_manage/the_novice_gift.html', gift_data)
        else:
            if not gift["ret"]:
                gift_data.update({"mail_det": "", "mail_name": "", "mail_desc": "", "tips": 0, "order": 20, "reward": []})
                return render(request, 'activity_manage/the_novice_gift.html', gift_data)
            else:
                g_info = gift["ret"]
                start_day = g_info.get("start")
                end_day = g_info.get("end")
                tips = g_info.get("tips")
                mail_name = g_info.get("name")
                mail_det = g_info.get("det")
                desc = g_info.get("desc")
                order = g_info.get("order")
                reward = ProcessInfo.deal_gift_reward(g_info.get("re"))
                gift_data.update({"start_day": start_day, "end_day": end_day, "mail_det": mail_det, "mail_name": mail_name,"mail_desc": desc, "tips": tips, "order": order, "reward": reward})
                return render(request, 'activity_manage/the_novice_gift.html', gift_data)
    else:
        dic = request.POST
        switch = int(dic.get("show", 0))
        order = int(dic.get("order", 1))
        rewards_conf = dic.getlist("rewards_conf")
        input_info = dic.getlist("input_date")
        mail_name = dic.get("mail_name")
        mail_detail = dic.get("mail_detail")
        activity_desc = dic.get("activity_desc")
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]

        reward,prop = {},[]
        for key, value in zip(rewards_conf, input_info):
            props_info = {}
            key = key.encode('utf-8')
            value = int(value.encode('utf-8'))
            if key == "chip":
                reward.update({key: value})
            elif key == "diamond":
                reward.update({key: value})
            elif key == "coupon":
                reward.update({key: value})
            else:
                key = int(key)
                props_info.update({"id": key, "count": value})
                prop.append(props_info)
                reward.update({"props": prop})

        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"
        new_gift = {
            'id': '801_2019-03-05','model': 10,
            'type': 1,'tips': switch,  # 0不显示 1 显示
            'order': order,  # 活动显示顺序
            'hot': 3,'show': 0,
            'name': mail_name,'det': mail_detail,
            'start': start_day,'end': end_day,
            'desc': activity_desc,'re': reward,
        }
        url = '/v2/shell/wx/new_player_modify'
        context = {"ret": new_gift}
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)

        if ret.status_code == 200:
            record_data = {"status_type": "修改活动奖励", "info": reward}

            insert_record_data(phone, TheNoviceRecord, record_data)
            info = "新手大礼包设置成功！"
            msg = True
        else:
            info = "新手大礼包设置失败！"
            msg = False
        return JsonResponse({'code': msg, 'info': info})


# ==========================累计充值返奖==============================
@decorator
def accumulate_top_up(request):
    """活动管理--累计充值返奖"""
    phone = request.session.get('uid')
    config_list, hot_name, open_time = Activity_Info.pay_status(), Activity_Info.get_hot_type(), Activity_Info.get_open_time()
    total_info, give_reward, weapon_list = Activity_Info.get_total_pay(), Activity_Info.give_props_data(), Activity_Info.give_weapon_data()
    give_reward.extend(weapon_list)
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    deal_list, channel_data = ["1000", "2001_0", "2002_0"], {}
    for chl, name in chanel_info.items():
        chl = chl.encode("utf-8")
        if chl not in deal_list:
            channel_data[chl] = name
        else:
            continue
    prop_list = ["coin", "power", "diamond", "silver_coupon"]
    prop_info = ["201", "1201", "202", "1202", "203", "1203", "205", "1205", "206", "1206", "301", "1301", "1302", "1351","1321",
                 "302", "215", "1215", "216", "1216", "217", "1217", "218", "1218", "219", "1219", "220", "1220", "701", "1701","702",
                 "1702", "703", "1703", "704", "1704", "1305", "1327", "1311", "1611", "1328", "1329", "1330", "1331", "1332", "1333",
                 "1207"]
    pay_info = range(1, 8)
    if request.method == "GET":
        dic = request.GET
        channel = dic.get("channel", "1000_0").encode("utf-8")
        time_info = datetime.date.today().strftime('%Y-%m-%d')
        select_status = dic.get('select_status', "1").encode("utf-8")
        grand_total = {"model_index": select_status, "start": time_info, "end": time_info, "channel": channel, "name": "", "desc": "", "tips": 0, "order": "", "reward": []}
        if select_status == "1":
            url = '/v2/shell/activity/total_pay'
            context = {"pid": 1, "phone": phone, "channel": channel}
            ret = Context.Controller.request(url, context)
            activity = Context.json_loads(ret.text)
            if "c" not in activity:
                grand_total = grand_total
            else:
                config = activity["c"]
                if not config or not config.has_key("info"):
                    grand_total = grand_total
                else:
                    pay_list, index, prop_id = [], 1, 2
                    tips, name, order, hot = config["tips"], config["name"], config["order"], str(config["hot"])
                    desc, start, end, time_type = config["desc"], config["start"], config["end"], config["time_type"]
                    # channel_list, reward = config["channel"], config["info_{}".format(channel)]
                    channel_list = config["channel"]
                    keys = 'total_pay:{}:{}'.format(channel, 'config')
                    res = Context.RedisMatch.hash_mget(keys, ["info"])
                    reward = (Context.json_loads(res[0]) if res[0] else config["info"])
                    for info in reward:
                        total_pay = {}
                        result = ProcessInfo.deal_gift_reward(info["re"])
                        reward_len = len(result)
                        for s in range(1, 8 - reward_len):
                            add_info = {'option': 'coin', 'value': "", 'name': "", 'prop_id': prop_id}
                            result.append(add_info)
                            prop_id += 1
                        total_pay.update({"index": index, "pay": info["pay"], "return": result})
                        pay_list.append(total_pay)
                        index += 1
                    grand_total.update(
                        {"reward_len": len(pay_list), "tips": tips, "name": name, "order": order, "hot": hot,
                         "desc": desc, "start": start, "end": end, "time_type": time_type, "channel_list": channel_list,
                         "reward": pay_list})
        else:
            activity_key = 'total_pay:{}:{}:{}'.format("system", select_status, 'activity')
            result = Context.RedisMatch.hash_mget(activity_key, ["c"])  # cg 保留数据状态
            # config = (Context.json_loads(result[0]) if result[0] else [])
            if result[0]:
                config = Context.json_loads(result[0])
                pay_list, index, prop_id = [], 1, 2
                tips, name, order, hot = config["tips"], config["name"], config["order"], str(config["hot"])
                desc, start, end, time_type = config["desc"], config["start"], config["end"], config["time_type"]
                # channel_list, reward = config["channel"], config["info_{}".format(channel)]
                channel_info = config["channel"]
                keys = 'total_pay:{}:{}'.format(channel, "timer")
                res = Context.RedisMatch.hash_mget(keys, ["info"])
                reward = (Context.json_loads(res[0]) if res[0] else config["info"])
                for info in reward:
                    total_pay = {}
                    result = ProcessInfo.deal_gift_reward(info["re"])
                    reward_len = len(result)
                    for s in range(1, 8 - reward_len):
                        add_info = {'option': 'coin', 'value': "", 'name': "", 'prop_id': prop_id}
                        result.append(add_info)
                        prop_id += 1
                    total_pay.update({"index": index, "pay": info["pay"], "return": result})
                    pay_list.append(total_pay)
                    index += 1
                grand_total.update(
                    {"model_index": select_status, "reward_len": len(pay_list), "tips": tips, "name": name,
                     "order": order, "hot": hot, "desc": desc, "start": start, "end": end, "time_type": time_type,
                     "channel_list": channel_info, "reward": pay_list})
            else:
                grand_total = grand_total

        grand_total.update({"config_list": config_list, "prop_list": prop_list, "prop_info": prop_info,
                            "hot_name": hot_name, "chanel_info": channel_data, "act_data": total_info,
                            "open_time": open_time, "chanel_list": Context.json_dumps(channel_data),
                            "give_reward": give_reward, "give_list": Context.json_dumps(give_reward),
                            "pay_info": Context.json_dumps(pay_info)})
        return render(request, 'activity_manage/accumulate_top_up.html', grand_total)
    else:
        dic = request.POST
        select_status = str(dic.get("select_status", "1"))
        deal_pid = str(dic.get("deal_pid", "0"))
        channel_id = dic.get("channel", "1001_0").encode("utf-8")
        # bound_list = dic.getlist("bound")  # 锁定状态 1 锁定 2 未锁定
        switch, pay_money, pro_name, pro_number = int(dic.get("show", 0)), dic.getlist("pay_money"), dic.getlist("act_reward"), dic.getlist("act_data")
        barrel_day, act_name, act_hot, act_desc = dic.getlist("barrel_day"), str(dic.get("act_name")), int(dic.get("act_hot")), str(dic.get("act_desc"))
        open_channel, time_type, order = dic.getlist("act_channel"), int(dic.get("time_type")), int(dic.get("act_order", 1))
        start_time, end_time, retain_data = dic.get('start_time')[:10], dic.get('stop_time')[:10], int(dic.get("act_info", 1))
        if len(open_channel) != len(set(open_channel)):
            info = "渠道数据重复!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) > 1:
            info = "渠道数据错误!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})

        chanel_list, open_list = [], []
        if "0" in open_channel and len(open_channel) == 1:
            del chanel_info['0']
            for key, value in chanel_info.items():
                channel = key.encode('utf-8')
                chanel_list.append(channel)
            open_channel = chanel_list

        for chl in open_channel:
            channel = chl.encode('utf-8')
            open_list.append(channel)

        # total_list, index = [], 7
        # reward_list = ProcessInfo.deal_props_reward(pro_name, pro_number, barrel_day, index)
        # for pay, reward in zip(pay_money, reward_list):
        #     pro_info = {}
        #     pro_pay = pay.encode('utf-8')
        #     if pro_pay == "":
        #         info = "请输入充值金额!"
        #         msg = False
        #         return JsonResponse({'code': msg, 'info': info})
        #     else:
        #         pro_pay = int(pro_pay)
        #         pro_info.update({"pay": pro_pay, "re": reward})
        #         total_list.append(pro_info)
        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"
        config = {
            "id": "1301_2020-05-28",
            "model": 20,
            "type": 1,
            "tips": switch,
            "order": order,
            "hot": act_hot,
            "show": 0,
            "name": act_name,
            "start": start_day,
            "end": end_day,
            "channel": open_list,
            "desc": act_desc,
            "time_type": time_type,  # 1.每天 2.每周 3.每月
            # "info": total_list,
        }
        day_time = Time.current_time("%Y-%m-%d") + " 00:00:00"

        for key, value in chanel_info.items():
            key_channel = key.encode('utf-8')
            if select_status == "1":
                keys = 'total_pay:{}:{}'.format(key_channel, "config")
            else:
                keys = 'total_pay:{}:{}'.format(key_channel, "timer")
            res = Context.RedisMatch.hash_mget(keys, ["info"])
            reward = (Context.json_loads(res[0]) if res[0] else [])
            if reward:
                if key_channel == "1000_0":
                    config["info"] = reward
                else:
                    config["info_{}".format(key_channel)] = reward
            else:
                continue
        print("------------deal_pid", deal_pid, select_status)
        if deal_pid == "0":
            if select_status == "1":
                day_info = {"start_day": day_time, "end_day": end_day, "cg": retain_data, "c": Context.json_dumps(config)}
                keys = 'total_pay:{}:{}:{}'.format("system", select_status, 'activity')
                Context.RedisMatch.hash_mset(keys, day_info)

                url = '/v2/shell/activity/total_pay'
                context = {"phone": phone, "pid": 2, "c": config, "channel": channel_id}
                print("------------retain_data", retain_data, type(retain_data))
                if retain_data == 1:
                    context.update({"cg": retain_data})
                print("------------context2020", context)
                ret = Context.Controller.request(url, context)

                if ret.status_code == 200:
                    msg, info = True, "累计充值返奖设置成功！"
                else:
                    msg, info = False, "累计充值返奖设置失败!"
            else:
                print("------------config222", config)
                day_info = {"start_day": day_time, "end_day": end_day, "cg": retain_data, "c": Context.json_dumps(config)}
                keys = 'total_pay:{}:{}:{}'.format("system", select_status, 'activity')
                Context.RedisMatch.hash_mset(keys, day_info)
                msg, info = True, "累计充值配置添加成功!"

        else:  # 保存渠道配置
            pay_money, pro_name = dic.getlist("pay_money"), dic.getlist("act_reward")
            barrel_day, pro_number = dic.getlist("barrel_day"), dic.getlist("act_data")
            total_list, index = [], 7
            reward_list = ProcessInfo.deal_props_reward(pro_name, pro_number, barrel_day, index)
            for pay, reward in zip(pay_money, reward_list):
                pro_info = {}
                pro_pay = pay.encode('utf-8')
                if pro_pay == "":
                    msg, info = False, "请输入充值金额!"
                    return JsonResponse({'code': msg, 'info': info})
                else:
                    pro_pay = int(pro_pay)
                    pro_info.update({"pay": pro_pay, "re": reward})
                    total_list.append(pro_info)
            day_info = {"info": Context.json_dumps(total_list)}
            if select_status == "1":
                keys = 'total_pay:{}:{}'.format(channel_id, 'config')
            else:
                keys = 'total_pay:{}:{}'.format(channel_id, "timer")
            Context.RedisMatch.hash_mset(keys, day_info)

            msg, info = True, "配置保存成功!"
        return JsonResponse({'code': msg, 'info': info})


# ==========================vip登录赠送==============================
@decorator
def vip_login_give(request):
    phone = request.session.get('uid')
    if request.method == "GET":
        end_time = datetime.date.today().strftime('%Y-%m-%d')
        vip_info = [{"grade": 1, "chip": 0}, {"grade": 2, "chip": 0}, {"grade": 3, "chip": 0}, {"grade": 4, "chip": 0},
                    {"grade": 5, "chip": 0}, {"grade": 6, "chip": 0}, {"grade": 7, "chip": 0}, {"grade": 8, "chip": 0},
                    {"grade": 9, "chip": 0}, {"grade": 10, "chip": 0}, {"grade": 11, "chip": 0},{"grade": 12, "chip": 0}]
        url = '/v2/shell/shop/vip_activity_query'
        context = {"phone": phone}
        ret = Context.Controller.request(url, context)
        vip_login = Context.json_loads(ret.text)
        if not vip_login.has_key("ret") or len(vip_login["ret"]) < 1:
            login_info = {"start_day": end_time, "end_day": end_time, "vip_info": vip_info}
            return render(request, 'activity_manage/vip_login_give.html',login_info)
        else:
            vip_list = []
            vip_data = vip_login["ret"]

            start_day,end_day = vip_data["start"],vip_data["end"]
            act_name,act_desc = vip_data["name"],vip_data["desc"]
            tips,order = vip_data.get("tips", 0),vip_data.get("order", "")
            for key, value in vip_data["va"].items():
                vip_dict = {}
                vip_dict.update({"grade": int(key), "chip": value.get("chip", 0)})
                vip_list.append(vip_dict)
            login_data = {"vip_info": vip_list, "start_day": start_day, "end_day": end_day, "act_name": act_name,"act_desc": act_desc, "tips": tips, "order": order}
            return render(request, 'activity_manage/vip_login_give.html', login_data)
    else:
        dic = request.POST
        tips = int(dic.get("tips", 0))
        order = int(dic.get("order", 1))
        vip_chip = dic.getlist("vip_chip")
        history_chip = dic.getlist("history_chip")
        activity_name = dic.get("activity_name")
        activity_desc = dic.get("activity_desc")
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]

        login_info,operation_info = {},[]
        for index, value in enumerate(vip_chip):
            chip_info = {}
            chip_value = int(value)
            index = index + 1
            chip_info.update({"chip": chip_value})
            login_info.update({"{}".format(index): chip_info})
            vip_info = "vip{}:{}".format(index, chip_value)
            operation_info.append(vip_info)

        start_day,end_day = start_time + " 00:00:00",end_time + " 23:59:59"

        str_record = "开始时间:{}".format(start_day) + "  " + "结束时间:{}".format(end_day) + "  " + "活动名称:{}".format(
            activity_name) + "  " + "活动描述:{}".format(activity_desc) + "  " + "活动顺序:{}".format(order)
        record_data = {"status_type": "修改登录赠送信息", "info": str_record}
        insert_record_data(phone, LoginGiveRecord, record_data)

        login_give = {
            'id': '801_2019-01-09','model': 9,
            'type': 1,'tips': tips,  # 0不显示 1 显示
            'order': order,'hot': 3,
            'show': 0,'name': activity_name,
            'start': start_day,'end': end_day,
            'desc': activity_desc,'va': login_info,
        }
        record_data = {"status_type": "修改vip数据", "info": str(operation_info)}
        insert_record_data(phone, LoginGiveRecord, record_data)

        url = '/v2/shell/shop/vip_activity_modify'
        context = {"ret": login_give}
        context.update({"phone": phone})
        ret = Context.Controller.request(url, context)
        if ret.status_code == 200:
            info = "VIP登录赠送修改成功！"
            msg = True
        else:
            info = "VIP登录赠送修改失败！"
            msg = False
        return JsonResponse({'code': msg, 'info': info})

# ==========================存钱窝==============================
@decorator
def saving_pot(request):
    phone = request.session.get('uid')
    if request.method == "GET":
        end_time = datetime.date.today().strftime('%Y-%m-%d')
        vip_info = [{"grade": 0, "chip": 0, "day_time": 1}, {"grade": 1, "chip": 0, "day_time": 1},
                    {"grade": 2, "chip": 0, "day_time": 1}, {"grade": 3, "chip": 0, "day_time": 1},
                    {"grade": 4, "chip": 0, "day_time": 1}, {"grade": 5, "chip": 0, "day_time": 1},
                    {"grade": 6, "chip": 0, "day_time": 1}, {"grade": 7, "chip": 0, "day_time": 1},
                    {"grade": 8, "chip": 0, "day_time": 1}, {"grade": 9, "chip": 0, "day_time": 1},
                    {"grade": 10, "chip": 0, "day_time": 1}, {"grade": 11, "chip": 0, "day_time": 1},
                    {"grade": 12, "chip": 0, "day_time": 1}]

        url = '/v2/shell/shop/save_money_activity_query'
        context = {"phone": phone}
        ret = Context.Controller.request(url, context)
        saving_info = Context.json_loads(ret.text)
        if not saving_info.has_key("ret") or len(saving_info["ret"]) < 1:
            save_info = {"start_day": end_time, "end_day": end_time, "save_chip": 0, "vip_info": vip_info}
            return render(request, 'activity_manage/saving_pot.html',save_info)
        else:
            save_list = []
            saving_data = saving_info["ret"]

            start_day = saving_data["start"]
            end_day = saving_data["end"]
            save_chip = saving_data["save_chip"]

            for key, value in saving_data["sp"].items():
                save_dict = {}
                save_dict.update({"grade": int(key), "chip": value.get("chip", 0), "day_time": value.get("day_time", 0)})
                save_list.append(save_dict)

            login_data = {"vip_info": save_list, "start_day": start_day, "end_day": end_day, "save_chip": save_chip}
            return render(request, 'activity_manage/saving_pot.html', login_data)
    else:
        dic = request.POST
        save_chip = int(dic.get("save"))
        chip_limit = dic.getlist("chip_limit")
        get_number = dic.getlist("get_number")
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]

        index = 0
        saving_info,chip_operation,time_operation = {},[],[]
        for chip, time in zip(chip_limit, get_number):
            chip_info = {}
            chip_int,day_time = int(chip),int(time)
            chip_info.update({"chip": chip_int, "day_time": day_time})
            saving_info.update({"{}".format(index): chip_info})
            vip_chip = "vip{}:{}".format(index, chip_int)
            vip_time = "vip{}:{}".format(index, day_time)
            chip_operation.append(vip_chip)
            time_operation.append(vip_time)
            index = index + 1

        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"

        saving_pot = {
            'id': '801_2019-01-11',
            'model': 10,
            'type': 1,
            'hot': 3,
            'show': 0,
            'save_chip': save_chip,
            'start': start_day,
            'end': end_day,
            'sp': saving_info,
        }
        time_record = "开始时间:{}".format(start_day) + "  " + "结束时间:{}".format(end_day)
        name_list = ["修改鸟蛋上限", "修改每日领取次数", "修改每消耗N鸟蛋", "修改时间"]
        info_list = [str(chip_operation), str(time_operation), save_chip, time_record]

        for name, info in zip(name_list, info_list):
            record_data = {}
            record_data.update({"status_type": name, "info": info})
            insert_record_data(phone, SavingPotRecord, record_data)

        url = '/v2/shell/shop/save_money_activity_modify'
        context = {"ret": saving_pot}
        context.update({"phone": phone})
        ret = Context.Controller.request(url, context)
        if ret.status_code == 200:
            info = "存钱窝修改成功！"
            msg = True
        else:
            info = "存钱窝修改失败！"
            msg = False
        return JsonResponse({'code': msg, 'info': info})


# ==========================开心摇摇乐==============================
@decorator
def happy_shake_alter(request):
    phone = request.session.get('uid')
    room_info = Activity_Info.get_room_info()
    select = Activity_Info.get_select_info()
    select_info = select[1:]
    happy_info = {"room_info": room_info,"select_info": select_info}
    if request.method == "GET":
        dic = request.GET
        way = dic.get("way")
        end_time = datetime.date.today().strftime('%Y-%m-%d')
        happy_list = {"happy": [{"money": "", "rebate": ""}]}
        url = '/v2/shell/activity/happy_shake'
        context = {"phone": phone,"pid": 1}
        ret = Context.Controller.request(url, context)
        config = Context.json_loads(ret.text)
        if way != None:
            new_way = str(way)
        else:
            new_way = "1"
        if not config.has_key("ret") or len(config["ret"]) < 1:
            happy_info.update({"start_day": end_time, "end_day": end_time, "happy_list": happy_list, "way": new_way, "top_up": "top_up","rebate": "rebate"})
            return render(request, 'activity_manage/happy_shake_alter.html', happy_info)
        else:
            result = config["ret"]
            start_day = result["start"]
            end_day = result["end"]
            tips = result["tips"]
            order = result["order"]
            happy_name = result["name"]
            happy_desc = result["desc"]
            happy_list = result["detail"]
            new_way = str(happy_list["way"])
            if way != None:
                new_str = str(way)
                if new_str != new_way:
                    new_way = new_str
                    happy_list["happy"] = [{"money": "", "rebate": ""}]
                else:
                    new_way = new_str
            else:
                new_way = str(new_way)
            happy_data = {"start_day": start_day, "end_day": end_day, "tips": tips, "order": order,"happy_name": happy_name, "happy_desc": happy_desc, "happy_list": happy_list,"way": new_way, "top_up": "top_up","rebate": "rebate"}
            return render(request, 'activity_manage/happy_shake_alter.html', happy_data)
    else:
        dic = request.POST
        detail_info = {}
        order = int(dic.get("order"))
        switch = int(dic.get("switch_show"))  # 活动开关
        login = int(dic.get("login_switch"))  # 登录提示开关
        way = int(dic.get("select_way"))  # 方式
        rebate = dic.getlist("rebate")  # 返利
        top_up = dic.getlist("top_up")  # 充值金额
        room_info = dic.getlist("room")  # 开放房间
        name = dic.get('happy_name').encode('utf-8')
        desc = dic.get('happy_desc').encode('utf-8')
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]

        happy = []
        for money, rebate in zip(top_up, rebate):
            shake = {}
            shake.update({"money": int(money), "rebate": int(rebate)})
            happy.append(shake)

        room_list = []
        for room in room_info:
            room = str(room)
            room_list.append(room)
        detail_info.update({'switch': switch, "way": way, "room": room_list, "happy": happy})
        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"

        happy_ret = {
            'id': '801_2019-03-18',
            'model': 11,
            'type': 1,
            'tips': login,  # 0不显示 1 显示
            'order': order,  # 显示顺序
            'hot': 3,
            'show': 0,
            "name": name,
            "desc": desc,
            'start': start_day,
            'end': end_day,
            'detail': detail_info
        }
        url = '/v2/shell/activity/happy_shake'
        context = {"ret": happy_ret, "pid": 2,"phone": phone}
        ret = Context.Controller.request(url, context)
        if ret.status_code == 200:
            way_info = ("循环" if way == 1 else "手动")
            if switch == 1:
                status_type, room_info = "摇摇乐活动开启", "场次:"
                for room in room_list:
                    room_name = (
                        "初级场" if room == "201" else "中级场" if room == "202" else "高级场" if room == "203" else "VIP房" if room == "209" else room)
                    room_info += room_name + ""
                money_info, rebate_info = '额度:', '返利:'
                for data in happy:
                    money_info += str(data["money"]) + " "
                    rebate_info += str(data["rebate"]) + " "
            else:
                status_type, money_info, rebate_info, room_info = "摇摇乐活动关闭", "", "", ""

            record_data = {"status_type": status_type, "way_info": way_info, "money": money_info, "rebate": rebate_info,"room": room_info}
            insert_record_data(phone, HappyRecord, record_data)
            info = "开心摇摇乐修改成功！"
            msg = True
        else:
            info = "开心摇摇乐修改失败！"
            msg = False
        return JsonResponse({'status': msg, 'info': info})


@decorator
def happy_shake_query(request):
    phone,number = request.session.get('uid'),1
    select_info = Activity_Info.get_select_info()
    url_date = "/activity_manage/happy_shake_query/"
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page != None:
            conf, shake_info = get_happy_info(phone)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            shake_info.update({"number": number, "page": page})
        else:
            end_day = datetime.date.today().strftime('%Y-%m-%d')
            shake_info = {"start_day": end_day, "end_day": end_day, "way":"0","page": [],"number": number}
    else:
        dic = request.POST
        way = dic.get('way').encode('utf-8')  # 方式
        start_day = dic.get("start_time")[:10]  # 查询开始时间
        end_day = dic.get("stop_time")[:10]  # 查询结束时间

        shake_info = {"start_day": start_day, "end_day": end_day, "way": way}
        keys = 'happy_shake:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, shake_info)

        start_time = Time.str_to_timestamp(start_day + " 00:00:00") * 1000
        end_time = Time.str_to_timestamp(end_day + " 23:59:59") * 1000

        day_time = HappyInfo.objects.all().values("day_time").last()
        if day_time:
            h_day_time = int(day_time["day_time"]) / 1000
            h_end_time = int(end_time) / 1000
            if h_day_time <= h_end_time:
                cur_day = Time.timestamp_to_str(h_day_time)
                insert_happy_info(phone, cur_day, end_day)
        else:
            insert_happy_info(phone, start_day, end_day)

        if way == '0':
            result = HappyInfo.objects.filter(day_time__range=(start_time, end_time)).values('json_data').order_by("-day_time")
        else:
            result = HappyInfo.objects.filter(day_time__range=(start_time, end_time), way=way).values('json_data').order_by("-day_time")

        sorted_info = []
        order_id = len(result)
        for info in result:
            data = json.loads(info.get("json_data"))
            happy_id = str(data["sid"])
            info = HappyData.objects.filter(happy_id=happy_id).values("uid", "multiple", "reward")
            if len(info) > 0:
                user_list = info[:]  # queryset转为list
                info_dict = {}
                for user in user_list:
                    info_dict.update({user["uid"]: {"bl": user["multiple"], "reward": user["reward"]}})
                data_list = info_dict
            else:
                data_list = {}
            data.update({"pd": data_list, "order_id": order_id})
            sorted_info.append(data)
            order_id = order_id - 1

        paginator = Paginator(sorted_info, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        shake_info.update({"page": page,"number": number})

    shake_info.update({"url_date": url_date,"select_info": select_info })
    return render(request, 'activity_manage/happy_shake_query.html', shake_info)


def insert_happy_info(phone,start_time,end_time):
    url = '/v2/shell/activity/happy_shake'
    context = {"start": start_time, "end": end_time,"pid":3}
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    game_info = Context.json_loads(ret.text)
    if not game_info.has_key("ret"):
        return 0
    else:
        happy_data = []
        happy_info = game_info["ret"]
        for data in happy_info:
            shake_data = {}
            trig_time = int(data["sid"]) /1000
            all_rebate = int(data["rebate"]) * 5000
            get_number = 0
            new_data = data["pd"]
            for key,value in new_data.items():
                get_number += value.get("reward", 0)

            insert_shake_info(new_data,data["sid"]) #插入弹窗显示数据
            del data["pd"] #删除用户数据
            shake_data.update(data)
            shake_data.update({"trig_time": Time.timestamp_to_str(trig_time), "all_rebate": all_rebate,"get_number":get_number})
            happy_data.append(shake_data)
        create_happy_data(happy_data)

def get_happy_info(phone):
    """开心摇摇乐--筛选条件"""
    keys = 'happy_shake:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day", "way"])  # 筛选条件
    start_day, end_day, way = result[0], result[1],int(result[2])
    def_info = {"start_day": start_day, "end_day": end_day, "way": way}

    start_time = Time.str_to_timestamp(start_day + " 00:00:00") * 1000
    end_time = Time.str_to_timestamp(end_day + " 23:59:59") * 1000

    if way == 0:
        result = HappyInfo.objects.filter(day_time__range=[start_time, end_time]).values('json_data').order_by("-day_time")
    else:
        result = HappyInfo.objects.filter(day_time__range=[start_time, end_time],way=way).values('json_data').order_by("-day_time")

    sort_info = []
    order_id = len(result)
    for info in result:
        data = json.loads(info.get("json_data"))
        happy_id = str(data["sid"])
        info = HappyData.objects.filter(happy_id=happy_id).values("uid", "multiple", "reward")
        if len(info) > 0:
            user_list = info[:]  # queryset转为list
            info_dict = {}
            for user in user_list:
                info_dict.update({user["uid"]:{"bl":user["multiple"],"reward":user["reward"]}})
            data_list = info_dict
        else:
            data_list = {}
        data.update({"pd": data_list,"order_id":order_id})
        sort_info.append(data)
        order_id = order_id - 1

    return sort_info,def_info


def create_happy_data(result):
    """摇摇乐--数据"""
    shake_data = []
    for m_info in result:
        happy_id = int(m_info["sid"])
        day_time = int(happy_id)
        way = int(m_info["way"])
        res = HappyInfo.objects.filter(happy_id=happy_id,way=way)
        if res:
            HappyInfo.objects.filter(happy_id=happy_id,way=way).update(
                happy_id=happy_id,
                day_time = day_time,
                way = way,
                json_data = json.dumps(m_info)
            )
        else:
            feel_happy = HappyInfo(
                happy_id=happy_id,
                day_time=day_time,
                way=way,
                json_data=json.dumps(m_info)
            )
            shake_data.append(feel_happy)

        if len(shake_data) > 1000:
            HappyInfo.objects.bulk_create(shake_data)
            shake_data = []

    HappyInfo.objects.bulk_create(shake_data)


def insert_shake_info(result,happy_ids):
    """插入玩家信息"""
    get_data = []
    happy_id = str(happy_ids)
    for uid,data in result.items():
        uid = str(uid)
        multiple = data.get("bl",0)
        reward  = data.get("reward",0)
        res = HappyData.objects.filter(happy_id=happy_id,uid=uid)
        if res:
            HappyData.objects.filter(happy_id=happy_id,uid=uid).update(
                happy_id=happy_id,
                uid = uid,
                multiple = multiple,
                reward = reward
            )
        else:
            Happy_info = HappyData(
                happy_id=happy_id,
                uid=uid,
                multiple=multiple,
                reward=reward
            )
            get_data.append(Happy_info)

        if len(get_data) > 1000:
            HappyData.objects.bulk_create(get_data)
            get_data = []

    HappyData.objects.bulk_create(get_data)


# ==========================活动礼包==============================
@decorator
def activity_gift_bag(request):
    phone = request.session.get('uid')
    gift_name = Activity_Info.get_gift_type()
    hot_name = Activity_Info.get_hot_type()
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    give_reward = Activity_Info.give_props_data()  # 道具
    weapon_list = Activity_Info.give_weapon_data()  # 武器
    give_reward.extend(weapon_list)
    del chanel_info['1000']
    if request.method == 'GET':
        dic = request.GET
        model = int(dic.get("model", 1))
        if model == 1:
            context = {"pid": 1}
            price = 6
        else:
            context = {"pid": 3}
            price = 88

        gift_info = { "price": price, "model": str(model)}
        url = '/v2/shell/activity/gift_box'
        context.update({"phone": phone})
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.text)
        if not gift.has_key("ret"):
            day_time = datetime.date.today().strftime('%Y-%m-%d')
            reward_list = range(0, 5)
            gift_info.update({"start": day_time, "end": day_time,"reward_list": reward_list})
        else:
            gift_one = gift["ret"]
            tips = gift_one.get("tips", 0)
            name = gift_one.get("name", "")
            order = gift_one.get("order", 0)
            hot = gift_one.get("hot", 0)
            desc = gift_one.get("desc", "")
            start = gift_one.get("start", "")
            end = gift_one.get("end", "")
            discount = gift_one.get("discount", 0)  # 折扣
            price = gift_one.get("price", 0)  # 充值金额
            channel_list = gift_one.get("channel", [])
            reward = gift_one.get("gift{}".format(model), {})

            reward_list = ProcessInfo.deal_gift_reward(reward)
            len_list = len(reward_list)
            if len_list < 5:
                for n in range(0, 5 - len_list):
                    reward_list.append({'option': 'chip'})
            reward_len = len(reward_list)
            gift_info.update({"tips": tips, "name": name, "order": order, "hot": hot, "desc": desc, "start": start, "end": end,"discount": discount, "channel_list": channel_list, "reward_list": reward_list, "reward_len": reward_len})
        gift_info.update({"gift_name":gift_name,"hot_name":hot_name,"chanel_info":chanel_info,"chanel_list":Context.json_dumps(chanel_info),"give_reward":give_reward,"give_list":Context.json_dumps(give_reward)})
        return render(request, 'activity_manage/activity_gift_one.html', gift_info)
    else:
        dic = request.POST
        model = int(dic.get("model"))
        show = int(dic.get("show", 0))
        order = int(dic.get("order", 1))
        hot = int(dic.get("hot", 0))
        activity_name = dic.get("activity_name")
        activity_desc = dic.get("activity_desc")
        start_day = dic.get('start_time')  # [:10]
        end_day = dic.get('stop_time')  # [:10]
        open_channel = dic.getlist("channel")
        pay_money = float(dic.get("pay_money", 0))
        discount = float(dic.get("discount", 0))
        good_name = dic.getlist("good_name")
        good_number = dic.getlist("good_number")

        if len(open_channel) != len(set(open_channel)):
            info = "渠道数据重复!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) > 1:
            info = "渠道数据错误!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})
        if "0" in open_channel and len(open_channel) == 1:
            old_data = ChannelList.objects.all().values('channel_data').first()
            chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
            del chanel_info['0']
            del chanel_info['1000']
            chanel_list = []
            for key, value in chanel_info.items():
                channel = key.encode('utf-8')
                chanel_list.append(channel)
            open_channel = chanel_list

        open_list = []
        for chl in open_channel:
            channel = chl.encode('utf-8')
            open_list.append(channel)

        gift_name = []
        gift_number = []
        for g_name, g_value in zip(good_name, good_number):
            g_value = g_value.encode('utf-8')
            if g_value == "":
                continue
            else:
                g_name = g_name.encode('utf-8')
                gift_name.append(g_name)
                gift_number.append(g_value)

        if len(gift_name) != len(set(gift_name)):
            info = "礼包商品数据重复!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})
        reward = {}
        prop = []
        weapon_list = []
        for key, value in zip(gift_name, gift_number):
            props_info = {}
            key = key.encode('utf-8')
            values = value.encode('utf-8')
            if values == "life" and key.isdigit():
                if int(key) > 20000:
                    weapon_list.append(int(key))
                    reward.update({"weapon": weapon_list})
                    continue
                else:
                    info = "商品数量异常!"
                    msg = False
                    return JsonResponse({'code': msg, 'info': info})
            else:
                value = int(values)
                if key == "chip":
                    reward.update({key: value})
                elif key == "diamond":
                    reward.update({key: value})
                elif key == "coupon":
                    reward.update({key: value})
                elif key == "target":
                    reward.update({key: value})
                elif key == "auto_shot":
                    reward.update({key: value})
                else:
                    key = int(key)
                    if key > 20000:
                        new_key = key * 1000 + value
                        props_info.update({"id": new_key, "count": 1})
                    else:
                        props_info.update({"id": key, "count": value})
                    prop.append(props_info)
                    reward.update({"props": prop})
        if model == 1:
            model_name = 13
            productId = 101111
            pid = 2
        else:
            model_name = 14
            productId = 101112
            pid = 4

        activity_gift = {
            'id': '1301_2019-03-22',
            'model': model_name,
            'type': 1,
            'tips': show,  # 0不显示 1 显示
            'order': order,  # 活动显示顺序
            'hot': hot,
            'show': 0,
            'price': pay_money,
            'discount': discount,
            'name': activity_name,
            'start': start_day,
            'end': end_day,
            'channel': open_list,
            'productId': productId,
            'desc': activity_desc,
            'gift{}'.format(model): reward,
        }

        url = '/v2/shell/activity/gift_box'
        context = {"pid": pid, "ret": activity_gift,"phone": phone}
        ret = Context.Controller.request(url, context)
        if ret.status_code == 200:
            # gift_record_info(request,gift_info)
            info = "活动礼包{}设置成功!".format(model)
            msg = True
        else:
            info = "活动礼包{}设置失败!".format(model)
            msg = False
        return JsonResponse({'code': msg, 'info': info})


# ==========================老活动配置==============================
@decorator
def activity_wheel_config(request):
    """活动管理--幸运轮盘"""
    if request.method == 'GET':
        context = {"aid":1,"pid": 1}
        def_time = datetime.date.today().strftime('%Y-%m-%d')
        hot_name = Activity_Info.get_hot_type()
        old_data = ChannelList.objects.all().values('channel_data').first()
        chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
        give_reward = Activity_Info.give_props_data()  # 道具

        del chanel_info['1000']
        reward_list = range(0,10)
        def_info = {"start": def_time, "end": def_time,"hot_name": hot_name,"chanel_info": chanel_info, "chanel_list": Context.json_dumps(chanel_info), "give_reward": give_reward,"reward_list":reward_list}
        url = '/v2/shell/activity/old_config'
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.text)
        if not gift.has_key("ret"):
            gift_info = def_info
            return render(request, 'activity_manage/activity_wheel.html', gift_info)
        else:
            config_info = gift["ret"]
            if not config_info:
                gift_info = def_info
            else:
                if isinstance(config_info, list):
                    config = config_info[0]
                else:
                    config = config_info
                tips = config.get("tips", 0)
                name = config.get("name", "")
                order = config.get("order", 0)
                hot = config.get("hot", 0)
                desc = config.get("desc", "")
                start = config.get("start", "")
                end = config.get("end", "")
                need_pay = config.get("need_pay", 0)  #单笔充值金额
                channel_list = config.get("channel", [])
                reward = config.get("rw_list", {})
                del def_info['start']
                del def_info['end']
                del def_info['reward_list']
                reward_list = ProcessInfo.deal_wheel_reward(reward)
                gift_info = {"tips": tips, "name": name, "order": order, "hot": str(hot), "desc": desc, "start": start,"end": end, "need_pay": need_pay,"channel_list": channel_list,"reward_list": reward_list}
                gift_info.update(def_info)
            return render(request, 'activity_manage/activity_wheel.html', gift_info)
    else:
        dic = request.POST
        show = int(dic.get("show", 0))
        order = int(dic.get("order", 10))
        hot = int(dic.get("hot", 0))
        activity_name = dic.get("activity_name")
        activity_desc = dic.get("activity_desc")
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]
        open_channel = dic.getlist("channel")
        need_pay = int(dic.get("one_price", 0))
        reward_name = dic.getlist("reward_name")
        reward_number = dic.getlist("reward_number")
        rate_list = dic.getlist("rate")

        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"

        rate_number = 10000
        r_info = 0
        for rate_info in rate_list:
            r_info = int(rate_info) + r_info

        if r_info != rate_number:
            info = "概率数据异常!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})

        if len(open_channel) != len(set(open_channel)):
            info = "渠道数据重复!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) > 1:
            info = "渠道数据错误!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})
        if "0" in open_channel and len(open_channel) == 1:
            old_data = ChannelList.objects.all().values('channel_data').first()
            chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
            del chanel_info['0']
            del chanel_info['1000']
            chanel_list = []
            for key, value in chanel_info.items():
                channel = key.encode('utf-8')
                chanel_list.append(channel)
            open_channel = chanel_list

        open_list = []
        for chl in open_channel:
            channel = chl.encode('utf-8')
            open_list.append(channel)

        reward = {}
        rate = 0
        for key, value in zip(reward_name, reward_number):
            key_info = key.encode('utf-8')
            value = int(value)
            if key_info == "chip":
                rate_data = int(rate_list[rate])
                reward.update({str(rate):{"rate":rate_data,"reward":{"chip":value}}})
            if key_info == "diamond":
                rate_data = int(rate_list[rate])
                reward.update({str(rate): {"rate": rate_data, "reward": {"diamond": value}}})
            if key_info == "coupon":
                rate_data = int(rate_list[rate])
                reward.update({str(rate): {"rate": rate_data, "reward": {"coupon": value}}})
            if key_info == "target":
                rate_data = int(rate_list[rate])
                reward.update({str(rate): {"rate": rate_data, "reward": {"target": value}}})
            if key_info.isdigit():
                prop = []
                rate_data = int(rate_list[rate])
                keys = int(key_info)
                prop.append({"id": keys, "count": value})
                reward.update({str(rate): {"rate": rate_data, "reward": {"props":prop}}})
            rate = rate +1

        wheel_config = {
            'id': '101_2019-03-27',
            'model': 1,
            'tips': show,  # 0不显示 1 显示
            'order': order,  # 活动显示顺序
            'hot': hot,
            'show': 0,
            'need_pay': need_pay,
            'name': activity_name,
            'start': start_day,
            'end': end_day,
            'channel': open_list,
            'desc': activity_desc,
            'rw_list': reward
        }

        url = '/v2/shell/activity/old_config'
        context = {"aid":1,"pid": 2, "ret": wheel_config}
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)

        if ret.status_code == 200:
            info = "幸运轮盘设置成功!"
            msg = True
        else:
            info = "幸运轮盘设置失败!"
            msg = False
        return JsonResponse({'code': msg, 'info': info})

@decorator
def activity_task_config(request):
    """活动管理--爆蛋7天乐"""
    if request.method == 'GET':
        context = {"aid":2,"pid": 1}
        def_time = datetime.date.today().strftime('%Y-%m-%d')
        hot_name = Activity_Info.get_hot_type()
        old_data = ChannelList.objects.all().values('channel_data').first()
        chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
        give_reward = Activity_Info.give_props_data()  # 道具
        bird_list = Activity_Info.get_bird_type() #所有鸟

        del chanel_info['1000']
        task_list = range(0,7)
        def_info = {"start": def_time, "end": def_time,"hot_name": hot_name,"chanel_info": chanel_info, "chanel_list": Context.json_dumps(chanel_info), "give_reward": give_reward,"task_list":task_list,"bird_list":bird_list}
        url = '/v2/shell/activity/old_config'
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.text)
        if not gift.has_key("ret"):
            gift_info = def_info
            return render(request, 'activity_manage/activity_task.html', gift_info)
        else:
            config_info = gift["ret"]
            if not config_info:
                gift_info = def_info
            else:
                if isinstance(config_info, list):
                    config = config_info[0]
                else:
                    config = config_info
                tips = config.get("tips", 0)
                name = config.get("name", "")
                order = config.get("order", 0)
                hot = config.get("hot", 0)
                desc = config.get("desc", "")
                start = config.get("start", "")
                end = config.get("end", "")
                need_pay = config.get("need_pay", 0)  #单笔充值金额
                channel_list = config.get("channel", [])
                reward = config.get("reward", {})
                reward_info = ProcessInfo.get_reward_info(reward)
                task_info = config.get("task", {})
                del def_info['start']
                del def_info['end']
                del def_info['task_list']
                task_list = ProcessInfo.deal_task_reward(task_info)
                gift_info = {"tips": tips, "name": name, "order": order, "hot": str(hot), "desc": desc, "start": start,"end": end, "need_pay": need_pay,"channel_list": channel_list,"task_list": task_list,"reward_info":reward_info}
                gift_info.update(def_info)
            return render(request, 'activity_manage/activity_task.html', gift_info)
    else:
        dic = request.POST
        show = int(dic.get("show", 0))
        order = int(dic.get("order", 8))
        hot = int(dic.get("hot", 0))
        activity_name = dic.get("activity_name")
        activity_desc = dic.get("activity_desc")
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]
        open_channel = dic.getlist("channel")
        reward_name = dic.get("reward_name", "chip")
        reward_number = int(dic.get("reward_number", 0))

        task_name = dic.getlist("task_name")
        task_number = dic.getlist("task_number")
        good_name = dic.getlist("good_name")
        good_number = dic.getlist("good_number")
        task_desc = dic.getlist("task_desc")

        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"

        if len(open_channel) != len(set(open_channel)):
            info = "渠道数据重复!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) > 1:
            info = "渠道数据错误!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})
        if "0" in open_channel and len(open_channel) == 1:
            old_data = ChannelList.objects.all().values('channel_data').first()
            chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
            del chanel_info['0']
            del chanel_info['1000']
            chanel_list = []
            for key, value in chanel_info.items():
                channel = key.encode('utf-8')
                chanel_list.append(channel)
            open_channel = chanel_list

        open_list = []
        for chl in open_channel:
            channel = chl.encode('utf-8')
            open_list.append(channel)

        reward_info = ProcessInfo.deal_props_info(reward_name,reward_number)

        task_list = {}
        tid = 0
        for key, value in zip(good_name, good_number):
            key_info = key.encode('utf-8')
            value = int(value)
            if key_info == "chip":
                bird = int(task_name[tid])
                if bird > 1:
                    state = 1
                else:
                    state = 0
                number = int(task_number[tid])
                desc_name = task_desc[tid]
                task_id = 105000 + tid +1
                task_list.update({task_id: [6, state, bird, number, 0, {"chip": value}, desc_name]})
            if key_info == "diamond":
                bird = int(task_name[tid])
                if bird > 1:
                    state = 1
                else:
                    state = 0
                number = int(task_number[tid])
                desc_name = task_desc[tid]
                task_id = 105000 + tid +1
                task_list.update({task_id: [6, state, bird, number, 0, {"diamond": value}, desc_name]})
            if key_info == "coupon":
                bird = int(task_name[tid])
                if bird > 1:
                    state = 1
                else:
                    state = 0
                number = int(task_number[tid])
                desc_name = task_desc[tid]
                task_id = 105000 + tid +1
                task_list.update({task_id: [6, state, bird, number, 0, {"coupon": value}, desc_name]})
            if key_info == "target":
                bird = int(task_name[tid])
                if bird > 1:
                    state = 1
                else:
                    state = 0
                number = int(task_number[tid])
                desc_name = task_desc[tid]
                task_id = 105000 + tid +1
                task_list.update({task_id: [6, state, bird, number, 0, {"target": value}, desc_name]})
            if key_info.isdigit():
                prop = []
                keys = int(key_info)
                prop.append({"id": keys, "count": value})
                bird = int(task_name[tid])
                if bird > 1:
                    state = 1
                else:
                    state = 0
                number = int(task_number[tid])
                desc_name = task_desc[tid]
                task_id = 105000 + tid +1
                task_list.update({task_id: [6, state, bird, number, 0,{"props":prop}, desc_name]})
            tid = tid + 1

        task_config = {
            'id': '201_2019-04-09',
            'model': 2,
            'tips': show,  # 0不显示 1 显示
            'order': order,  # 活动显示顺序
            'hot': hot,
            'show': 0,
            'reward': reward_info,
            'name': activity_name,
            'start': start_day,
            'end': end_day,
            'channel': open_list,
            'desc': activity_desc,
            'task': task_list
        }

        url = '/v2/shell/activity/old_config'
        context = {"aid":2,"pid": 2, "ret": task_config}
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)

        if ret.status_code == 200:
            info = "爆蛋7天乐设置成功!"
            msg = True
        else:
            info = "爆蛋7天乐设置失败!"
            msg = False
        return JsonResponse({'code': msg, 'info': info})

@decorator
def activity_rank_config(request):
    """活动管理--炮王之王"""
    if request.method == 'GET':
        context = {"aid":3,"pid": 1}
        def_time = datetime.date.today().strftime('%Y-%m-%d')
        hot_name = Activity_Info.get_hot_type()
        old_data = ChannelList.objects.all().values('channel_data').first()
        chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
        give_reward = Activity_Info.give_props_data()  # 道具
        weapon_list = Activity_Info.give_weapon_data()  # 武器
        give_reward.extend(weapon_list)

        del chanel_info['1000']
        def_info = {"start": def_time, "end": def_time,"hot_name": hot_name,"chanel_info": chanel_info, "chanel_list": Context.json_dumps(chanel_info), "give_reward": give_reward,"give_list": Context.json_dumps(give_reward)}
        url = '/v2/shell/activity/old_config'
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.text)

        if not gift.has_key("ret"):
            gift_info = def_info
            return render(request, 'activity_manage/activity_rank.html', gift_info)
        else:
            config_info = gift["ret"]
            if not config_info:
                gift_info = def_info
            else:
                if isinstance(config_info, list):
                    config = config_info[0]
                else:
                    config = config_info
                tips = config.get("tips", 0)
                name = config.get("name", "")
                order = config.get("order", 0)
                hot = config.get("hot", 0)
                desc = config.get("desc", "")
                start = config.get("start", "")
                end = config.get("end", "")
                count = config.get("count", 0)  #上榜人数
                channel_list = config.get("channel", [])
                level = config.get("level", [])
                reward = config.get("reward", [])
                reward_list = ProcessInfo.deal_rank_reward(reward)
                reward_info = []
                for led, conf in zip(level,reward_list):
                    conf.update({"rank":led})
                    reward_info.append(conf)

                del def_info['start']
                del def_info['end']
                gift_info = {"tips": tips, "name": name, "order": order, "hot": str(hot), "desc": desc, "start": start,"end": end, "count": count,"level":level,"channel_list": channel_list,"reward_info":reward_info}
                gift_info.update(def_info)
            return render(request, 'activity_manage/activity_rank.html', gift_info)
    else:
        dic = request.POST
        show = int(dic.get("show", 0))
        order = int(dic.get("order", 8))
        hot = int(dic.get("hot", 0))
        activity_name = dic.get("activity_name")
        activity_desc = dic.get("activity_desc")
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]
        open_channel = dic.getlist("channel")
        # count = dic.get("count", 1)

        start_range = dic.getlist("start_range")
        end_range = dic.getlist("end_range")
        good_name = dic.getlist("good_name")
        good_number = dic.getlist("good_number")

        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"

        if len(open_channel) != len(set(open_channel)):
            info = "渠道数据重复!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) > 1:
            info = "渠道数据错误!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})
        if "0" in open_channel and len(open_channel) == 1:
            old_data = ChannelList.objects.all().values('channel_data').first()
            chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
            del chanel_info['0']
            del chanel_info['1000']
            chanel_list = []
            for key, value in chanel_info.items():
                channel = key.encode('utf-8')
                chanel_list.append(channel)
            open_channel = chanel_list

        open_list = []
        for chl in open_channel:
            channel = chl.encode('utf-8')
            open_list.append(channel)

        level = []
        new_start = []
        new_end = []
        for les, lend in zip(start_range, end_range):
            if les == u"" or lend == u"":
                continue
            else:
                start = int(les)
                end = int(lend)
                new_start.append(start)
                new_end.append(end)
                if len(new_start) != len(set(new_start)):
                    info = "名次范围有重复的数据!"
                    msg = False
                    return JsonResponse({'status': msg, 'info': info})

                if len(new_end) != len(set(new_end)):
                    info = "名次范围有重复的数据!"
                    msg = False
                    return JsonResponse({'status': msg, 'info': info})
                if end < start:
                    level.append(range(end, start + 1))
                else:
                    level.append(range(start, end + 1))

        flag = True
        for k, v in enumerate(level):
            if k >= len(level) - 1:
                flag = True
                break
            if v[-1] + 1 != level[k + 1][0]:
                flag = False
                break
            else:
                continue
        if not flag:
            info = "排名序号异常!"
            return JsonResponse({'status': flag, 'info': info})

        reward_list = []
        for key,value in zip(good_name,good_number):
            props = ProcessInfo.get_for_deal(key,value)
            reward_list.append(props)

        if len(level) != len(reward_list):
            info = "奖励配置数据异常!"
            msg = False
            return JsonResponse({'status': msg, 'info': info})

        num_list = new_start + new_end
        people = ProcessInfo.find_max_num(num_list)
        rank_config = {
            'id': '301_2019-04-13',
            'model': 3,
            'tips': show,  # 0不显示 1 显示
            'order': order,  # 活动显示顺序
            'hot': hot,
            'show': 0,
            'count': people,
            'name': activity_name,
            'start': start_day,
            'end': end_day,
            'channel': open_list,
            'desc': activity_desc,
            'level':level,
            'reward': reward_list
        }

        url = '/v2/shell/activity/old_config'
        context = {"aid":3,"pid": 2, "ret": rank_config}
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)

        if ret.status_code == 200:
            info = "炮王之王设置成功!"
            msg = True
        else:
            info = "炮王之王设置失败!"
            msg = False
        return JsonResponse({'code': msg, 'info': info})

@decorator
def activity_login_config(request):
    """活动管理--登录有礼"""
    if request.method == 'GET':
        context = {"aid":4,"pid": 1}
        def_time = datetime.date.today().strftime('%Y-%m-%d')
        hot_name = Activity_Info.get_hot_type()
        old_data = ChannelList.objects.all().values('channel_data').first()
        chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
        give_reward = Activity_Info.give_props_data()  # 道具
        weapon_list = Activity_Info.give_weapon_data()  # 武器
        give_reward.extend(weapon_list)

        login_list =[{"led":1,'props_list': range(1,5)},{"led":2,'props_list': range(1,5)},{"led":3,'props_list':range(1,5)},{"led":4,'props_list': range(1,5)},{"led":5,'props_list': range(1,5)},{"led":6,'props_list': range(1,5)},{"led":7,'props_list': range(1,5)}]
        login_info = range(1,8)
        del chanel_info['1000']
        def_info = {"start": def_time, "end": def_time,"hot_name": hot_name,"chanel_info": chanel_info, "chanel_list": Context.json_dumps(chanel_info), "give_reward": give_reward,"give_list": Context.json_dumps(give_reward),"login_reward":login_list,"login_info":Context.json_dumps(login_info)}
        url = '/v2/shell/activity/old_config'
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.text)
        if not gift.has_key("ret"):
            gift_info = def_info
            return render(request, 'activity_manage/activity_login.html', gift_info)
        else:
            config_info = gift["ret"]
            if not config_info:
                gift_info = def_info
            else:
                if isinstance(config_info,list):
                    config = config_info[0]
                else:
                    config = config_info
                tips = config.get("tips", 0)
                name = config.get("name", "")
                order = config.get("order", 0)
                hot = config.get("hot", 0)
                desc = config.get("desc", "")
                start = config.get("start", "")
                end = config.get("end", "")
                channel_list = config.get("channel", [])

                del def_info['start']
                del def_info['end']
                del def_info['login_reward']
                login_reward = ProcessInfo.deal_login_reward(config.get("reward", []))

                gift_info = {"tips": tips, "name": name, "order": order, "hot": str(hot), "desc": desc, "start": start,"end": end,"channel_list": channel_list,"login_reward":login_reward}
                gift_info.update(def_info)
            return render(request, 'activity_manage/activity_login.html', gift_info)
    else:
        dic = request.POST
        show = int(dic.get("show", 0))
        order = int(dic.get("order", 4))
        hot = int(dic.get("hot", 0))
        activity_name = dic.get("activity_name")
        activity_desc = dic.get("activity_desc")
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]
        open_channel = dic.getlist("channel")

        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"

        if len(open_channel) != len(set(open_channel)):
            info = "渠道数据重复!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) > 1:
            info = "渠道数据错误!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})
        if "0" in open_channel and len(open_channel) == 1:
            old_data = ChannelList.objects.all().values('channel_data').first()
            chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
            del chanel_info['0']
            del chanel_info['1000']
            chanel_list = []
            for key, value in chanel_info.items():
                channel = key.encode('utf-8')
                chanel_list.append(channel)
            open_channel = chanel_list

        open_list = []
        for chl in open_channel:
            channel = chl.encode('utf-8')
            open_list.append(channel)


        good_list = range(1,8)
        reward_list = []
        for gid in good_list:
            good_name = dic.getlist("good_name{}".format(gid))
            good_number = dic.getlist("good_number{}".format(gid))
            login_dcit = {}
            props_data = []
            for key,value in zip(good_name,good_number):
                value = value.encode('utf-8')
                if value == "":
                    continue
                else:
                    props = ProcessInfo.get_for_deal(key,value)
                    if "chip" in props:
                        login_dcit.update(props)
                    if "diamond" in props:
                        login_dcit.update(props)
                    if "coupon" in props:
                        login_dcit.update(props)
                    if "target" in props:
                        login_dcit.update(props)
                    if "props" in props:
                        props_data.append(props["props"][0])

            login_dcit.update({"props":props_data})
            reward_list.append(login_dcit)

        rank_config = {
            'id': '301_2019-04-13',
            'model': 4,
            'tips': show,  # 0不显示 1 显示
            'order': order,  # 活动显示顺序
            'hot': hot,
            'show': 0,
            'name': activity_name,
            'start': start_day,
            'end': end_day,
            'channel': open_list,
            'desc': activity_desc,
            'reward': reward_list
        }

        url = '/v2/shell/activity/old_config'
        context = {"aid":4,"pid": 2, "ret": rank_config}
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)

        if ret.status_code == 200:
            info = "登录有礼设置成功!"
            msg = True
        else:
            info = "登录有礼设置失败!"
            msg = False
        return JsonResponse({'code': msg, 'info': info})


@decorator
def activity_share_config(request):
    """活动管理--关注有礼"""
    if request.method == 'GET':
        context = {"aid":5,"pid": 1}
        def_time = datetime.date.today().strftime('%Y-%m-%d')
        hot_name = Activity_Info.get_hot_type()
        old_data = ChannelList.objects.all().values('channel_data').first()
        chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道

        del chanel_info['1000']
        def_info = {"start": def_time, "end": def_time,"hot_name": hot_name,"chanel_info": chanel_info, "chanel_list": Context.json_dumps(chanel_info)}
        url = '/v2/shell/activity/old_config'
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.text)
        if not gift.has_key("ret"):
            gift_info = def_info
            return render(request, 'activity_manage/activity_share.html', gift_info)
        else:
            config_info = gift["ret"]
            if not config_info:
                gift_info = def_info
            else:
                if isinstance(config_info, list):
                    config = config_info[0]
                else:
                    config = config_info
                tips = config.get("tips", 0)
                name = config.get("name", "")
                order = config.get("order", 0)
                hot = config.get("hot", 0)
                desc = config.get("desc", "")
                start = config.get("start", "")
                end = config.get("end", "")
                channel_list = config.get("channel", [])
                del def_info['start']
                del def_info['end']
                gift_info = {"tips": tips, "name": name, "order": order, "hot": str(hot), "desc": desc, "start": start,"end": end,"channel_list": channel_list}
                gift_info.update(def_info)
            return render(request, 'activity_manage/activity_share.html', gift_info)
    else:
        dic = request.POST
        show = int(dic.get("show", 0))
        order = int(dic.get("order", 8))
        hot = int(dic.get("hot", 0))
        activity_name = dic.get("activity_name")
        activity_desc = dic.get("activity_desc")
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]
        open_channel = dic.getlist("channel",[])

        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"


        if len(open_channel) != len(set(open_channel)):
            info = "渠道数据重复!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) > 1:
            info = "渠道数据错误!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})
        if "0" in open_channel and len(open_channel) == 1:
            old_data = ChannelList.objects.all().values('channel_data').first()
            chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
            del chanel_info['0']
            del chanel_info['1000']
            chanel_list = []
            for key, value in chanel_info.items():
                channel = key.encode('utf-8')
                chanel_list.append(channel)
            open_channel = chanel_list

        open_list = []
        for chl in open_channel:
            channel = chl.encode('utf-8')
            open_list.append(channel)

        rank_config = {
            'id': '501_2019-04-19',
            'model': 5,
            'tips': show,  # 0不显示 1 显示
            'order': order,  # 活动显示顺序
            'hot': hot,
            'show': 0,
            'name': activity_name,
            'start': start_day,
            'end': end_day,
            'channel': open_list,
            'desc': activity_desc,
        }

        url = '/v2/shell/activity/old_config'
        context = {"aid":5,"pid": 2, "ret": rank_config}
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)

        if ret.status_code == 200:
            info = "关注有礼设置成功!"
            msg = True
        else:
            info = "关注有礼设置失败!"
            msg = False
        return JsonResponse({'code': msg, 'info': info})

@decorator
def activity_discount_config(request):
    """活动管理--直购特卖场"""
    if request.method == 'GET':
        context = {"aid":6,"pid": 1}
        def_time = datetime.date.today().strftime('%Y-%m-%d')
        hot_name = Activity_Info.get_hot_type()
        old_data = ChannelList.objects.all().values('channel_data').first()
        chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
        product_list = Activity_Info.product_config()  # 商品
        reward_info = range(0,2)

        del chanel_info['1000']
        def_info = {"start": def_time, "end": def_time,"hot_name": hot_name,"chanel_info": chanel_info, "chanel_list": Context.json_dumps(chanel_info), "product_list": product_list,"reward_info":reward_info}
        url = '/v2/shell/activity/old_config'
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.text)
        if not gift.has_key("ret"):
            gift_info = def_info
            return render(request, 'activity_manage/activity_discount.html', gift_info)
        else:
            config_info = gift["ret"]
            if not config_info:
                gift_info = def_info
            else:
                if isinstance(config_info, list):
                    config = config_info[0]
                else:
                    config = config_info
                reward_info = []
                tips = config.get("tips", 0)
                name = config.get("name", "")
                order = config.get("order", 0)
                hot = config.get("hot", 0)
                desc = config.get("desc", "")
                start = config.get("start", "")
                end = config.get("end", "")
                channel_list = config.get("channel", [])
                product = config.get("product", [])
                reward_info.append({"product_id":str(product[0].get("product_id"))})

                del def_info['start']
                del def_info['end']
                del def_info['reward_info']
                gift_info = {"tips": tips, "name": name, "order": order, "hot": str(hot), "desc": desc, "start": start,"end": end,"channel_list": channel_list,"reward_info":reward_info}
                gift_info.update(def_info)
            return render(request, 'activity_manage/activity_discount.html', gift_info)
    else:
        dic = request.POST
        show = int(dic.get("show", 0))
        order = int(dic.get("order", 8))
        hot = int(dic.get("hot", 0))
        activity_name = dic.get("activity_name")
        activity_desc = dic.get("activity_desc")
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]
        open_channel = dic.getlist("channel")

        product_id = dic.get("product_id").encode('utf-8')
        # discount = dic.get("discount").encode('utf-8')
        # price = dic.get("price").encode('utf-8')


        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"

        # if discount == "" or price == "":
        #     info = "请输入折扣或售价!"
        #     msg = False
        #     return JsonResponse({'code': msg, 'info': info})

        if len(open_channel) != len(set(open_channel)):
            info = "渠道数据重复!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) > 1:
            info = "渠道数据错误!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})
        if "0" in open_channel and len(open_channel) == 1:
            old_data = ChannelList.objects.all().values('channel_data').first()
            chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
            del chanel_info['0']
            del chanel_info['1000']
            chanel_list = []
            for key, value in chanel_info.items():
                channel = key.encode('utf-8')
                chanel_list.append(channel)
            open_channel = chanel_list

        open_list = []
        for chl in open_channel:
            channel = chl.encode('utf-8')
            open_list.append(channel)

        result = ProcessInfo.deal_product_id(product_id)
        product = []
        product.append({"type":1,"id":result["weaponid"],"product_id":product_id,"price":int(result["price"]),"discount":float(result["discount"])})
        rank_config = {
            'id': '601_2019-04-19',
            'model': 6,
            'tips': show,  # 0不显示 1 显示
            'order': order,  # 活动显示顺序
            'hot': hot,
            'show': 0,
            'name': activity_name,
            'start': start_day,
            'end': end_day,
            'channel': open_list,
            'desc': activity_desc,
            'product': product
        }
        url = '/v2/shell/activity/old_config'
        context = {"aid":6,"pid": 2, "ret": rank_config}
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)

        if ret.status_code == 200:
            info = "直购特卖场设置成功!"
            msg = True
        else:
            info = "直购特卖场设置失败!"
            msg = False
        return JsonResponse({'code': msg, 'info': info})

@decorator
def activity_give_config(request):
    """活动管理--神兵天降"""
    if request.method == 'GET':
        context = {"aid":7,"pid": 1}
        def_time = datetime.date.today().strftime('%Y-%m-%d')
        hot_name = Activity_Info.get_hot_type()
        old_data = ChannelList.objects.all().values('channel_data').first()
        chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
        give_reward = Activity_Info.give_weapon_data()  # 道具

        del chanel_info['1000']
        reward_list = [{"award_name":"中间"},{"award_name":"右上"},{"award_name":"左上"},{"award_name":"右下"},{"award_name":"左下"}]
        def_info = {"start": def_time, "end": def_time,"hot_name": hot_name,"chanel_info": chanel_info, "chanel_list": Context.json_dumps(chanel_info), "give_reward": give_reward,"reward_list":reward_list}
        url = '/v2/shell/activity/old_config'
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.text)
        if not gift.has_key("ret"):
            gift_info = def_info
            return render(request, 'activity_manage/activity_give.html', gift_info)
        else:
            config_info = gift["ret"]
            if not config_info:
                gift_info = def_info
            else:
                if isinstance(config_info, list):
                    config = config_info[0]
                else:
                    config = config_info
                tips = config.get("tips", 0)
                name = config.get("name", "")
                order = config.get("order", 0)
                hot = config.get("hot", 0)
                desc = config.get("desc", "")
                start = config.get("start", "")
                end = config.get("end", "")
                channel_list = config.get("channel", [])
                del def_info['start']
                del def_info['end']
                del def_info['reward_list']
                reward_list = ProcessInfo.deal_give_reward(config.get("rw_list", {}))
                gift_info = {"tips": tips, "name": name, "order": order, "hot": str(hot), "desc": desc, "start": start,"end": end,"channel_list": channel_list,"reward_list":reward_list}
                gift_info.update(def_info)
            return render(request, 'activity_manage/activity_give.html', gift_info)
    else:
        dic = request.POST
        show = int(dic.get("show", 0))
        order = int(dic.get("order", 12))
        hot = int(dic.get("hot", 0))
        activity_name = dic.get("activity_name")
        activity_desc = dic.get("activity_desc")
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]
        open_channel = dic.getlist("channel")

        good_name = dic.getlist("good_name")
        good_day = dic.getlist("good_day")
        good_number = dic.getlist("good_number")
        good_pay = dic.getlist("good_pay")

        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"

        for day,number in zip(good_day,good_number):
            day = day.encode('utf-8')
            number = number.encode('utf-8')
            if day == "" or number == "":
                info = "请输入奖励商品天数或数量!"
                msg = False
                return JsonResponse({'code': msg, 'info': info})

        for pay in good_pay:
            pay = pay.encode('utf-8')
            if pay == "":
                info = "请输入充值条件!"
                msg = False
                return JsonResponse({'code': msg, 'info': info})

        if len(open_channel) != len(set(open_channel)):
            info = "渠道数据重复!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) > 1:
            info = "渠道数据错误!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})
        if "0" in open_channel and len(open_channel) == 1:
            old_data = ChannelList.objects.all().values('channel_data').first()
            chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
            del chanel_info['0']
            del chanel_info['1000']
            chanel_list = []
            for key, value in chanel_info.items():
                channel = key.encode('utf-8')
                chanel_list.append(channel)
            open_channel = chanel_list

        open_list = []
        for chl in open_channel:
            channel = chl.encode('utf-8')
            open_list.append(channel)

        reward = {}
        rate = 0
        for key, value in zip(good_name, good_day):
            key_info = key.encode('utf-8')
            value = int(value)
            if key_info == "chip":
                need_pay = int(good_pay[rate])
                count = int(good_number[rate])
                props = ProcessInfo.get_for_deal(key_info,value,count)
                reward.update({need_pay:props})
            if key_info == "diamond":
                need_pay = int(good_pay[rate])
                count = int(good_number[rate])
                props = ProcessInfo.get_for_deal(key_info, value, count)
                reward.update({need_pay: props})
            if key_info == "coupon":
                need_pay = int(good_pay[rate])
                count = int(good_number[rate])
                props = ProcessInfo.get_for_deal(key_info, value, count)
                reward.update({need_pay: props})
            if key_info == "target":
                need_pay = int(good_pay[rate])
                count = int(good_number[rate])
                props = ProcessInfo.get_for_deal(key_info, value, count)
                reward.update({need_pay: props})
            if key_info.isdigit():
                need_pay = int(good_pay[rate])
                count = int(good_number[rate])
                props = ProcessInfo.get_for_deal(key_info, value, count)
                reward.update({need_pay: props})
            rate = rate +1

        config = {
            'id': '701_2019-04-19',
            'model': 7,
            'tips': show,  # 0不显示 1 显示
            'order': order,  # 活动显示顺序
            'hot': hot,
            'show': 0,
            'name': activity_name,
            'start': start_day,
            'end': end_day,
            'channel': open_list,
            'desc': activity_desc,
            'rw_list': reward
        }

        url = '/v2/shell/activity/old_config'
        context = {"aid":7,"pid": 2, "ret": config}
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)

        if ret.status_code == 200:
            info = "神兵天降设置成功!"
            msg = True
        else:
            info = "神兵天降设置失败!"
            msg = False
        return JsonResponse({'code': msg, 'info': info})

# ==========================五一活动==============================
@decorator
def may_day_make_proud(request):
    hot_name = Activity_Info.get_hot_type()
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info['1000']
    phone = request.session.get('uid')
    if request.method == 'GET':
        activity_info = {"hot_name": hot_name, "chanel_info": chanel_info,"chanel_list": Context.json_dumps(chanel_info)}
        url = '/v2/shell/activity/point_shop'
        context = {"pid": 1, "phone": phone}
        ret = Context.Controller.request(url, context)
        result = Context.json_loads(ret.text)
        config = result["ret"]
        if not config:
            day_time = datetime.date.today().strftime('%Y-%m-%d')
            may_day_list = range(0, 3)
            activity_info.update({"start": day_time, "end": day_time, "may_day_list": may_day_list})
        else:
            tips = config.get("tips", 0)
            name = config.get("name", "")
            order = config.get("order", 0)
            hot = config.get("hot", 0)
            desc = config.get("desc", "")
            start = config.get("start", "")
            end = config.get("end", "")
            shot_value = config.get("shot_value", 0)  # 洗码量
            shot_add = config.get("shot_add", 0)  # 加分
            channel_list = config.get("channel", [])
            reward = config.get("reward", [])
            may_day_list = ProcessInfo.deal_may_day_reward(reward)
            activity_info.update({"tips": tips, "name": name, "order": order, "hot": str(hot), "desc": desc, "start": start,"end": end, "shot_value": shot_value, "shot_add": shot_add, "channel_list": channel_list,"may_day_list": may_day_list})
        return render(request, 'activity_manage/may_day_activity.html', activity_info)
    else:
        dic = request.POST
        show = int(dic.get("show", 0))
        order = int(dic.get("order", 8))
        hot = int(dic.get("hot", 0))
        activity_name = dic.get("activity_name")
        activity_desc = dic.get("activity_desc")
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]
        open_channel = dic.getlist("channel")
        shot_value = int(dic.get("shot_value", 0))
        shot_add = int(dic.get("shot_add", 0))
        good_name = dic.getlist("good_name")
        good_number = dic.getlist("good_number")

        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"

        if len(open_channel) != len(set(open_channel)):
            info = "渠道数据重复!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) > 1:
            info = "渠道数据错误!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})
        if "0" in open_channel and len(open_channel) == 1:
            old_data = ChannelList.objects.all().values('channel_data').first()
            chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
            del chanel_info['0']
            del chanel_info['1000']
            chanel_list = []
            for key, value in chanel_info.items():
                channel = key.encode('utf-8')
                chanel_list.append(channel)
            open_channel = chanel_list

        open_list = []
        for chl in open_channel:
            channel = chl.encode('utf-8')
            open_list.append(channel)

        reward_data = []
        for name, count in zip(good_name, good_number):
            if name == u"" or count == u"":
                info = "请输入奖励配置!"
                msg = False
                return JsonResponse({'code': msg, 'info': info})
            else:
                name = name.encode('utf-8')
                count = int(count)
                reward_data.append({"product": {"name": name, "count": count}})
        config = {
            'id': '1501_2019-04-15',
            'model': 15,
            'tips': show,  # 0不显示 1 显示
            'order': order,  # 活动显示顺序
            'hot': hot,
            'show': 0,
            'count': 3,
            'name': activity_name,
            'start': start_day,
            'end': end_day,
            'shot_value': shot_value,
            'shot_add': shot_add,
            'channel': open_list,
            'desc': activity_desc,
            'level': [[1], [2], [3]],
            'reward': reward_data
        }

        url = '/v2/shell/activity/point_shop'
        context = {"pid": 2, "ret": config,"phone": phone}
        ret = Context.Controller.request(url, context)
        if ret.status_code == 200:
            info = "五一赚翻天设置成功!"
            msg = True
        else:
            info = "五一赚翻天设置失败!"
            msg = False
        return JsonResponse({'code': msg, 'info': info})


@decorator
def make_proud_query(request):
    phone,number = request.session.get('uid'),1
    url_date = "/activity_manage/make_proud_query/"
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page != None:
            conf, may_day = get_may_day_info(phone)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            may_day.update({"number": number, "page": page})
        else:
            day_time = datetime.date.today().strftime('%Y-%m-%d')
            may_day = {"start_day": day_time, "end_day": day_time, "page": [], "number": number}
    else:
        dic = request.POST
        start_time = dic.get("start_time")[:10]  # 查询开始时间
        end_time = dic.get("stop_time")[:10]  # 查询结束时间

        start_day,end_day = start_time + " 00:00:00",end_time + " 23:59:59"

        may_day = {"start_day": start_day, "end_day": end_day}
        keys = 'make_proud:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, may_day)

        day_start = Time.str_to_timestamp(start_day)
        day_end = Time.str_to_timestamp(end_day)

        res = MayDayRank.objects.filter(start_time__gte=day_start, start_time__lte=day_end).values("start_time", "end_time", "insert_time")
        if res:
            new_day_tamp = Time.current_ts()
            for act_data in res:
                start_stamp = int(act_data.get("start_time"))
                end_stamp = int(act_data.get("end_time"))
                insert_stamp = int(act_data.get("insert_time"))
                if end_stamp <= new_day_tamp and insert_stamp >= end_stamp:
                    continue
                else:
                    start_str = Time.timestamp_to_str(start_stamp)
                    insert_may_rank(phone, start_str, end_day)  # 插入数据
        else:
            insert_may_rank(phone, start_day, end_day)  # 插入数据

        May_list = []
        res_info = MayDayRank.objects.filter(start_time__gte=day_start, start_time__lte=day_end).values("start_time", "end_time", "channel")
        for data in res_info:
            start_stamp = int(data.get("start_time"))
            end_stamp = int(data.get("end_time"))
            channel_list = Context.json_loads(data.get("channel"))
            info = RankInfo.objects.filter(start_id=start_stamp, end_id=end_stamp).values("json_data")
            if len(info) > 0:
                user_list = info[:]  # queryset转为list
                play_info = []
                for user in user_list:
                    data_info = Context.json_loads(user.get("json_data"))
                    play_info.append(data_info)
            else:
                play_info = []

            start_str = Time.timestamp_to_str(start_stamp)
            end_str = Time.timestamp_to_str(end_stamp)

            May_list.append({"start_stamp": start_str, "end_stamp": end_str, "channel": channel_list, "play_info": play_info})
        sorted_info = sorted(May_list, key=lambda x: Time.str_to_timestamp(x['start_stamp']), reverse=True)

        paginator = Paginator(sorted_info, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页

        may_day.update({"page": page, "number": number})

    may_day.update({"url_date": url_date})
    return render(request, 'activity_manage/may_day_rank.html', may_day)


def insert_may_rank(phone,start_time,end_time):
    url = '/v2/shell/activity/point_shop'
    context = {"start": start_time, "end": end_time,"pid":3}
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    game_info = Context.json_loads(ret.text)
    if not game_info.has_key("ret"):
        return 0
    else:
        config_data = []
        config = game_info["ret"]
        for data in config:
            rank_dict = {}
            start_day = int(data.get("start",0))
            end_day = int(data.get("end",0))
            channel_list = data.get("channel",[])
            day_time = data["detail"].get("aid",0)
            rank_info = data["detail"].get("info",[])
            rank_dict.update({"start_day":start_day,"end_day":end_day,"channel":channel_list,"day_time":day_time,"info":rank_info})
            config_data.append(rank_dict)
        create_rank_info(config_data)


def get_may_day_info(phone):
    """五一排行榜详情--筛选条件"""
    keys = 'make_proud:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day"])  # 筛选条件
    start_time, end_time = result[0], result[1]
    def_info = {"start_day": start_time[:10], "end_day": end_time[:10]}

    day_start = Time.str_to_timestamp(start_time)
    day_end = Time.str_to_timestamp(end_time)

    May_list = []
    res_info = MayDayRank.objects.filter(start_time__gte=day_start, start_time__lte=day_end).values("start_time", "end_time", "channel")

    for data in res_info:
        start_stamp = data.get("start_time")
        end_stamp = data.get("end_time")
        channel_list = Context.json_loads(data.get("channel"))
        info = RankInfo.objects.filter(start_id=start_stamp,end_id=end_stamp).values("json_data")
        if len(info) > 0:
            user_list = info[:]  # queryset转为list
            play_info = []
            for user in user_list:
                data_info = Context.json_loads(user.get("json_data"))
                play_info.append(data_info)
        else:
            play_info = []

        start_str = Time.timestamp_to_str(start_stamp)
        end_str = Time.timestamp_to_str(end_stamp)
        May_list.append({"start_stamp": start_str, "end_stamp": end_str, "channel": channel_list, "play_info": play_info})

    sort_info = sorted(May_list, key=lambda x: Time.str_to_timestamp(x['start_stamp']), reverse=True)
    return sort_info,def_info


def create_rank_info(result):
    """创建五一排行榜详情"""
    rank_data = []
    may_day = []
    for m_info in result:
        start_time = m_info["start_day"]
        end_time = m_info["end_day"]
        channel = m_info["channel"]
        day_time = m_info["day_time"]
        rank_info = m_info["info"]

        res = MayDayRank.objects.filter(start_time=start_time,end_time=end_time)
        if res:
            MayDayRank.objects.filter(start_time=start_time,end_time=end_time).update(
                start_time=start_time,
                end_time=end_time,
                channel=Context.json_dumps(channel),
                day_time=day_time,
            )
        else:
            day_rank = MayDayRank(
                start_time=start_time,
                end_time=end_time,
                channel=Context.json_dumps(channel),
                day_time=day_time,
            )
            rank_data.append(day_rank)

        if len(rank_data) > 1000:
            MayDayRank.objects.bulk_create(rank_data)
            rank_data = []

        if len(rank_info) >0:
            may_day = create_May_day_info(rank_info,start_time,end_time)
        else:
            may_day = []
            continue
    RankInfo.objects.bulk_create(may_day)
    MayDayRank.objects.bulk_create(rank_data)


def create_May_day_info(result,start_time,end_time):
    """创建五一排行榜领取信息"""
    may_day = []
    for r_info in result:
        uid = int(r_info["id"])
        pay_point = int(r_info["point"]) - int(r_info["shot_point"])
        surplus_point = int(r_info["point"]) - int(r_info["use_point"])
        r_info.update({"pay_point":pay_point,"surplus_point":surplus_point})
        res = RankInfo.objects.filter(start_id=start_time, end_id=end_time,uid=uid)
        if res:
            RankInfo.objects.filter(start_id=start_time, end_id=end_time,uid=uid).update(
                start_id=start_time,
                end_id=end_time,
                uid=uid,
                json_data=Context.json_dumps(r_info),
            )
        else:
            day_info = RankInfo(
                start_id=start_time,
                end_id=end_time,
                uid=uid,
                json_data=Context.json_dumps(r_info),
            )
            may_day.append(day_info)

        if len(may_day) > 1000:
            RankInfo.objects.bulk_create(may_day)
            may_day = []

    return may_day


# ==========================欢乐砸金蛋==============================
@decorator
def smash_egg_alter(request):
    phone = request.session.get('uid')
    hot_name = Activity_Info.get_hot_type()
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info['1000']
    if request.method == 'GET':
        smash_info = {"hot_name": hot_name, "chanel_info": chanel_info,"chanel_list": Context.json_dumps(chanel_info)}
        reward_list = [{"name": "鸟蛋", "value": 1}, {"name": "钻石", "value": 2}, {"name": "鸟券", "value": 3},
                       {"name": "全屏冰冻", "value": 4}, {"name": "狂暴", "value": 5}, {"name": "超级武器", "value": 6},
                       {"name": "召唤", "value": 7}, {"name": "创房卡", "value": 8}, {"name": "臭蛋", "value": 9}
                       ]
        day_time = datetime.date.today().strftime('%Y-%m-%d')
        smash_info.update({"start": day_time, "end": day_time, "reward_list": reward_list})

        url = '/v2/shell/activity/smash_egg'
        context = {"aid": 1, "pid": 1,"phone": phone}
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.text)
        if not gift.has_key("ret"):
            return render(request, 'activity_manage/activity_smash_egg.html', smash_info)
        else:
            config = gift["ret"]
            if not config:
                return render(request, 'activity_manage/activity_smash_egg.html', smash_info)
            else:
                tips = config.get("tips", 0)
                name = config.get("name", "")
                order = config.get("order", 21)
                hot = config.get("hot", 0)
                desc = config.get("desc", "")
                start = config.get("start", "")
                end = config.get("end", "")
                add_hammer = config.get("add_hammer", 0)
                total_pay = config.get("pay", 0)  # 累计充值金额
                return_data = config.get("return", 0)  # 返利额度
                channel_list = config.get("channel", [])
                reward = config.get("reward", {})

                reward_list = ProcessInfo.deal_egg_reward(reward)
                gift_info = {"tips": tips, "name": name, "order": order, "hot": str(hot), "desc": desc, "start": start,
                             "end": end, "add_hammer": add_hammer, "total_pay": total_pay, "return_data": return_data,
                             "channel_list": channel_list, "reward_list": reward_list,"hot_name": hot_name,
                             "chanel_info": chanel_info,"chanel_list": Context.json_dumps(chanel_info)}
                return render(request, 'activity_manage/activity_smash_egg.html', gift_info)
    else:
        dic = request.POST
        show = int(dic.get("show", 0))
        order = int(dic.get("order", 21))
        hot = int(dic.get("hot", 0))
        activity_name = dic.get("activity_name")
        activity_desc = dic.get("activity_desc")
        add_hammer = int(dic.get("add_hammer"))
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]
        open_channel = dic.getlist("channel")
        need_pay = int(dic.get("pay", 0))
        return_data = int(dic.get("return", 0))
        min_list = dic.getlist("min_number")
        max_list = dic.getlist("max_number")
        rate_list = dic.getlist("rate")

        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"

        rate_number = 10000
        r_info = 0
        for rate_info in rate_list:
            if rate_info == "":
                info = "请输入出现概率!"
                msg = False
                return JsonResponse({'code': msg, 'info': info})
            else:
                r_info = int(rate_info) + r_info

        if r_info != rate_number:
            info = "出现概率数据异常!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})

        if len(open_channel) != len(set(open_channel)):
            info = "渠道数据重复!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) > 1:
            info = "渠道数据错误!"
            msg = False
            return JsonResponse({'code': msg, 'info': info})
        if "0" in open_channel and len(open_channel) == 1:
            old_data = ChannelList.objects.all().values('channel_data').first()
            chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
            del chanel_info['0']
            del chanel_info['1000']
            chanel_list = []
            for key, value in chanel_info.items():
                channel = key.encode('utf-8')
                chanel_list.append(channel)
            open_channel = chanel_list

        open_list = []
        for chl in open_channel:
            channel = chl.encode('utf-8')
            open_list.append(channel)

        reward = {}
        rate = 0
        for min, max in zip(min_list, max_list):
            if min == "" or max == "":
                info = "请输入最大值或最小值!"
                msg = False
                return JsonResponse({'code': msg, 'info': info})
            else:
                min,max = int(min),int(max)
                reward.update({str(rate + 1): {"min": min, "max": max, "rate": rate_list[rate]}})
                rate = rate + 1

        config = {
            'id': '1601_2019-04-19',
            'model': 16,
            'tips': show,  # 0不显示 1 显示
            'order': order,  # 活动显示顺序
            'hot': hot,
            'show': 0,
            'pay': need_pay,
            'return': return_data,
            'name': activity_name,
            'start': start_day,
            'end': end_day,
            "add_hammer": add_hammer,
            'channel': open_list,
            'desc': activity_desc,
            'reward': reward
        }

        url = '/v2/shell/activity/smash_egg'
        context = {"pid": 2, "ret": config}
        context.update({"phone": phone})
        ret = Context.Controller.request(url, context)

        if ret.status_code == 200:
            info = "欢乐砸金蛋设置成功!"
            msg = True
        else:
            info = "欢乐砸金蛋设置失败!"
            msg = False
        return JsonResponse({'code': msg, 'info': info})


# ==========================欢乐砸金蛋查询==============================
@decorator
def smash_egg_query(request):
    phone,number = request.session.get('uid'),1
    url_date = "/activity_manage/smash_egg_query/"
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info["1000"]
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page != None:
            conf, smash_info = get_egg_query_data(phone)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            smash_info.update({"number": number, "page": page})
        else:
            day_time = datetime.date.today().strftime('%Y-%m-%d')
            smash_info = {"start_day": day_time, "end_day": day_time,"channel": "0", "number": number}
    else:
        dic = request.POST
        start_time = dic.get("start_time")[:10]  # 查询开始时间
        end_time = dic.get("stop_time")[:10]  # 查询结束时间
        channel = dic.get('channel').encode('utf-8')  # 渠道name

        start_day, end_day = start_time + " 00:00:00", end_time + " 23:59:59"
        smash_info = {"start_day": start_day, "end_day": end_day, "channel": channel}
        keys = 'smash_egg:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, smash_info)

        day_start = Time.str_to_timestamp(start_day)
        day_end = Time.str_to_timestamp(end_day)

        res = EggQuery.objects.filter(start_time__gte=day_start, start_time__lte=day_end).values("start_time", "end_time", "insert_time")
        if res:
            new_day_tamp = Time.current_ts()
            for act_data in res:
                start_stamp = int(act_data.get("start_time"))
                end_stamp = int(act_data.get("end_time"))
                insert_stamp = int(act_data.get("insert_time"))
                if end_stamp <= new_day_tamp and insert_stamp >= end_stamp:
                    continue
                else:
                    start_str = Time.timestamp_to_str(start_stamp)
                    insert_egg_query(phone, start_str, end_day)  # 插入数据
        else:
            insert_egg_query(phone, start_day, end_day)  # 插入数据

        if channel == "0":
            res_info = EggQuery.objects.filter(start_time__gte=day_start, start_time__lte=day_end).values("json_data")
        else:
            res_info = EggQuery.objects.filter(start_time__gte=day_start, start_time__lte=day_end,channel__in=channel).values("json_data")

        query_info = []
        order = 1
        for data in res_info:
            egg_data = Context.json_loads(data.get("json_data"))
            egg_data.update({"order": order, "start_stamp": Time.timestamp_to_datetime(egg_data["start_day"]),"end_stamp": Time.timestamp_to_datetime(egg_data["end_day"])})
            query_info.append(egg_data)
            order += 1

        sorted_info = sorted(query_info, key=lambda x: int(x['start_day']), reverse=True)
        paginator = Paginator(sorted_info, 30)

        page, plist = Context.paging(paginator, 1)  # 翻页
        smash_info.update({"page": page, "number": number})
    smash_info.update({"url_date": url_date,"chanel_info": chanel_info})
    return render(request, 'activity_manage/smash_egg_query.html', smash_info)


def insert_egg_query(phone,start_time,end_time):
    url = '/v2/shell/activity/smash_egg'
    context = {"start": start_time, "end": end_time,"pid":3}
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    game_info = Context.json_loads(ret.text)
    if not game_info.has_key("ret"):
        return 0
    else:
        config_data = []
        config = game_info["ret"]
        for data in config:
            query_dict = {}
            start_day = int(data.get("start", 0))
            end_day = int(data.get("end", 0))
            channel_list = data.get("channel", [])
            aid = data["detail"].get("aid", 0)
            pay = int(data.get("pay", 0))
            query_info = data["detail"].get("info", [])
            query_dict.update({"start_day": start_day, "end_day": end_day, "channel": channel_list,"pay":pay,"aid": aid,"info": query_info})
            config_data.append(query_dict)
        create_egg_query(config_data)


def create_egg_query(result):
    """创建欢乐砸金蛋查询"""
    query_data = []
    may_day = []
    for m_info in result:
        start_time = m_info["start_day"]
        end_time = m_info["end_day"]
        channel = m_info["channel"]
        aid = m_info["aid"]
        rank_info = m_info["info"]
        count,money = 0,0
        for info in rank_info:
            chip = int(info.get("chip",0))
            money = money + chip
            count += 1
        m_info.update({"count":count,"money":int(money)/5000})
        del m_info["info"]

        res = EggQuery.objects.filter(start_time=start_time,end_time=end_time)
        if res:
            EggQuery.objects.filter(start_time=start_time,end_time=end_time).update(
                start_time=start_time,
                end_time=end_time,
                channel=Context.json_dumps(channel),
                aid=aid,
                json_data=Context.json_dumps(m_info),
            )
        else:
            day_rank = EggQuery(
                start_time=start_time,
                end_time=end_time,
                channel=Context.json_dumps(channel),
                aid=aid,
                json_data=Context.json_dumps(m_info),
            )
            query_data.append(day_rank)

        if len(query_data) > 1000:
            EggQuery.objects.bulk_create(query_data)
            query_data = []

        if len(rank_info) >0:
            may_day = create_egg_query_info(rank_info,aid)
        else:
            may_day = []
            continue
    EggQueryInfo.objects.bulk_create(may_day)
    EggQuery.objects.bulk_create(query_data)


def create_egg_query_info(result,aid):
    """创建欢乐砸金蛋领取信息"""
    may_day = []
    for r_info in result:
        uid = int(r_info["id"])
        res = EggQueryInfo.objects.filter(aid= aid,uid=uid)
        if res:
            EggQueryInfo.objects.filter(aid= aid,uid=uid).update(
                aid=aid,
                uid=uid,
                json_data=Context.json_dumps(r_info),
            )
        else:
            day_info = EggQueryInfo(
                aid=aid,
                uid=uid,
                json_data=Context.json_dumps(r_info),
            )
            may_day.append(day_info)

        if len(may_day) > 1000:
            EggQueryInfo.objects.bulk_create(may_day)
            may_day = []

    return may_day


def get_egg_query_data(phone):
    """欢乐砸金蛋--筛选条件"""
    keys = 'smash_egg:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day","channel"])  # 筛选条件
    start_time, end_time,channel = result[0], result[1], result[2]
    def_info = {"start_day": start_time[:10], "end_day": end_time[:10],"channel": channel}

    day_start = Time.str_to_timestamp(start_time)
    day_end = Time.str_to_timestamp(end_time)

    if channel == "0":
        res_info = EggQuery.objects.filter(start_time__gte=day_start, start_time__lte=day_end).values("json_data")
    else:
        res_info = EggQuery.objects.filter(start_time__gte=day_start, start_time__lte=day_end,channel__in=channel).values("json_data")

    query_info,order = [],1
    for data in res_info:
        egg_data = Context.json_loads(data.get("json_data"))
        egg_data.update({"order": order, "start_stamp": Time.timestamp_to_datetime(egg_data["start_day"]),"end_stamp": Time.timestamp_to_datetime(egg_data["end_day"])})
        query_info.append(egg_data)
        order += 1

    sorted_info = sorted(query_info, key=lambda x: int(x['start_day']), reverse=True)

    return sorted_info,def_info


def insert_red_packet_info(phone,start_time,end_time,red_type):
    url = '/v1/shell/gm/get_red_packet_info'
    context = {"start": start_time, "end": end_time,"red_type":red_type}
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.text)

    if "special" not in config and "special_timer" not in config:
        return 0
    else:
        special_info,new_special_timer = [],[]
        if red_type == 0:
            special_info = config.get("special")
        else:
            for timer in config["special_timer"]:
                all_packet_sum,all_get_money,all_send_gold,all_surplus = 0,0,0,0 #红包数量、领取红包个数、发红包的金额、剩余的红包金额
                single_red = []
                send_packet_list = Context.json_loads(timer["send_packet_list"])
                for red ,stamp in zip(timer["red_info"],send_packet_list):
                    red_dict,red_record = {},[]
                    all_packet_sum,all_get_money = all_packet_sum + int(red.get("packet_sum")),all_get_money + int(red.get("get_money"))
                    all_send_gold,all_surplus = all_send_gold + int(red.get("send_gold")),all_surplus + int(red.get("surplus"))

                    for key,value in red.items():
                        values = Context.json_loads(value)
                        if isinstance(values,dict):
                            red_record.append(values)
                        else:
                            continue
                    red_dict.update({stamp:red_record})
                    single_red.append(red_dict)

                timer.update({"user_info":single_red,"all_packet_sum":all_packet_sum,"all_get_money":all_get_money,"all_send_gold":all_send_gold,"all_surplus":all_surplus,"packet_list":send_packet_list})
                new_special_timer.append(timer)
        new_special_info = new_special_timer + special_info

        red_packet_list = []
        for info in new_special_info:
            user_info,red_packet_dic = [],{}
            if info.has_key('packet_sum'):
                if red_type == 0:
                    packet_sum = info["packet_sum"]
                    if packet_sum:
                        red_sum = int(re.findall(r"\d+\.?\d*", packet_sum)[0])
                    else:
                        red_sum = 0
                    red_packet_dic.update({"no_times": red_sum - int(info["get_money"]),"packet_sum": red_sum})
                    del info["packet_sum"]
                else:
                    red_packet_dic.update({"no_times": int(info["all_packet_sum"]) - int(info["all_get_money"])})
                    red_packet_dic.update({"packet_sum": info["packet_sum"],"all_packet_sum": info["all_packet_sum"]})
                    del info["all_packet_sum"]
            if info.has_key('get_money'):
                if red_type == 0:
                    red_packet_dic.update({"get_money": info["get_money"],"red_packet_type":red_type})
                    del info["get_money"]
                else:
                    red_packet_dic.update({"get_money": info["all_get_money"],"red_packet_type":red_type})
                    del info["all_get_money"]
            if info.has_key('surplus'):
                if red_type == 0:
                    surplus,send_gold = info["surplus"],info["send_gold"]
                    surplus = (int(surplus) if surplus else 0)
                    send_gold = (int(send_gold) if send_gold else 0)

                    red_packet_dic.update({"get_gold": send_gold - surplus})
                    red_packet_dic.update({"surplus": surplus})
                    del info["surplus"]
                else:
                    red_packet_dic.update({"get_gold": int(info["all_send_gold"]) - int(info["all_surplus"])})
                    red_packet_dic.update({"surplus": info["all_surplus"],"inter_time":int(info["interval_time"])/60})
                    del info["all_surplus"]
            if info.has_key('send_gold'):
                if red_type == 0:
                    red_packet_dic.update({"send_gold": info["send_gold"]})
                    del info["send_gold"]
                    red_packet_dic.update({"day_time": info["day_time"]})
                    red_packet_dic.update({"day_stamp": Time.str_to_timestamp(str(info["day_time"]))})
                    del info["day_time"]
                    if info.has_key("red_packet_type"):
                        del info["red_packet_type"]
                    special_id = info.get("special_id", "0")
                    packet_list =[]
                    for key, value in info.items():
                        values = Context.json_loads(value)
                        if isinstance(values, dict):
                            values.update({"special_id":special_id})
                            user_info.append(values)
                        else:
                            continue
                    packet_list.append(int(special_id))
                    red_packet_dic.update({"user_info": user_info, "special_id": special_id,"packet_list":packet_list})
                else:
                    start_tamp = int(info.get("start_today")) + int(info.get("start_hours"))
                    end_tamp = int(info.get("end_today")) + int(info.get("end_hours"))
                    red_packet_dic.update({"start_date": Time.timestamp_to_str(start_tamp), "end_date": Time.timestamp_to_str(end_tamp),"day_time": Time.timestamp_to_str(start_tamp)})
                    red_packet_dic.update({"day_stamp": start_tamp, "user_info": info.get("user_info"), "special_id": info["special_id"],"stop_state": int(info["stop_state"])})
                    red_packet_dic.update({"all_send_gold": info["all_send_gold"],"send_gold": info["send_gold"],"packet_list":info["packet_list"]})
                    del info["all_send_gold"]
            create_red_get_data(red_packet_dic["user_info"],red_type)
            del red_packet_dic["user_info"]
            red_packet_list.append(red_packet_dic)
        # sorted_info = sorted(red_packet_list, key=lambda x: Time.str_to_timestamp(x["day_time"]), reverse=True)
        # RedPacketInfo.objects.all().delete()
        create_red_packet_info(red_packet_list)


def create_red_packet_info(result):
    """红包--数据"""
    red_data = []
    for m_info in result:
        day_time = str(m_info["day_time"])[:10]
        day_stamp = int(m_info["day_stamp"])
        special_id = m_info["special_id"]
        stop_state = int(m_info.get("stop_state",1))
        special_end_time = m_info.get("end_date",m_info["day_time"])
        red_packet_type = int(m_info.get("red_packet_type"))
        end_stamp = Time.str_to_timestamp(special_end_time)
        date_time = datetime.datetime.now().strftime('%Y-%m-%d')
        res = RedPacketInfo.objects.filter(day_time=day_time,special_end_time=end_stamp)
        if res:
            RedPacketInfo.objects.filter(day_time=day_time,special_end_time=end_stamp).update(
                special_end_time=end_stamp,
                stop_state=stop_state,
                special_id=special_id,
                red_packet_type=red_packet_type,
                day_time=day_time,
                day_stamp=day_stamp,
                json_data=json.dumps(m_info),
                insert_time=date_time,
            )
        else:
            red_packet = RedPacketInfo(
                special_end_time=end_stamp,
                stop_state=stop_state,
                special_id=special_id,
                red_packet_type=red_packet_type,
                day_time=day_time,
                day_stamp=day_stamp,
                json_data=json.dumps(m_info),
                insert_time=date_time,
            )
            red_data.append(red_packet)

        if len(red_data) > 1000:
            RedPacketInfo.objects.bulk_create(red_data)
            red_data = []
    RedPacketInfo.objects.bulk_create(red_data)


def create_red_get_data(user_data,red_type):
    """红包领取--信息"""
    if red_type == 0:
        insert_get_info(user_data)
    else:
        for each_data in user_data:
            for key,values in each_data.items():
                result = []
                if len(values)>0:
                    for red_info in values:
                        red_info.update({"special_id":key})
                        result.append(red_info)
                    insert_get_info(result)
                else:
                    continue


def insert_get_info(result):
    """插入领取红包信息"""

    red_data = []
    for m_info in result:
        special_id = str(m_info["special_id"])
        uid = int(m_info["uid"])
        nick = m_info["nick"]
        packet = int(m_info["packet"])
        time = m_info["times"]

        res = RedGetData.objects.filter(red_packet_id=special_id,uid=uid)
        if res:
            RedGetData.objects.filter(red_packet_id=special_id,uid=uid).update(
                red_packet_id=special_id,
                uid=uid,
                nick=nick,
                packet=packet,
                time=time,
            )
        else:
            red_packet = RedGetData(
                red_packet_id=special_id,
                uid=uid,
                nick=nick,
                packet=packet,
                time=time,
            )
            red_data.append(red_packet)

        if len(red_data) > 1000:
            RedGetData.objects.bulk_create(red_data)
            red_data = []

    RedGetData.objects.bulk_create(red_data)


def get_red_packet(phone):
    """红包--筛选条件"""
    keys = 'red_packet:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day", "red_type"])  # 筛选条件
    start_time, end_time,red_type = result[0], result[1], result[2]
    def_info = {"start_day": start_time, "end_day": end_time,"red_type":str(red_type)}

    start_date, end_date = Time.str_to_datetime(start_time, '%Y-%m-%d'), Time.str_to_datetime(end_time, '%Y-%m-%d')
    res_info = RedPacketInfo.objects.filter(day_time__range=[start_date, end_date], red_packet_type=red_type).values('json_data').order_by("-day_stamp")

    order,config = 1,[]
    for date in res_info:
        red_data = Context.json_loads(date.get("json_data"))
        packet_info = []
        for packet in red_data["packet_list"]:
            packet_id = str(packet)
            info = RedGetData.objects.filter(red_packet_id=packet_id).values("uid", "nick", "packet", "time")
            if len(info) > 0:
                data_list = info[:]  # queryset转为list
                packet_info.append(data_list)
            else:
                continue
        red_data.update({"order": order, "user_info": packet_info})
        config.append(red_data)
        order = order + 1

    return config, def_info


@decorator
def month_card_alter(request):
    """月卡"""
    phone = request.session.get('uid')
    if request.method == 'GET':
        info = {}
        return render(request, 'activity_manage/month_card.html', info)
    else:
        dic = request.POST
        profit = dic.get('profit')  # 返利
        open = dic.get('show')  # 开关
        price = dic.get('price')  # 售价
        shot_value = dic.get('shot_value')  # 礼包描述
        total = dic.get('total')  # 总价值
        channel = dic.getlist('channel')  # 渠道
        good_name = dic.getlist('good_name')  # 商品名
        day_count = dic.getlist('day_count')  # 商品数量
        rw = dict(zip(good_name, day_count))
        props_id = dic.get('props_id')
        props_count = dic.get('props_count')
        rw.update({'props': [{'id': props_id, 'count': props_count}]})
        main_good_name = dic.get('main_good_name')
        main_day_count = dic.get('main_day_count')
        url = '/v2/shell/month_card'
        msg = True
        info = ""
        return JsonResponse({'code': msg, 'info': info})


@decorator
def new_user_and_vip_gift(request):
    """活动管理--新手活动礼包 vip活动礼包"""
    phone = request.session.get('uid')
    hot_name = Activity_Info.get_hot_type()
    give_reward = Activity_Info.give_props_data()  # 道具
    weapon_list = Activity_Info.give_weapon_data()  # 武器
    give_reward.extend(weapon_list)
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info['1000']
    if request.method == 'GET':
        dic = request.GET
        model = int(dic.get("model", 3))
        day_time = datetime.date.today().strftime('%Y-%m-%d')
        if model == 3:
            context = {"pid": 5}
            price = 6
        else:
            context = {"pid": 7}
            price = 128
        new_and_vip = {"hot_name": hot_name, "chanel_info": chanel_info, "chanel_list": Context.json_dumps(chanel_info),"give_reward": give_reward, "give_list": Context.json_dumps(give_reward)}
        new_and_vip.update({"start": day_time, "end": day_time, "price": price, 'model': model,"reward_list": []})

        url = '/v2/shell/activity/gift_box'
        context.update({"phone": phone})
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.text)
        if not gift.has_key("ret"):
            return render(request, 'activity_manage/new_activity_gift.html', new_and_vip)
        else:
            gift_one = gift["ret"]
            if not gift_one:
                return render(request, 'activity_manage/new_activity_gift.html', new_and_vip)
            else:
                if model == 3:
                    limit = gift_one.get('create_day', 10)
                else:
                    limit = gift_one.get('vip_limit', 10)
                tips = gift_one.get("tips", 0)
                name = gift_one.get("name", "")
                order = gift_one.get("order", 0)
                hot = gift_one.get("hot", 0)
                desc = gift_one.get("desc", "")
                start = gift_one.get("start", "")
                end = gift_one.get("end", "")
                discount = gift_one.get("discount", 0)  # 折扣
                price = gift_one.get("price", 0)  # 充值金额
                channel_list = gift_one.get("channel", [])
                reward = gift_one.get("gift", {})
                reward_list = ProcessInfo.deal_gift_reward(reward)
                reward_len = len(reward_list)
                gift_info = {"tips": tips, "name": name,"price": price,"order": order, "hot": hot, "desc": desc, "start": start,'limit': limit,
                             "end": end, "discount": discount, "channel_list": channel_list, "reward_list": reward_list,"reward_len": reward_len}
                return render(request, 'activity_manage/new_activity_gift.html', gift_info)
    else:
        dic = request.POST
        model = int(dic.get("model", 3))
        show = int(dic.get("show", 0))
        order = int(dic.get("order", 1))
        hot = int(dic.get("hot", 0))
        activity_name = dic.get("activity_name")
        activity_desc = dic.get("activity_desc")
        start_time = dic.get('start_time')  # [:10]
        end_time = dic.get('stop_time')  # [:10]
        open_channel = dic.getlist("channel")
        pay_money = float(dic.get("pay_money", 0))
        discount = float(dic.get("discount", 0))
        good_name = dic.getlist("good_name")
        good_number = dic.getlist("good_number")
        limit = dic.getlist('limit')
        start_day = start_time  # + " 00:00:00"
        end_day = end_time  # + " 23:59:59"

        for num in good_number:
            try:
                num = int(num)
            except ValueError:
                info = '商品数量必须为正整數'
                msg = False
                return {'code': msg, 'info': info}
            if num <= 0:
                info = '商品数量必须为大于0'
                msg = False
                return {'code': msg, 'info': info}
        if not limit[0]:
            info = '请输入活动限制'
            msg = False
            return {'code': msg, 'info': info}

        if not limit[0].isdigit():
            info = '活动限制必须输入整数'
            msg = False
            return {'code': msg, 'info': info}

        if model == 4 and int(limit[0]) > 12:
            info = 'vip活动限制不正确!'
            msg = False
            return {'code': msg, 'info': info}

        if len(open_channel) != len(set(open_channel)):
            info = "渠道数据重复!"
            msg = False
            return {'code': msg, 'info': info}

        if "0" in open_channel and len(open_channel) > 1:
            info = "渠道数据错误!"
            msg = False
            return {'code': msg, 'info': info}
        if "0" in open_channel and len(open_channel) == 1:
            old_data = ChannelList.objects.all().values('channel_data').first()
            chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
            del chanel_info['0']
            del chanel_info['1000']
            chanel_list = []
            for key, value in chanel_info.items():
                channel = key.encode('utf-8')
                chanel_list.append(channel)
            open_channel = chanel_list

        open_list = []
        for chl in open_channel:
            channel = chl.encode('utf-8')
            open_list.append(channel)

        gift_name = []
        gift_number = []
        for g_name, g_value in zip(good_name, good_number):
            g_value = g_value.encode('utf-8')
            if g_value == "":
                continue
            else:
                g_name = g_name.encode('utf-8')
                gift_name.append(g_name)
                gift_number.append(g_value)

        if len(gift_name) != len(set(gift_name)):
            info = "礼包商品数据重复!"
            msg = False
            return {'code': msg, 'info': info}
        reward = {}
        prop = []
        weapon_list = []
        for key, value in zip(gift_name, gift_number):
            props_info = {}
            key = key.encode('utf-8')
            values = value.encode('utf-8')
            if values == "life" and key.isdigit():
                if int(key) > 20000:
                    weapon_list.append(int(key))
                    reward.update({"weapon": weapon_list})
                    continue
                else:
                    info = "商品数量异常!"
                    msg = False
                    return {'code': msg, 'info': info}
            else:
                value = int(values)
                if key == "chip":
                    reward.update({key: value})
                elif key == "diamond":
                    reward.update({key: value})
                elif key == "coupon":
                    reward.update({key: value})
                elif key == "target":
                    reward.update({key: value})
                elif key == "auto_shot":
                    reward.update({key: value})
                else:
                    key = int(key)
                    if key > 20000:
                        new_key = key * 1000 + value
                        props_info.update({"id": new_key, "count": 1})
                    else:
                        props_info.update({"id": key, "count": value})
                    prop.append(props_info)
                    reward.update({"props": prop})

        if not reward:
            info = "商品不能为空!"
            msg = False
            return {'code': msg, 'info': info}

        if model == 3:
            model_name = 17
            productId = 101113
            pid = 6
        else:
            model_name = 18
            productId = 101114
            pid = 8

        activity_gift = {
            'id': '1301_2019-03-22',
            'model': model_name,
            'type': 1,
            'tips': show,  # 0不显示 1 显示
            'order': order,  # 活动显示顺序
            'hot': hot,
            'show': 0,
            'price': pay_money,
            'discount': discount,
            'name': activity_name,
            'start': start_day,
            'end': end_day,
            'channel': open_list,
            'productId': productId,
            'desc': activity_desc,
            'gift': reward,
        }
        if model == 3:
            activity_gift['create_day'] = int(limit[0])
        elif model == 4:
            activity_gift['vip_limit'] = int(limit[0])

        url = '/v2/shell/activity/gift_box'
        context = {"pid": pid, "ret": activity_gift, "phone": phone}
        ret = Context.Controller.request(url, context)
        if ret.status_code == 200:
            info = "活动礼包设置成功!"
            msg = True
        else:
            info = "活动礼包设置失败!"
            msg = False
        return {'code': msg, 'info': info}


# ==========================端午节活动==============================
@decorator
def dragon_boat_alter(request):
    phone = request.session.get('uid')
    hot_name = Activity_Info.get_hot_type()
    give_reward = Activity_Info.give_props_data()  # 道具
    weapon_list = Activity_Info.give_weapon_data()  # 武器
    give_reward.extend(weapon_list)
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info['1000']
    if request.method == 'GET':
        festival_info = {"hot_name": hot_name, "chanel_info": chanel_info, "chanel_list": Context.json_dumps(chanel_info), "give_reward":give_reward}
        day_time = datetime.date.today().strftime('%Y-%m-%d')
        price = {'A': "", "B": "", "C": "", "D": ""}
        dragon_list = {u'0': {'limit': "", 'need': {u'A': '', 'B': '', 'C': '', 'D': ''},
                       'reward': [{'option': 'chip', 'value': ''}, {'option': 'chip', 'value': ''}]}
                       }
        festival_info.update({"start": day_time, "end": day_time, "show_end": day_time, "price": price, "Dragon_list": dragon_list})
        url = '/v2/shell/activity/dragon_boat'
        context = {"pid": 1,"phone":phone}
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.text)
        if not gift.has_key("ret"):
            return render(request, 'activity_manage/dragon_boat_fstival.html', festival_info)
        else:
            config = gift["ret"]
            if not config:
                return render(request, 'activity_manage/dragon_boat_fstival.html', festival_info)
            else:
                tips = config.get("tips", 0)
                name = config.get("name", "")
                order = config.get("order", 0)
                hot = config.get("hot", 0)
                desc = config.get("desc", "")
                start = config.get("start", "")
                end = config.get("end", "")
                show_end = config.get("show_end", "")  # 活动关闭时间
                price = config.get("price", {})
                channel_list = config.get("channel", [])
                reward_list = ProcessInfo.deal_Dragon_Boat(config.get("rw_list", {}))
                gift_info = {"tips": tips, "name": name, "order": order, "hot": str(hot), "desc": desc, "start": start,"end": end,
                             "show_end": show_end, "price": price, "channel_list": channel_list,"Dragon_list": reward_list,
                             "hot_name": hot_name, "chanel_info": chanel_info, "chanel_list": Context.json_dumps(chanel_info), "give_reward":give_reward}
                return render(request, 'activity_manage/dragon_boat_fstival.html', gift_info)
    else:
        dic = request.POST
        show = int(dic.get("show", 0))
        order = int(dic.get("order", 26))
        hot = int(dic.get("hot", 0))
        activity_name = dic.get("activity_title")
        activity_desc = dic.get("activity_desc")
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]
        show_time = dic.get('close_time')[:10]

        price_list = dic.getlist("price")
        good_name = dic.getlist("good_name")
        good_number = dic.getlist("good_number")
        A_list = dic.getlist("A")
        B_list = dic.getlist("B")
        C_list = dic.getlist("C")
        D_list = dic.getlist("D")
        limit_list = dic.getlist("limit")
        limit_count = dic.getlist("limit_count")

        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"
        show_time = show_time + " 23:59:59"

        price_key = ["A", "B", "C", "D"]
        price_info = {}
        for letter, value in zip(price_key, price_list):
            chip = value.encode('utf-8')
            if chip == "":
                continue
            else:
                price_info.update({letter: int(chip)})
        dragon_name,dragon_number,n = [],[],2
        new_good_name = [good_name[i:i + n] for i in range(0, len(good_name), n)]
        new_good_number = [good_number[i:i + n] for i in range(0, len(good_number), n)]
        for d_name, d_value in zip(new_good_name, new_good_number):
            boat_name = []
            boat_number = []
            for g_name, g_value in zip(d_name, d_value):
                g_value = g_value.encode('utf-8')
                if g_value == "":
                    continue
                else:
                    g_name = g_name.encode('utf-8')
                    boat_name.append(g_name)
                    boat_number.append(g_value)

            if len(boat_name) != len(set(boat_name)):
                info = "奖励商品数据重复!"
                msg = False
                return JsonResponse({'code': msg, 'info': info})

            dragon_name.append(boat_name)
            dragon_number.append(boat_number)

        reward_info = {}
        index = 0
        for gift_name, gift_number, A, B, C, D, limit, count in zip(dragon_name, dragon_number, A_list, B_list, C_list,D_list, limit_list, limit_count):
            reward_dict = {}
            need = {}
            reward = ProcessInfo.deal_auto_shot_reward(gift_name, gift_number)
            if not reward:
                info = "请输入奖励数量!"
                msg = False
                return JsonResponse({'code': msg, 'info': info})
            else:
                reward_dict.update({"reward": reward})
            A, B, C, D = A.encode('utf-8'), B.encode('utf-8'), C.encode('utf-8'), D.encode('utf-8')
            if A != "":
                need["A"] = int(A)
            if B != "":
                need["B"] = int(B)
            if C != "":
                need["C"] = int(C)
            if D != "":
                need["D"] = int(D)
            reward_dict.update({"need": need})
            limit, count = limit.encode('utf-8'), count.encode('utf-8')
            if limit == "1":
                reward_dict.update({"limit": int(count)})

            reward_info.update({str(index): reward_dict})
            index = index + 1

        config = {
            'id': '1501_2019-05-27',
            'model': 19,
            'tips': show,
            'order': order,
            'hot': hot,
            'show': 0,
            'count': 3,
            'name': activity_name,
            'start': start_day,
            'end': end_day,
            'show_end': show_time,
            'price': price_info,
            'desc': activity_desc,
            'rw_list': reward_info
        }
        url = '/v2/shell/activity/dragon_boat'
        context = {"pid": 2, "ret": config}
        context.update({"phone": phone})
        ret = Context.Controller.request(url, context)
        result = Context.json_loads(ret.text)
        if result.has_key("error"):
            if result["error"] == 1:
                info = "活动已开启，不可修改时间!"
                msg = False
            else:
                info = "端午活动设置失败!"
                msg = False
        else:
            info = "端午活动设置成功!"
            msg = True
        return JsonResponse({'code': msg, 'info': info})


# ==========================端午节活动详情==============================
@decorator
def dragon_boat_query(request):
    phone,number = request.session.get('uid'),1
    url_date = "/activity_manage/dragon_boat_query/"
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info["1000"]
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page != None:
            conf, compute_info = get_dragon_boat_data(phone)
        else:
            conf, compute_info = 0, {"uid": ""}
        festival_info = Context.get_Get_info(url_date, one_page, conf, compute_info)
    else:
        dic = request.POST
        start_time = dic.get("start_time")[:10]  # 查询开始时间
        end_time = dic.get("stop_time")[:10]  # 查询结束时间
        channel = dic.get('channel').encode('utf-8')  # 渠道name
        uid = dic.get('uid').encode('utf-8')

        start_day,end_day = start_time + " 00:00:00",end_time + " 23:59:59"
        festival_info = {"start_day": start_time, "end_day": end_time, "channel": channel, "uid": uid}
        keys = "dragon_boat:{}:{}".format(phone, "query")
        Context.RedisMatch.hash_mset(keys, festival_info)

        day_start = Time.str_to_timestamp(start_day)
        day_end = Time.str_to_timestamp(end_day)
        res = DragonBoat.objects.filter(start_time__gte=day_start, start_time__lte=day_end).values("start_time","end_time","insert_time")
        if res:
            new_day_tamp = Time.current_ts()
            for act_data in res:
                start_stamp = int(act_data.get("start_time"))
                end_stamp = int(act_data.get("end_time"))
                insert_stamp = int(act_data.get("insert_time"))
                if end_stamp <= new_day_tamp and insert_stamp >= end_stamp:
                    continue
                else:
                    start_str = Time.timestamp_to_str(start_stamp)
                    insert_dragon_boat(phone, start_str, end_day)  # 插入数据
        else:
            insert_dragon_boat(phone, start_day, end_day)  # 插入数据

        if channel == "0" and uid == "":
            res_info = DragonBoat.objects.filter(start_time__gte=start_stamp, start_time__lte=end_stamp).values("json_data")
        elif channel != "0" and uid == "":
            res_info = DragonBoat.objects.filter(start_time__gte=start_stamp, start_time__lte=end_stamp,channel=channel).values("json_data")
        elif channel == "0" and uid != "":
            res_info = DragonBoat.objects.filter(start_time__gte=start_stamp, start_time__lte=end_stamp,uid=uid).values("json_data")
        else:
            res_info = DragonBoat.objects.filter(start_time__gte=start_stamp, start_time__lte=end_stamp,channel=channel,uid=uid).values("json_data")

        query_info = []
        for data in res_info:
            festival = Context.json_loads(data.get("json_data"))
            start_time = Time.timestamp_to_datetime(festival["start_day"])
            end_time = Time.timestamp_to_datetime(festival["end_day"])
            festival.update({"start_time": start_time, "end_time": end_time})
            query_info.append(festival)

        sorted_info = sorted(query_info, key=lambda x: int(x['start_day']), reverse=True)
        paginator = Paginator(sorted_info, 30)
        page, plist = Context.paging(paginator, 1)
        festival_info.update({"page": page, "number": number})

    festival_info.update({"chanel_info": chanel_info, "url_date": url_date})
    return render(request, 'activity_manage/dragon_boat_particulars.html', festival_info)


def insert_dragon_boat(phone, start_time, end_time):
    url = '/v2/shell/activity/dragon_boat'
    context = {"start": start_time, "end": end_time, "pid": 5}
    msg, config_info = Context.get_server_data(url, context, phone)
    if msg:
        create_dragon_boat_data(config_info)
    else:
        return 0


def create_dragon_boat_data(result):
    """创建端午节活动详情"""
    query_data = []
    insert_time = Time.current_ts()
    for day_time,user in result.items():
        start_time = Time.str_to_timestamp(day_time,'%Y-%m-%d')
        for uid, info in user.items():
            user_dict,in_zongzi,out_zongzi = {},{},{}
            ua,ub,uc,ud = int(info.get("ua", 0)),int(info.get("ub", 0)),int(info.get("uc", 0)),int(info.get("ud", 0))
            la, lb, lc, ld = int(info.get("la", 0)), int(info.get("lb", 0)), int(info.get("lc", 0)), int(info.get("ld", 0))
            in_zongzi.update({"A": ua + la, "B": ub + lb, "C": uc + lc, "D": ud + ld})
            out_zongzi.update({"A": ua,"B": ub,"C": uc,"D": ud})
            channel,phone,nick = info.get("c", 0),info.get("p", 0),info.get("n", "")
            reward = info.get("rw", {})
            end_time = info.get("e", 0)
            if end_time:
                end_time = Time.str_to_timestamp(end_time,'%Y-%m-%d')
            else:
                end_time = start_time
            user_dict.update({"start_day":start_time,"end_day":end_time,"uid":uid,"reward":reward,"c":channel,"p":phone,"nick":nick,"out_zongzi":out_zongzi,"in_zongzi":in_zongzi})
            res = DragonBoat.objects.filter(start_time=start_time,end_time=end_time,uid=uid)
            if res:
                DragonBoat.objects.filter(start_time=start_time,end_time=end_time,uid=uid).update(
                    start_time=start_time,
                    end_time=end_time,
                    insert_time=insert_time,
                    channel=channel,
                    uid=uid,
                    json_data=Context.json_dumps(user_dict),
                )
            else:
                day_data = DragonBoat(
                    start_time=start_time,
                    end_time=end_time,
                    insert_time=insert_time,
                    channel=channel,
                    uid=uid,
                    json_data=Context.json_dumps(user_dict),
                )
                query_data.append(day_data)

            if len(query_data) > 1000:
                DragonBoat.objects.bulk_create(query_data)
                query_data = []

    DragonBoat.objects.bulk_create(query_data)


def get_dragon_boat_data(phone):
    """端午节活动--筛选条件"""
    query_info = []
    keys = "dragon_boat:{}:{}".format(phone, "query")
    start_time,end_time,channel,uid = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day","channel", "uid"])
    start_stamp = Time.str_to_timestamp(start_time)
    end_stamp = Time.str_to_timestamp(end_time)

    def_info = {"start_day": start_time[:10], "end_day": end_time[:10], "uid": uid, "channel":channel}

    if channel == "0" and uid == "":
        res_info = DragonBoat.objects.filter(start_time__gte=start_stamp, end_time__lte=end_stamp).values("json_data")
    elif channel != "0" and uid == "":
        res_info = DragonBoat.objects.filter(start_time__gte=start_stamp, end_time__lte=end_stamp, channel=channel).values("json_data")
    elif channel == "0" and uid != "":
        res_info = DragonBoat.objects.filter(start_time__gte=start_stamp, end_time__lte=end_stamp, uid=uid).values("json_data")
    else:
        res_info = DragonBoat.objects.filter(start_time__gte=start_stamp, end_time__lte=end_stamp, channel=channel, uid=uid).values("json_data")

    for data in res_info:
        festival = Context.json_loads(data.get("json_data"))
        start_time = Time.timestamp_to_datetime(festival["start_day"])
        end_time = Time.timestamp_to_datetime(festival["end_day"])
        festival.update({"start_time": start_time, "end_time": end_time})
        query_info.append(festival)

    sorted_info = sorted(query_info, key=lambda x: int(x['start_day']), reverse=True)
    return sorted_info,def_info


@decorator
def luxury_gifts(request, lid):
    phone = request.session.get('uid')
    lid = int(lid)
    give_reward = Activity_Info.give_props_data()  # 道具
    weapon_list = Activity_Info.give_weapon_data()  # 武器
    give_reward.extend(weapon_list)
    month_list = Activity_Info.get_month()
    vip_list = Shop.shop_vip_grade()  #vip等级
    if request.method == 'GET':
        gifts_info = {"vip_info": vip_list, "vip_list": Context.json_dumps(vip_list), "month_list": month_list,"give_reward": give_reward}
        now_month = request.GET.get('month')
        if now_month is None:
            today = datetime.datetime.today()
            month = calendar.monthrange(today.year, today.month)[1]
        else:
            month = now_month
        url = '/v2/shell/sign_in_config'
        context = {"phone": phone, "pid": 1, "level": month}
        ret = Context.Controller.request(url, context)
        gifts = Context.json_loads(ret.text)
        if "ret" not in gifts or "level" not in gifts:
            login_list = []
            for index in range(1, month + 1):
                reward = {"days": index}
                login_list.append(reward)
            many_list = [{"days": 3}, {"days": 5}, {"days": 7}, {"days": 10}, {"days": 15}, {"days": 20}, {"days": month}]
            gifts_info.update({"month": str(month), "login_reward": login_list, "series_list": many_list})
        else:
            luxury, month = gifts["ret"], int(gifts["level"])
            if luxury:
                luxury_list, series_list, vip_level = [], [], []
                for index, value in luxury["date"].items():
                    login_info, days = {}, int(index)
                    reward = value.get("rw", {})
                    result1 = ProcessInfo.get_reward_info(reward)
                    add_info = value.get("add", {})
                    if add_info:
                        vip, multiple = str(add_info.get("vip", 0)), add_info.get("multiple", "")
                    else:
                        vip, multiple = 0, ""
                    result1.update({"vip": vip, "multiple": multiple})
                    login_info.update({"days": days, "reward": result1})
                    luxury_list.append(login_info)

                for index, series in luxury["continue"].items():
                    series_info, vip_info, days = {}, [], int(index)
                    reward = series.get("rw", {})
                    result2 = ProcessInfo.get_reward_info(reward)
                    add_list = series.get("add", [])
                    for m_vip in add_list:
                        vip_dict = {}
                        vip_dict.update({"vip": str(m_vip.get("vip", "0")), "multiple": m_vip.get("multiple", 0)})
                        vip_info.append(vip_dict)
                    series_info.update({"days": days, "reward": result2, "add_vip": vip_info})
                    series_list.append(series_info)

                for vip in luxury["complement"]:
                    level_dict = {}
                    rang, number = vip[0], vip[1]
                    level_dict.update({"start": rang[0], "end": rang[len(rang) - 1], "number": number})
                    vip_level.append(level_dict)
                gifts_info.update({"month": str(month), "login_reward": luxury_list, "series_list": series_list,"vip_range": vip_level})
            else:
                login_list = []
                for index in range(1, month + 1):
                    reward = {"days": index}
                    login_list.append(reward)
                many_list = [{"days": 3}, {"days": 5}, {"days": 7}, {"days": 10}, {"days": 15}, {"days": 20}, {"days": month}]
                gifts_info.update({"month": str(month), "login_reward": login_list, "series_list": many_list})
        return render(request, 'activity_manage/login_luxury_gifts.html', gifts_info)
    else:
        dic = request.POST
        lid = int(dic.get("lid", 0))

        sign_name,sign_number = dic.getlist("sign_name"),dic.getlist("sign_number")
        sign_vip,sign_multiple = dic.getlist("sign_vip"),dic.getlist("sign_multiple")
        sign,sign_info = 1,{}
        for nu_sign,na_sign,vi_sign,mul_sign in zip(sign_number,sign_name,sign_vip,sign_multiple):
            login_info,add = {},{}
            nu_sign = nu_sign.encode('utf-8')
            mul_sign = mul_sign.encode('utf-8')
            if nu_sign != "":
                nu_sign = int(nu_sign)
                reward = ProcessInfo.get_for_deal(na_sign, nu_sign)
                if mul_sign != "":
                    add.update({"vip":int(vi_sign),"multiple":int(mul_sign)})
                    login_info.update({"rw":reward,"add":add})
                else:
                    login_info.update({"rw": reward})
                sign_info.update({sign:login_info})
                sign = sign + 1
            else:
                info = "奖励配置不能为空!"
                msg = False
                return JsonResponse({'code': msg, 'info': info})

        series_info = {}
        series_name,series_number = dic.getlist("series_name"),dic.getlist("series_number")
        series_vip, series_multiple = dic.getlist("series_vip"),dic.getlist("series_multiple")
        series_day, month = dic.getlist("series_day"), int(dic.get("month", 0))
        n = 4
        vip_list = [series_vip[i:i + n] for i in range(0, len(series_vip), n)]
        multiple_list = [series_multiple[i:i + n] for i in range(0, len(series_multiple), n)]
        for day, nu_series, na_series, vip_info, multiple_info in zip(series_day,series_number, series_name, vip_list, multiple_list):
            series_list = {}
            day = day.encode('utf-8')
            nu_series = nu_series.encode('utf-8')
            if day != "" and nu_series != "" and u"" not in multiple_info:
                day = int(day)
                nu_series = int(nu_series)
                reward = ProcessInfo.get_for_deal(na_series, nu_series)
                add_list = []
                for vip, multiple in zip(vip_info, multiple_info):
                    vip_dict = {}
                    mul_series, vip = int(multiple), int(vip)
                    vip_dict.update({"vip": vip, "multiple": mul_series})
                    add_list.append(vip_dict)
                    series_list.update({"add": add_list})
                series_list.update({"rw": reward})
                series_info.update({day: series_list})
            else:
                info = "连续签到配置不能为空!"
                msg = False
                return JsonResponse({'code': msg, 'info': info})

        repair_list = []
        repair_start, repair_end = dic.getlist("repair_start"),dic.getlist("repair_end")

        repair_number = dic.getlist("repair_number")
        for start, end, number in zip(repair_start, repair_end, repair_number):
            level_list = []
            number = number.encode('utf-8')
            if start != "" and end != ""and number != "":
                start, end, number = int(start), int(end), int(number)
                vip_rang = range(start, end+1)
                level_list.append(vip_rang)
                level_list.append(number)
                repair_list.append(level_list)
            else:
                info = "vip补签配置不能为空!"
                msg = False
                return JsonResponse({'code': msg, 'info': info})

        config = {"date": sign_info, "continue": series_info, "complement": repair_list}
        url = '/v2/shell/sign_in_config'
        context = {"phone": phone, "pid": 2, "level": month, "conf": config}
        ret = Context.Controller.request(url, context)
        result = Context.json_loads(ret.text)
        if result.has_key("error"):
            info = "登录豪礼设置失败!"
            msg = False
        else:
            info = "登录豪礼设置成功!"
            msg = True
        return JsonResponse({'code': msg, 'info': info})


def insert_record_data(phone,Record,record_data):
    """操作记录"""
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    Record.objects.create(
        insert_time=insert_time,
        login_user=phone,
        record_data=Context.json_dumps(record_data),
    )


# ==========================白送50元==============================
@decorator
def for_free_give_money(request):
    phone = request.session.get('uid')
    give_reward = Activity_Info.give_props_data()  # 道具
    weapon_list = Activity_Info.give_weapon_data()  # 武器
    give_reward.extend(weapon_list)
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info['1000']
    if request.method == 'GET':
        url = '/v2/shell/gm/new_player_recharge'
        give_info = {"give_reward": give_reward, "give_list": Context.json_dumps(give_reward), "chanel_info": chanel_info, "chanel_list": Context.json_dumps(chanel_info)}
        context = {"pid": 1, "phone": phone}
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.text)
        if "ret" not in gift:
            reward = range(1, 8)
            give_info.update({"reward_list": reward})
            return render(request, 'activity_manage/for_free_give_money.html', give_info)
        else:
            reward_list = []
            config = gift["ret"]
            open = int(config.get("open", 0))
            channel_list = config.get("channel", [])
            product_id = config.get("productId", 0)
            day = config.get("day", 0)
            price = config.get("price", 0)
            product = config.get("product", {})
            for key, value in product.items():
                result = ProcessInfo.deal_gift_reward(value)
                reward_list.append(result)
            give_info.update({"open": open, "product_id": product_id, "day": day, "price": price, "reward_list": reward_list, "channel_list": channel_list})
            return render(request, 'activity_manage/for_free_give_money.html', give_info)
    else:
        dic = request.POST
        open = int(dic.get("open", 0))
        price = int(dic.get("price", 26))
        day = int(dic.get("open_day", 0))
        product_Id = int(dic.get("productID", 0))
        channel_list = dic.getlist("channel")

        one_name = dic.getlist("one_name")
        one_number = dic.getlist("one_number")
        two_name = dic.getlist("two_name")
        two_number = dic.getlist("two_number")

        index, product_info = 1, {}
        for o_name, o_number, t_name, t_number in zip(one_name, one_number, two_name, two_number):
            one_value = o_number.encode('utf-8')
            two_value = t_number.encode('utf-8')
            if one_value != "" and two_value != "":
                o_name = o_name.encode('utf-8')
                t_name = t_name.encode('utf-8')
                if o_name != t_name:
                    one_value = int(one_value)
                    two_value = int(two_value)
                    reward = ProcessInfo.get_for_deal(o_name, one_value)
                    new_reward = ProcessInfo.get_for_deal(t_name, two_value)
                    key = reward.keys()[0]
                    if key in new_reward:
                        reward[key].append(new_reward[key][0])
                    else:
                        reward.update(new_reward)

                    product_info.update({"{}".format(index): reward})
                    index = index + 1
                else:
                    info = "奖励配置不能重复!"
                    msg = False
                    return JsonResponse({'code': msg, 'info': info})
            else:
                info = "奖励配置不能为空!"
                msg = False
                return JsonResponse({'code': msg, 'info': info})

        config = {
            'open': open,
            'channel': channel_list,
            'productId': product_Id,
            'price': price,
            'day': day,
            'product': product_info,
        }
        url = '/v2/shell/gm/new_player_recharge'
        context = {"pid": 2, "config": config}
        context.update({"phone": phone})
        ret = Context.Controller.request(url, context)

        if ret.status_code == 200:
            info = "白送50元设置成功!"
            msg = True
        else:
            info = "白送50元设置失败!"
            msg = False
        return JsonResponse({'code': msg, 'info': info})

# ==========================7天登陆奖励==============================
@decorator
def seven_day_reward(request):
    phone = request.session.get('uid')
    give_reward = Activity_Info.give_props_data()  # 道具
    weapon_list = Activity_Info.give_weapon_data()  # 武器
    give_reward.extend(weapon_list)
    need_list = Activity_Info.login_reward_need()
    need_time = Activity_Info.need_time()
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info['1000']
    url = '/v2/shell/gm/login_reward'
    if request.method == 'GET':
        give_info = {"need_list": need_list, "need_time": need_time, "give_reward": give_reward, "chanel_info": chanel_info, "chanel_list": Context.json_dumps(chanel_info)}
        context = {"pid": 1, "phone": phone}
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.text)
        if "ret" not in gift:
            reward = [{'reward': [{'option': '', 'value': ''}, {'option': '', 'value': ''}, {'option': '', 'value': ''},{'option': '', 'value': ''}], 'need': {'type': 1, 'value': ''}, 'index': 1},
                      {'reward': [{'option': '', 'value': ''}, {'option': '', 'value': ''}, {'option': '', 'value': ''},{'option': '', 'value': ''}], 'need': {'type': 1, 'value': ''}, 'index': 2},
                      {'reward': [{'option': '', 'value': ''}, {'option': '', 'value': ''}, {'option': '', 'value': ''},{'option': '', 'value': ''}], 'need': {'type': 1, 'value': ''}, 'index': 3},
                      {'reward': [{'option': '', 'value': ''}, {'option': '', 'value': ''}, {'option': '', 'value': ''},{'option': '', 'value': ''}], 'need': {'type': 1, 'value': ''}, 'index': 4},
                      {'reward': [{'option': '', 'value': ''}, {'option': '', 'value': ''}, {'option': '', 'value': ''},{'option': '', 'value': ''}], 'need': {'type': 1, 'value': ''}, 'index': 5},
                      {'reward': [{'option': '', 'value': ''}, {'option': '', 'value': ''}, {'option': '', 'value': ''},{'option': '', 'value': ''}], 'need': {'type': 1, 'value': ''}, 'index': 6},
                      {'reward': [{'option': '', 'value': ''}, {'option': '', 'value': ''}, {'option': '', 'value': ''},{'option': '', 'value': ''}], 'need': {'type': 1, 'value': ''}, 'index': 7},
                      ]
            give_info.update({"reward_list": reward})
            return render(request, 'activity_manage/seven_day_reward.html', give_info)
        else:
            reward_list, index = [], 1
            config = gift["ret"]
            for info in config:
                day_list = {}
                reward_info = info.get("rw", {})
                need_info = info.get("need", {})
                result = ProcessInfo.deal_gift_reward(reward_info)
                if need_info:
                    day_list.update({"reward": result, "need": need_info, "index": index})
                else:
                    need_info = {"type": 1, "value": ""}
                    day_list.update({"reward": result, "need": need_info, "index": index})

                reward_list.append(day_list)
                index = index + 1
            give_info.update({"reward_list": reward_list})
        return render(request, 'activity_manage/seven_day_reward.html', give_info)
    else:
        dic = request.POST
        login_list, n = [], 4
        pro_name = dic.getlist("pro_name", [])
        pro_number = dic.getlist("pro_number", [])
        pro_time = dic.getlist("pro_time", [])
        name_list = [pro_name[i:i + n] for i in range(0, len(pro_name), n)]
        number_list = [pro_number[i:i + n] for i in range(0, len(pro_number), n)]
        time_list = [pro_time[i:i + n] for i in range(0, len(pro_time), n)]

        need_type = dic.getlist("need_type", [])
        need_value = dic.getlist("need_value", [])

        for name_info, number_info, day_info, n_type, n_value in zip(name_list, number_list, time_list, need_type, need_value):
            login_info = {}
            if len(name_info) != len(set(name_info)):
                info = "奖励配置不能重复!"
                msg = False
                return JsonResponse({'code': msg, 'info': info})
            else:
                if u"" in number_info:
                    info = "奖励配置不能为空!"
                    msg = False
                    return JsonResponse({'code': msg, 'info': info})
                else:
                    value = n_value.encode('utf-8')
                    reward = ProcessInfo.deal_auto_shot_reward(name_info, number_info, day_info)
                    if value == "":
                        login_info.update({"rw": reward})
                    else:
                        n_type, n_value = int(n_type), int(n_value)
                        login_info.update({"rw": reward, "need": {"type": n_type, "value": n_value}})
                    login_list.append(login_info)

        context = {"pid": 2, "phone": phone, "config": login_list}
        ret = Context.Controller.request(url, context)
        if ret.status_code == 200:
            info = "7天登陆奖励设置成功!"
            msg = True
        else:
            info = "7天登陆奖励设置失败!"
            msg = False
        return JsonResponse({'code': msg, 'info': info})


@decorator
def monopoly_game(request):
    """大富翁"""
    phone = request.session.get('uid')
    hot_name = Activity_Info.get_hot_type()
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info['1000']
    url = '/v2/shell/activity/get_config'
    if request.method == 'GET':
        time_info = datetime.date.today().strftime('%Y-%m-%d')
        def_info = {"hot_name": hot_name, "chanel_info": chanel_info, "chanel_list": Context.json_dumps(chanel_info)}
        context = {"pid": 1, "phone": phone}
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.text)
        if "ret" not in gift:
            def_info.update({"start": time_info, "end": time_info, "hot": "0", "name": "", "desc": "", "tips": 0, "order": 20})
        else:
            config = gift["ret"]
            if config:
                tips, name, order, hot = config["tips"], config["name"], config["order"], config["hot"]
                desc, start, end, channel_list = config["desc"], config["start"], config["end"], config["channel"]
                def_info.update({"tips": tips, "name": name, "order": order, "hot": hot, "desc": desc,
                                 "start": start, "end": end, "channel_list": channel_list})
            else:
                def_info.update({"start": time_info, "end": time_info, "hot": "0", "name": "", "desc": "", "tips": 0, "order": 20})
        return render(request, 'activity_manage/monopoly_game.html', def_info)
    else:
        dic = request.POST
        name = dic.get("activity_name").encode('utf-8')
        hot = int(dic.get("hot"))
        order = int(dic.get("order", 1))
        switch = int(dic.get("show", 0))
        desc = dic.get("desc")
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]
        open_channel = dic.getlist("activity_channel")
        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"

        if len(open_channel) != len(set(open_channel)):
            info, msg = "渠道数据重复!", False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) > 1:
            info, msg = "渠道数据错误!", False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) == 1:
            del chanel_info['0']
            chanel_list = []
            for key, value in chanel_info.items():
                channel = key.encode('utf-8')
                chanel_list.append(channel)
            open_channel = chanel_list

        open_list = []
        for chl in open_channel:
            channel = chl.encode('utf-8')
            open_list.append(channel)

        config = {
            'id': '301_2020-03-10',
            'model': 21,
            'type': 1,
            "tips": switch,
            'order': order,
            'hot': hot,
            'show': 0,
            'name': name,
            'start': start_day,
            'end': end_day,
            'channel': open_list,
            'desc': desc,
        }

        context = {"pid": 2, "config": config, "phone": phone}
        ret = Context.Controller.request(url, context)
        result = Context.json_loads(ret.text)
        if "ret" in result:
            info = "大富翁设置成功!"
            msg = True
        else:
            info = "大富翁设置失败!"
            msg = False
        return JsonResponse({'code': msg, 'info': info})


@decorator
def bag_lucky_draw(request):
    """福袋降临"""
    phone = request.session.get('uid')
    hot_name = Activity_Info.get_hot_type()
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info['1000']
    give_reward = Activity_Info.give_props_data()
    weapon_list = Activity_Info.give_weapon_data()
    give_reward.extend(weapon_list)
    url = '/v2/shell/activity/deal_activity_config'
    if request.method == 'GET':
        time_info = datetime.date.today().strftime('%Y-%m-%d')
        reward_list = range(0, 10)
        def_info = {"hot_name": hot_name, "chanel_info": chanel_info, "chanel_list": Context.json_dumps(chanel_info), "reward_list":reward_list, "give_reward":give_reward}
        context = {"pid": 1, "phone": phone}
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.text)
        if "config" not in gift:
            def_info.update({"start": time_info, "end": time_info, "hot": "0", "name": "", "desc": "", "tips": 0, "order": 20})
        else:
            config = gift["config"]
            if config:
                del def_info["reward_list"]
                props_list = []
                for key, value in config["rw_list"].items():
                    rate = int(value.get("rate", 0))
                    reward = value.get("reward", {})
                    result = ProcessInfo.deal_gift_reward(reward)[0]
                    result.update({"rate": rate})
                    props_list.append(result)

                tips, name, order, hot, limit = config["tips"], config["name"], config["order"], str(config["hot"]), config["limit"]
                desc, start, end, channel_list = config["desc"], config["start"], config["end"], config["channel"]
                def_info.update({"tips": tips, "name": name, "order": order, "hot": hot, "limit": limit, "desc": desc, "start": start, "end": end, "channel_list": channel_list, "reward_list": props_list})
            else:
                def_info.update({"start": time_info, "end": time_info, "hot": "0", "name": "", "desc": "", "tips": 0, "order": 20})
        return render(request, 'activity_manage/lucky_bag.html', def_info)
    else:
        dic = request.POST
        act_name = dic.get("act_name").encode('utf-8')
        hot = int(dic.get("act_hot"))
        limit = int(dic.get("limit"))
        order = int(dic.get("act_order", 1))
        switch = int(dic.get("show", 0))
        desc = dic.get("act_desc")
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]
        open_channel = dic.getlist("act_channel")
        reward_name = dic.getlist("reward_name")
        reward_number = dic.getlist("reward_number")
        rate_list = dic.getlist("rate")
        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"

        if len(open_channel) != len(set(open_channel)):
            info, msg = "渠道数据重复!", False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) > 1:
            info, msg = "渠道数据错误!", False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) == 1:
            del chanel_info['0']
            chanel_list = []
            for key, value in chanel_info.items():
                channel = key.encode('utf-8')
                chanel_list.append(channel)
            open_channel = chanel_list

        open_list = []
        for chl in open_channel:
            channel = chl.encode('utf-8')
            open_list.append(channel)

        reward_list, index = {}, 0
        for rate, name, number in zip(rate_list, reward_name, reward_number):
            reward_info = {}
            result = ProcessInfo.get_for_deal(name, number)
            rate = int(rate)
            reward_info.update({"rate": rate, "reward": result})
            reward_list[index] = reward_info
            index += 1

        config = {
            'id': '1322_2020-05-01',
            'model': 22,
            'type': 1,
            'tips': switch,
            'order': order,
            'hot': hot,
            'show': 0,
            'name': act_name,
            'start': start_day,
            'end': end_day,
            "channel": open_list,
            'limit': limit,
            'desc': desc,
            'rw_list': reward_list,
        }

        context = {"pid": 2, "config": config, "phone": phone}
        ret = Context.Controller.request(url, context)
        result = Context.json_loads(ret.text)
        if "ret" in result:
            info = "福袋抽奖设置成功!"
            msg = True
        else:
            info = "福袋抽奖设置失败!"
            msg = False
        return JsonResponse({'code': msg, 'info': info})


@decorator
def login_lucky_draw(request):
    """登陆奖励"""
    phone = request.session.get('uid')
    hot_name = Activity_Info.get_hot_type()
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info['1000']
    give_reward = Activity_Info.give_props_data()
    url = '/v2/shell/activity/deal_activity_config'
    if request.method == 'GET':
        time_info = datetime.date.today().strftime('%Y-%m-%d')
        reward_list = []
        rate_list = range(0, 5)
        def_info = {"hot_name": hot_name, "chanel_info": chanel_info, "chanel_list": Context.json_dumps(chanel_info), "reward_list":reward_list,"rate_list":rate_list, "give_reward":give_reward, "give_list": Context.json_dumps(give_reward)}
        context = {"pid": 3, "phone": phone}
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.text)
        print("-------------gift", gift)
        if "config" not in gift:
            def_info.update({"start": time_info, "end": time_info, "hot": "0", "name": "", "desc": "", "tips": 0, "order": 21, "props_list": []})
        else:
            config = gift["config"]
            if config:
                del def_info["reward_list"]
                props_list = []
                for key, reward in config["rw_list"].items():
                    result = ProcessInfo.deal_gift_reward(reward)[0]
                    props_list.append(result)

                rate_list = []
                for key, value in config["rate"].items():
                    rate_list.append(value)

                tips, name, order, hot = config["tips"], config["name"], config["order"], str(config["hot"])
                desc, start, end, channel_list = config["desc"], config["start"], config["end"], config["channel"]
                def_info.update({"tips": tips, "name": name, "order": order, "hot": hot, "desc": desc,
                                 "start": start, "end": end, "channel_list": channel_list,
                                 "props_list": props_list, "rate_list": rate_list})
            else:
                def_info.update({"start": time_info, "end": time_info, "hot": "0", "name": "", "desc": "", "tips": 0, "order": 21})
        return render(request, 'activity_manage/login_lucky_draw.html', def_info)
    else:
        dic = request.POST
        act_name = dic.get("act_name").encode('utf-8')
        hot = int(dic.get("act_hot"))
        order = int(dic.get("act_order", 1))
        switch = int(dic.get("show", 0))
        desc = dic.get("act_desc")
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]
        open_channel = dic.getlist("act_channel")
        reward_name = dic.getlist("reward_name")
        reward_number = dic.getlist("reward_number")
        rate_list = dic.getlist("rate")
        multiple_list = dic.getlist("multiple")
        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"

        if len(open_channel) != len(set(open_channel)):
            info, msg = "渠道数据重复!", False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) > 1:
            info, msg = "渠道数据错误!", False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) == 1:
            del chanel_info['0']
            chanel_list = []
            for key, value in chanel_info.items():
                channel = key.encode('utf-8')
                chanel_list.append(channel)
            open_channel = chanel_list

        open_list = []
        for chl in open_channel:
            channel = chl.encode('utf-8')
            open_list.append(channel)

        reward_list, index = {}, 0
        for name, number in zip(reward_name, reward_number):
            result = ProcessInfo.get_for_deal(name, number)
            reward_list[index] = result
            index += 1

        rate_info, rate_index = {}, 0
        for rate, multiple in zip(rate_list, multiple_list):
            rate_data = {}
            rate = int(rate)
            multiple = int(multiple)
            rate_data.update({"rate": rate, "reward": multiple})
            rate_info[rate_index] = rate_data
            rate_index += 1

        config = {
            'id': '1323_2020-05-01',
            'model': 23,
            'type': 1,
            'tips': switch,
            'order': order,
            'hot': hot,
            'show': 0,
            'name': act_name,
            'start': start_day,
            'end': end_day,
            "channel": open_list,
            'desc': desc,
            'rw_list': reward_list,
            'rate': rate_info,
        }
        context = {"pid": 4, "config": config, "phone": phone}
        ret = Context.Controller.request(url, context)
        result = Context.json_loads(ret.text)
        if "ret" in result:
            info = "登陆奖励设置成功!"
            msg = True
        else:
            info = "登陆奖励设置失败!"
            msg = False
        return JsonResponse({'code': msg, 'info': info})


@decorator
def special_gift_bag(request):
    """专属礼包"""
    phone = request.session.get('uid')
    gift_list = Activity_Info.gift_type()
    icon_list = Activity_Info.icon_type()
    hot_name = Activity_Info.get_hot_type()
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info['1000']
    give_reward = Activity_Info.give_props_data()
    weapon_list = Activity_Info.give_weapon_data()
    give_reward.extend(weapon_list)

    url = '/v2/shell/activity/deal_activity_config'
    if request.method == 'GET':
        time_info = datetime.date.today().strftime('%Y-%m-%d')
        reward_list = range(0, 0)
        rate_list = range(0, 5)
        def_info = {"hot_name": hot_name, "chanel_info": chanel_info, "chanel_list": Context.json_dumps(chanel_info), "reward_list":reward_list,"rate_list":rate_list, "give_reward":give_reward, "gift_list":gift_list, "props_list": Context.json_dumps(give_reward), "icon_list": icon_list, "icon_info": Context.json_dumps(icon_list)}
        context = {"pid": 5, "phone": phone}
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.text)
        if "config" not in gift:
            def_info.update({"start": time_info, "end": time_info, "hot": "0", "name": "", "desc": "", "tips": 0, "order": 22,"reward_len": len(reward_list)})
        else:
            config = gift["config"]
            if config:
                del def_info["reward_list"]
                reward_list, index = [], 1
                for key, value in config["product"].items():
                    product_id = str(key)
                    res = ProductList.objects.filter(product_id=product_id)
                    if res:
                        ProductList.objects.filter(product_id=product_id).update(
                            product_data=Context.json_dumps(value)
                        )
                    else:
                        ProductList.objects.create(
                            product_id=product_id,
                            product_data=Context.json_dumps(value)
                        )
                    prop_list = ProcessInfo.deal_gift_reward(value["content"])
                    del value["content"]
                    reward_len, prop_id = len(prop_list), 1
                    for s in range(1, 6 - reward_len):
                        add_info = {'option': 'coin', 'value': "", 'name': "", 'prop_id': prop_id}
                        prop_list.append(add_info)
                        prop_id += 1
                    value.update({"index": index, "prop_list": prop_list})
                    reward_list.append(value)
                    index += 1

                tips, name, order, hot = config["tips"], config["name"], config["order"], str(config["hot"])
                desc, start, end, channel_list = config["desc"], config["start"], config["end"], config["channel"]
                def_info.update({"tips": tips, "name": name, "order": order, "hot": hot, "desc": desc,
                                 "start": start, "end": end, "channel_list": channel_list
                                    ,"reward_len": len(config["product"]),"reward_list": reward_list})
            else:
                def_info.update({"start": time_info, "end": time_info, "hot": "0", "name": "", "desc": "", "tips": 0, "order": 22})
        return render(request, 'activity_manage/special_gift_bag.html', def_info)
    else:
        dic = request.POST
        act_name = dic.get("act_name").encode('utf-8')
        hot = int(dic.get("act_hot"))
        order = int(dic.get("act_order", 1))
        switch = int(dic.get("show", 0))
        desc = dic.get("act_desc")
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]
        open_channel = dic.getlist("act_channel")
        gift_name = dic.getlist("gift_name")
        price = dic.getlist("price")
        money = dic.getlist("money")
        gift_type = dic.getlist("gift_type")
        icon_type = dic.getlist("icon_type")
        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"

        pro_name = dic.getlist("act_reward")
        pro_number = dic.getlist("act_data")
        barrel_day = dic.getlist("barrel_day")

        if len(open_channel) != len(set(open_channel)):
            info, msg = "渠道数据重复!", False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) > 1:
            info, msg = "渠道数据错误!", False
            return JsonResponse({'code': msg, 'info': info})

        if "0" in open_channel and len(open_channel) == 1:
            del chanel_info['0']
            chanel_list = []
            for key, value in chanel_info.items():
                channel = key.encode('utf-8')
                chanel_list.append(channel)
            open_channel = chanel_list

        open_list = []
        for chl in open_channel:
            channel = chl.encode('utf-8')
            open_list.append(channel)

        index = 5
        reward_list = ProcessInfo.deal_props_reward(pro_name, pro_number, barrel_day, index)
        product_info, product_id = {}, "103201"
        for g_name, g_price, g_money, g_type, g_icon, reward in zip(gift_name, price, money, gift_type, icon_type, reward_list):
            gift_info = {}
            price, real_price, g_type, icon = int(g_price), int(g_money), int(g_type), int(g_icon)
            gift_info.update({"price": price, "name": g_name, "real_price": real_price, "type": g_type, "icon": icon, "content": reward})
            product_info["{}".format(product_id)] = gift_info
            product_id = int(product_id) + 1

        config = {
            'id': '1323_2020-05-01',
            'model': 24,
            'type': 1,
            'tips': switch,
            'order': order,
            'hot': hot,
            'show': 0,
            'name': act_name,
            'start': start_day,
            'end': end_day,
            "channel": open_list,
            'desc': desc,
            'product': product_info,
        }
        context = {"pid": 6, "config": config, "phone": phone}
        ret = Context.Controller.request(url, context)
        result = Context.json_loads(ret.text)
        if "ret" in result:
            info = "专属礼包设置成功!"
            msg = True
        else:
            info = "专属礼包设置失败!"
            msg = False
        return JsonResponse({'code': msg, 'info': info})


# ==========================充值积分周期榜==============================
@decorator
def recharge_integral(request):
    """ 充值积分周期榜"""
    hot_name = Activity_Info.get_hot_type()
    url_date, number, phone = "/activity_manage/recharge_integral/", 1, request.session.get('uid')
    if request.method == 'GET':
        one_pages = request.GET.get('page')
        if one_pages:
            config, power_rank = get_pay_rank(phone)
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
            power_rank = {"start_day": day_time, "end_day": day_time, "page": [], "number": number}
    else:
        dic = request.POST
        start_time = dic.get('start_time').encode('utf-8')[:10]
        end_time = dic.get('stop_time').encode('utf-8')[:10]

        power_rank = {"start_day": start_time, "end_day": end_time}
        keys = 'user_pay_rank:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, power_rank)

        start_day = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_day = Time.str_to_datetime(end_time, '%Y-%m-%d')

        while start_day <= end_day:
            res = PayRank.objects.filter(day_time=start_day).first()
            cur_day = Time.datetime_to_str(start_day, '%Y-%m-%d')
            if res:
                if res.day_time == res.insert_time:
                    insert_pay_rank(phone, cur_day, cur_day)
                else:
                    start_day = Time.next_days(start_day)
                    continue
            else:
                insert_pay_rank(phone, cur_day, cur_day)
            start_day = Time.next_days(start_day)

        start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')

        res_info = PayRank.objects.filter(day_time__range=[start_date, end_date]).values('json_data').order_by("-day_time")
        rank_list = []
        for info in res_info:
            rank_list.append(Context.json_loads(info.get("json_data")))
        paginator = Paginator(rank_list, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        power_rank.update({"page": page, "number": number})

    power_rank.update({"url_date": url_date, "hot_name": hot_name})
    return render(request, 'activity_manage/recharge_integral_period.html', power_rank)


def get_pay_rank(phone):
    keys = 'user_pay_rank:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day"])
    start_day, end_day = result[0], result[1]
    def_info = {"start_day": start_day, "end_day": end_day}
    start_date = Time.str_to_datetime(start_day, '%Y-%m-%d')
    end_date = Time.str_to_datetime(end_day, '%Y-%m-%d')
    res_info = PayRank.objects.filter(day_time__range=[start_date, end_date]).values('json_data').order_by("-day_time")
    sort_info = []
    for info in res_info:
        sort_info.append(Context.json_loads(info.get("json_data")))
    return sort_info, def_info


def insert_pay_rank(phone, start_day, end_day):
    url = '/v2/shell/activity/may_day_pay_rank'
    context = {"phone": phone, "start": start_day, "end": end_day}
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.text)
    if "rank" not in config:
        return 0
    else:
        rank_info = config["rank"]
        create_pay_rank(rank_info)


def create_pay_rank(rank_list):
    # PayRank.objects.all().delete()
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d')
    rank_data = []
    for m_info in rank_list:
        day_time, channel, user_id, sole_id = Time.timestamp_to_str(int(m_info["day_stamp"]), "%Y-%m-%d"), m_info["channel_id"], m_info["uid"], str(m_info["day_stamp"])
        m_info.update({"day_time": day_time})
        res = PayRank.objects.filter(sole_id=sole_id, uid=user_id).first()
        if res:
            PayRank.objects.filter(sole_id=sole_id, uid=user_id).update(
                sole_id=sole_id,
                day_time=day_time,
                insert_time=insert_time,
                uid=user_id,
                channel=channel,
                json_data=Context.json_dumps(m_info)
            )
        else:
            new_rank = PayRank(
                sole_id=sole_id,
                day_time=day_time,
                insert_time=insert_time,
                uid=user_id,
                channel=channel,
                json_data=Context.json_dumps(m_info)
            )
            rank_data.append(new_rank)

        if len(rank_data) > 1000:
            PayRank.objects.bulk_create(rank_data)
            rank_data = []

    PayRank.objects.bulk_create(rank_data)


@decorator
def pay_integral_rank(request):
    phone = request.session.get('uid')
    dic = request.POST
    pid = int(dic.get("rid"))
    if pid == 1:
        pic_id = int(request.POST.get("pic_id"))
        img_file = request.FILES.get("picture")
        if img_file:
            suffix = os.path.splitext(img_file.name)[1].lower()
            type_list = ['.jpg', '.png']  # , '.png', '.gif'
            pic_name = 'pay_rank_picture_{}'.format(pic_id)
            if os.path.splitext(img_file.name)[1].lower() in type_list:
                picture_name = "{}{}".format(pic_name, suffix)
                result = PayPictures.objects.filter(pic_id=pic_id).values("pic_name")
                if result:
                    PayPictures.objects.filter(pic_id=pic_id).update(
                        pic_name=picture_name,
                        pic_path="activity/" + picture_name
                    )
                else:
                    PayPictures.objects.create(
                        pic_name=picture_name,
                        pic_path="activity/" + picture_name,
                    )
                temp_path = settings.MEDIA_ROOT + "/activity"
                if not os.path.exists(temp_path):
                    os.makedirs(temp_path)

                file_name = settings.MEDIA_ROOT + "/activity/" + picture_name
                with open(file_name, 'wb') as pic:
                    for c in img_file.chunks():
                        pic.write(c)

                path = PayPictures.objects.filter(pic_id=pic_id).values("pic_path", "pic_name").first()
                if path:
                    new_path = path.get("pic_path")
                    pic_name = path.get("pic_name")

                    rank_picture = "http://{}/static/media/{}".format(request.get_host(), new_path).encode('utf-8')
                    version = update_picture_version(request, pic_name, rank_picture)
                    if version:
                        msg = "上传图片成功!"
                        status = True
                    else:
                        msg = "上传图片失败!"
                        status = False
                else:
                    msg = "上传图片不存在!"
                    status = False
            else:
                status = False
                msg = "上传图片格式错误!"
        else:
            msg = "未选择图片!"
            status = False
        return JsonResponse({"status": status, "msg": msg})
    elif pid == 2:
        """充值积分周期榜"""
        integral_name = dic.get("integral_name")
        integral_desc = dic.get("integral_desc")
        hot_info, channel = int(dic.get("hot_info")), dic.getlist('channel')
        order, switch, people = int(dic.get("order")), int(dic.get("open")), int(dic.get("people"))
        start_range, end_range = dic.getlist('start_range'), dic.getlist('end_range')
        award, number = dic.getlist('award'), dic.getlist('number')
        good_name = dic.getlist('goods_name')
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]

        if len(channel) < 1:
            info, msg = "请选择渠道!", False
            return JsonResponse({'status': msg, 'info': info})

        # level, new_start, new_end = [], [], []
        # for les, lend in zip(start_range, end_range):
        #     if les == u"" or lend == u"":
        #         continue
        #     else:
        #         start, end = int(les), int(lend)
        #         new_start.append(start)
        #         new_end.append(end)
        #         if len(new_start) != len(set(new_start)) or len(new_end) != len(set(new_end)):
        #             info, msg = "名次范围有重复的数据!", False
        #             return JsonResponse({'status': msg, 'info': info})
        #         if end < start:
        #             level.append(range(end, start + 1))
        #         else:
        #             level.append(range(start, end + 1))
        # flag = True
        # for k, v in enumerate(level):
        #     if k >= len(level) - 1:
        #         flag = True
        #         break
        #     if v[-1] + 1 != level[k + 1][0]:
        #         flag = False
        #         break
        #     else:
        #         continue
        # if not flag:
        #     info = "排名序号异常!"
        #     return JsonResponse({'status': flag, 'info': info})
        #
        # reward_list, pid = [], 1
        # for data, num in zip(award, number):
        #     data, num = data.encode('utf-8'), num.encode('utf-8')
        #     if num == "":
        #         continue
        #     else:
        #         reward_dict = {}
        #         if data == "0":
        #             result = PayPictures.objects.filter(pic_id=pid).values("pic_name").first()
        #             if result:
        #                 reward_dict.update({"product": {"name": good_name[pid - 1], "count": int(num), "pn": result["pic_name"]}})
        #                 reward_list.append(reward_dict)
        #             else:
        #                 info, msg = "图片未上传！", False
        #                 return JsonResponse({'status': msg, 'info': info})
        #         if data == "coin":
        #             reward_dict.update({"virtual": {"chip": int(num)}})
        #             reward_list.append(reward_dict)
        #         if data == "diamond":
        #             reward_dict.update({"virtual": {"diamond": int(num)}})
        #             reward_list.append(reward_dict)
        #     pid = pid + 1
        # if len(level) != len(reward_list):
        #     info, msg = "奖励配置数据异常!", False
        #     return JsonResponse({'status': msg, 'info': info})
        # num_list = new_start + new_end
        # people = ProcessInfo.find_max_num(num_list)

        # keys = 'pay_rank:{}:{}'.format(phone, 'set')
        # result = Context.RedisMatch.hash_mget(keys, ["level", "reward"])
        # level, reward_list = eval(result[0]), eval(result[1])

        level = [[1], [2], [3], [4, 5, 6, 7, 8, 9, 10], [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]]
        reward_list = [{u'product': {u'pid': 150010, u'name': u'\u4eac\u4e1c\u53612000\u5143x8'}, u'virtual': {u'weapon': [20012]}}, {u'product': {u'pid': 150011, u'name': u'\u4eac\u4e1c\u53612000\u5143x5'}, u'virtual': {u'props': [{u'count': 1, u'id': 20012360}]}}, {u'product': {u'pid': 150012, u'name': u'\u4eac\u4e1c\u53612000\u5143x3'}, u'virtual': {u'props': [{u'count': 1, u'id': 20012180}]}}, {u'virtual': {u'silver_coupon': 20000, u'props': [{u'count': 1, u'id': 20012090}]}}, {u'virtual': {u'silver_coupon': 20000}}]
        start_day = start_time + " 00:00:00"
        end_day = end_time + " 23:59:59"
        rank_info = {
            'id': '1201_2020-06-01',
            'model': 12,
            'type': 1,
            'tips': switch,
            'order': order,
            'hot': hot_info,
            'show': 0,
            "name": integral_name,
            "desc": integral_desc,
            'start': start_day,
            'end': end_day,
            'count': people,
            'channel': channel,
            'level': level,
            'reward': reward_list
        }

        url = '/v2/shell/activity/deal_activity_config'
        context = {"config": rank_info, "pid": 8, "phone": phone}
        ret = Context.Controller.request(url, context)
        if ret.status_code == 200:
            info = "充值积分周期榜设置成功！"
            msg = True
        else:
            info = "充值积分周期榜设置失败！"
            msg = False
        return JsonResponse({'status': msg, 'info': info})
    else:
        url = '/v2/shell/activity/deal_activity_config'
        context = {"pid": 7, "phone": phone}
        ret = Context.Controller.request(url, context)
        config = Context.json_loads(ret.content)

        start_time = datetime.date.today().strftime('%Y-%m-%d')

        if "config" not in config:
            pay_info = {"status": True, "name": "", "order": "", "hot": 0, "tips": 0, "count": 0,
                        "start": start_time, "end": start_time, "channel": [], "level": []}
            return JsonResponse(pay_info)
        else:
            rank_info = config["config"]
            if rank_info:
                tips, name, order = rank_info["tips"], rank_info["name"], rank_info["order"]
                hot, desc, start, end = str(rank_info["hot"]), rank_info["desc"], rank_info["start"], rank_info["end"]
                count = rank_info["count"]  # 上榜人数
                channel_list, level, reward = rank_info["channel"], rank_info["level"], rank_info["reward"]
                reward_list, pay_info = [], {}
                recharge_info = {"level": level, "reward": reward}
                keys = 'pay_rank:{}:{}'.format(phone, 'set')
                Context.RedisMatch.hash_mset(keys, recharge_info)

                pay_info = {'status': True, "name": name, "order": order, "hot": hot, "desc": desc, "count": count,
                            "reward": reward_list,
                            "tips": tips, "start": start, "end": end, "channel": channel_list, "level": level}
            else:
                pay_info = {"status": True, "name": "", "order": "", "hot": 0, "tips": 0, "count": 0,
                            "start": start_time, "end": start_time, "channel": [], "level": []}

            return JsonResponse(pay_info)


def update_picture_version(request, pn, pu):
    url = '/v2/game/product/update_picture_version'
    context = {"pn": pn, "pu": pu}
    context.update({"phone": request.session.get('uid')})
    ret = Context.Controller.request(url, context)
    if ret.status_code == 200:
        return True
    else:
        return False


@decorator
def look_record(request):
    url_date = "/activity_manage/all_record/"
    index, number = 1, 1
    dic = request.GET
    pid = dic.get('pid').encode('utf-8')
    one_page = dic.get('page')
    if pid == "red_record":
        result_list = RedPacketRecord.objects.all().values("insert_time","login_user","record_data").order_by("-insert_time")
    elif pid == "novice_gift_record":
        result_list = TheNoviceRecord.objects.all().values("insert_time","login_user","record_data").order_by("-insert_time")
    elif pid == "pay_double_record":
        result_list = DoubleOperation.objects.all().values("insert_time","login_user","record_data").order_by("-insert_time")
    elif pid == "login_give_record":
        result_list = LoginGiveRecord.objects.all().values("insert_time","login_user","record_data").order_by("-insert_time")
    elif pid == "saving_pot_record":
        result_list = SavingPotRecord.objects.all().values("insert_time","login_user","record_data").order_by("-insert_time")
    elif pid == "happy_shake_record":
        result_list = HappyRecord.objects.all().values("insert_time","login_user","record_data").order_by("-insert_time")
    elif pid == "activity_gift_record":
        result_list = GiftRecord.objects.all().values("insert_time","login_user","record_data").order_by("-insert_time")
    else:
        result_list = MonthCard.objects.all().values("insert_time","login_user","record_data").order_by("-insert_time")

    if one_page != None:
        one_page = int(one_page.encode('utf-8'))
        number, index = one_page, one_page

    record_list = []
    for info in result_list:
        insert_time,login_user = info.get("insert_time"),info.get("login_user")
        record_data = Context.json_loads(info.get("record_data"))
        record_data.update({"insert_time":insert_time,"login_user":login_user})
        record_list.append(record_data)

    paginator = Paginator(record_list, 30)
    page, plist = Context.paging(paginator, index)
    num_page = paginator.num_pages
    if one_page > num_page:
        number = num_page

    record_info = {'record_list': page, "number": number, "url_date": url_date}
    return render(request, 'record/{}.html'.format(pid),record_info)


@decorator
def red_packet_xls(request,rid):
    rid = int(rid)
    phone = request.session.get('uid')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=red_packet.xls'
    wb = Workbook(encoding='utf8')
    sheet = wb.add_sheet('red_packet')
    style = easyxf("""
        font:name Arial,colour_index white,bold on,height 0xA0;
        align:wrap off,vert center,horiz center;
        pattern:pattern solid,fore-colour 0x19;
        borders:left THIN,right THIN,top THIN,bottom THIN;
        """)
    if rid == 1:
        excel_red_packet(sheet,phone,style)
    else:
        red_player_xls(request,sheet,style,phone)

    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response


def excel_red_packet(sheet,phone,style):
    sheet.write(0, 0, '序号', style)
    sheet.write(0, 1, '起始日期', style)
    sheet.write(0, 2, '截止日期', style)
    sheet.write(0, 3, '红包类型', style)
    sheet.write(0, 4, '红包金额', style)
    sheet.write(0, 5, '红包数量', style)
    sheet.write(0, 6, '发放间隔', style)
    sheet.write(0, 7, '已领次数', style)
    sheet.write(0, 8, '未领次数', style)
    sheet.write(0, 9, '总领取数量', style)

    collect_info, default_time = get_red_packet(phone)
    data_row = 1

    record_data = {"status_type": "导出xls", "info": ""}
    insert_record_data(phone, RedPacketRecord, record_data)

    for info in collect_info:
        sheet.write(data_row, 0, data_row)
        red_packet_type = int(info["red_packet_type"])

        if red_packet_type == 0:
            sheet.write(data_row, 1, info["day_time"])
            sheet.write(data_row, 2, info["day_time"])
            packet_name = "普通红包"
            sheet.write(data_row, 3, packet_name)
            sheet.write(data_row, 4, info["send_gold"])
            sheet.write(data_row, 5, info["packet_sum"])
            sheet.write(data_row, 6, "--")
            sheet.write(data_row, 7, info["get_money"])
            sheet.write(data_row, 8, info["no_times"])
            sheet.write(data_row, 9, info["get_gold"])
        else:
            sheet.write(data_row, 1, info["start_date"])
            sheet.write(data_row, 2, info["end_date"])
            packet_name = "定时红包"
            sheet.write(data_row, 3, packet_name)
            sheet.write(data_row, 4, str(info["send_gold"]) + "|" + str(info["all_send_gold"]))
            sheet.write(data_row, 5, str(info["packet_sum"]) + "|" + str(info["all_packet_sum"]))
            sheet.write(data_row, 6, info["inter_time"])
            sheet.write(data_row, 7, info["get_money"])
            sheet.write(data_row, 8, info["no_times"])
            sheet.write(data_row, 9, info["get_gold"])
        data_row = data_row + 1


def red_player_xls(request,sheet,style,phone):
    sheet.write(0, 0, '序号', style)
    sheet.write(0, 1, '领取日期', style)
    sheet.write(0, 2, '玩家ID', style)
    sheet.write(0, 3, '领取数额', style)

    record_data = {"status_type": "导出领取详细xls", "info": ""}
    insert_record_data(phone, RedPacketRecord, record_data)

    packet_list = request.GET.get('Info')
    global data_row
    data_row = 1
    for packet in eval(packet_list):
        info = RedGetData.objects.filter(red_packet_id=str(packet)).values("uid", "nick", "packet", "time")
        if len(info) > 0:
            data_list = info[:]  # queryset转为list
            for index, info in enumerate(data_list):
                sheet.write(data_row, 0, index + 1)
                sheet.write(data_row, 1, Time.datetime_to_str(info["time"]))
                sheet.write(data_row, 2, info["uid"])
                sheet.write(data_row, 3, info["packet"])
                data_row = data_row + 1
            data_row = data_row + 1
        else:
            continue


@decorator
def export_all_xls(request):
    phone = request.session.get('uid')
    dic = request.GET
    rid = int(dic.get('rid'))
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename={}.xls'.format(rid)
    wb = Workbook(encoding='utf8')
    sheet = wb.add_sheet("{}".format(rid))
    style = easyxf("""
            font:name Arial,colour_index white,bold on,height 0xA0;
            align:wrap off,vert center,horiz center;
            pattern:pattern solid,fore-colour 0x19;
            borders:left THIN,right THIN,top THIN,bottom THIN;
            """)

    if rid == "happy_shake":
        happy_shake_xls(phone, sheet, style)
    elif rid == "pay_rank":
        pay_rank_xls(sheet,style)
    elif rid == "may_rank":
        may_rank_xls(phone,sheet,style)
    elif rid == "egg":
        version = dic.get('version')
        egg_xls(sheet,style,version)
    else:
        dragon_boat_xls(phone,sheet,style)

    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response


def happy_shake_xls(phone,sheet,style):
    sheet.write(0, 0, '序号', style)
    sheet.write(0, 1, '起始日期', style)
    sheet.write(0, 2, '截止日期', style)
    sheet.write(0, 3, '触发日期', style)
    sheet.write(0, 4, '触发方式', style)
    sheet.write(0, 5, '触发额度', style)
    sheet.write(0, 6, '返利总金额', style)
    sheet.write(0, 7, '发放数量', style)

    happy_info, default_time = get_happy_info(phone)
    data_row = 1
    for info in happy_info:
        sheet.write(data_row, 0, data_row)
        sheet.write(data_row, 1, info["start"])
        sheet.write(data_row, 2, info["end"])
        sheet.write(data_row, 3, info["trig_time"])
        if info["way"] == 1:
            way = "循环"
        else:
            way = "手动"
        sheet.write(data_row, 4, str(way))
        sheet.write(data_row, 5, info["money"])
        sheet.write(data_row, 6, info["all_rebate"])
        sheet.write(data_row, 7, info["get_number"])
        data_row = data_row + 1


def pay_rank_xls(sheet,style):
    sheet.write(0, 0, '序号', style)
    sheet.write(0, 1, '渠道', style)
    sheet.write(0, 2, '起始日期', style)
    sheet.write(0, 3, '截止日期', style)
    sheet.write(0, 4, '详情', style)

    rank_info, default_time = get_recharge_data()
    data_row = 1
    for info in rank_info:
        sheet.write(data_row, 0, data_row)
        sheet.write(data_row, 1, info["channel"])
        sheet.write(data_row, 2, info["start_stamp"])
        sheet.write(data_row, 3, info["end_stamp"])

        user_info = ""
        for user in info["play_info"]:
            cid = user.get("cid", 0)
            rank = user.get("rank", 0)
            ranks = rank + 1
            uid = user.get("id", 0)
            phone = user.get("phone", 0)
            nick = user.get("nick", 0)
            vip = user.get("vip", 0)
            point = user.get("point", 0)
            integral = user.get("integral", 0)
            if user["reward"].has_key("name"):
                reward = user["reward"]["name"]
            elif user["reward"].has_key("c"):
                reward = "{}鸟蛋".format(user["reward"]["c"])
            elif user["reward"].has_key("d"):
                reward = "{}钻石".format(user["reward"]["d"])

            user_str = "渠道:" + str(cid) + "名次:" + str(ranks) + "玩家ID:" + str(uid) + "手机号:" + str(phone) + "玩家昵称:" + str(
                nick) + "VIP等级:" + str(vip) + "充值金额:" + str(point) + "充值积分:" + str(integral) + "奖励:" + reward + '\n'
            user_info = user_info + user_str
        user_info = user_info + '\n'
        sheet.write(data_row, 4, user_info)
        data_row = data_row + 1


def may_rank_xls(phone,sheet,style):
    sheet.write(0, 0, '序号', style)
    sheet.write(0, 1, '渠道', style)
    sheet.write(0, 2, '起始日期', style)
    sheet.write(0, 3, '截止日期', style)
    sheet.write(0, 4, '详情', style)

    rank_info, default_time = get_may_day_info(phone)
    data_row = 1
    for info in rank_info:
        sheet.write(data_row, 0, data_row)
        sheet.write(data_row, 1, info["channel"])
        sheet.write(data_row, 2, info["start_stamp"])
        sheet.write(data_row, 3, info["end_stamp"])

        user_info = ""
        for user in info["play_info"]:
            cid = user.get("cid", 0)
            rank = user.get("rank", 0)
            ranks = rank + 1
            uid = user.get("id", 0)
            phone = user.get("phone", 0)
            nick = user.get("nick", 0)
            vip = user.get("vip", 0)
            point = user.get("point", 0)
            pay_point = user.get("pay_point", 0)
            shot_point = user.get("shot_point", 0)
            use_point = user.get("use_point", 0)
            surplus_point = user.get("surplus_point", 0)

            user_str = "名次:" + str(ranks) + "渠道:" + str(cid) + "玩家ID:" + str(uid) + "手机号:" + str(phone) + "玩家昵称:" + str(
                nick) + "VIP等级:" + str(vip) + "活动总积分:" + str(point) + "充值积分:" + str(pay_point) + "洗码量积分:" + str(
                shot_point) + "积分总消耗:" + str(use_point) + "积分总剩余:" + str(surplus_point) + '\n'
            user_info = user_info + user_str
        user_info = user_info + '\n'
        sheet.write(data_row, 4, user_info)
        data_row = data_row + 1


def egg_xls(sheet,style,version):
    sheet.write(0, 0, '序号', style)
    sheet.write(0, 1, '玩家ID', style)
    sheet.write(0, 2, '玩家昵称', style)
    sheet.write(0, 3, 'vip', style)
    sheet.write(0, 4, '手机号', style)
    sheet.write(0, 5, '获取奖励额度', style)

    data_row = 1
    res_info = EggQueryInfo.objects.filter(aid=version).values("json_data")
    for data in res_info:
        info = Context.json_loads(data.get("json_data"))
        sheet.write(data_row, 0, data_row)
        sheet.write(data_row, 1, info["id"])
        sheet.write(data_row, 2, info["nick"])
        sheet.write(data_row, 3, info["vip"])
        sheet.write(data_row, 4, info["phone"])
        chip = str(int(info["chip"]) / 5000) + "元"
        sheet.write(data_row, 5, chip)
        data_row = data_row + 1


def dragon_boat_xls(phone,sheet,style):
    sheet.write(0, 0, '渠道', style)
    sheet.write(0, 1, '玩家ID', style)
    sheet.write(0, 2, '手机号', style)
    sheet.write(0, 3, '玩家昵称', style)
    sheet.write(0, 4, '活动起止时间', style)
    sheet.write(0, 5, '获得奖励', style)

    data_row = 1
    conf, compute_info = get_dragon_boat_data(phone)
    for info in conf:
        sheet.write(data_row, 0, info["c"])
        sheet.write(data_row, 1, info["uid"])
        sheet.write(data_row, 2, info["p"])
        sheet.write(data_row, 3, info["nick"])
        sheet.write(data_row, 4, str(info["start_day"]) + "~" + str(info["end_day"]))
        if isinstance(info["reward"], unicode):
            reward_info = eval(info["reward"])
        else:
            reward_info = info["reward"]
        reward = BirdProps.get_reward_str(reward_info)
        sheet.write(data_row, 5, reward)
        data_row = data_row + 1