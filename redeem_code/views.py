# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render_to_response, render, redirect
from util.context import Context
from util.tool import Time
import time
from util.gamedate import *
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from datetime import datetime, date, timedelta
from login_manage.models import LoginInfo,ChannelList
from login_manage.views import decorator
from .models import *
import datetime
import json
from xlwt import *
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from util.process import ProcessInfo
from hashlib import sha1


@decorator
def redeem_overview(request):
    url_date, number, phone = "/redeem_code/redeem_overview/", 1, request.session.get('uid')
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info["1000"]
    money_list = redeem_Info.get_redeem_money()
    give_reward = Activity_Info.give_props_data()  # 道具
    weapon_list = Activity_Info.give_weapon_data()  # 武器
    give_reward.extend(weapon_list)
    day_time = datetime.date.today().strftime('%Y-%m-%d')
    create_time = Time.current_time('%Y-%m-%d %H:%M:%S')
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page:
            conf, code_info = get_redeem_overview(phone)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            code_info.update({"number": number, "page": page})
        else:
            code_info = {"channel": "0", "start_day": day_time, "end_day": day_time, "number": number, "create_time": create_time,"gift_name": ""}
    else:
        dic = request.POST
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]
        channel = dic.get('channel').encode('utf-8')
        gift_name = dic.get('gift_name').encode('utf-8').strip()

        code_info = {"channel": channel, "gift_name": gift_name, "start_day": start_time, "end_day": end_time}
        keys = 'redeem_total:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, code_info)

        get_redeem_total(phone, start_time, end_time)
        start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')
        if channel == "0":
            if gift_name == "":
                res_info = General.objects.filter(day_time__range=[start_date, end_date]).values("cdkey_name","channel","version","pool","count","used","unused","reward","create_time","lose_time","amount")
            else:
                res_info = General.objects.filter(day_time__range=[start_date, end_date], cdkey_name=gift_name).values("cdkey_name","channel","version","pool","count","used","unused","reward","create_time","lose_time","amount")
        else:
            if gift_name == "":
                res_info = General.objects.filter(day_time__range=[start_date, end_date] ,channel=channel).values("cdkey_name","channel","version","pool","count","used","unused","reward","create_time","lose_time","amount")
            else:
                res_info = General.objects.filter(day_time__range=[start_date, end_date] ,channel=channel, cdkey_name=gift_name).values("cdkey_name","channel","version","pool","count","used","unused","reward","create_time","lose_time","amount")

        redeem_list, code_id = [], 1
        for redeem in res_info:
            redeem.update({"code_id":code_id})
            redeem_list.append(redeem)
            code_id +=1
        paginator = Paginator(redeem_list, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        code_info.update({"page": page, "number": number})

    code_info.update({"create_time": create_time, "money_list": money_list,"give_reward": give_reward,"day_time": day_time,"chanel_info": chanel_info, "url_date": url_date,"give_list":Context.json_dumps(give_reward)})
    return render(request, 'redeem_code/redeem_generate.html',code_info)


def get_redeem_total(phone, start_time, end_time):
    url = "/v2/shell/gm/deal_redeem_code"
    context = {"pid": 3, "phone": phone, "start": start_time, "end": end_time}
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.content)
    if not config.has_key("conf"):
        return 0
    else:
        code_list = []
        for info in config["conf"]:
            code_info = {}
            lose_time = Time.timestamp_to_str(info["end_time"])
            creat_time = Time.timestamp_to_str(info["creat_time"])
            used, unused = info["cdkey_use"], int(info["count"]) - int(info["cdkey_use"])
            code_info.update({"lose_time": lose_time, "create_time": creat_time, "cdkey_name": info["describe"], "version": info["version"]})
            code_info.update({"channel": info["channel"], "used": used,"unused": unused, "count": info["count"], "reward": info["reward"], "pool": info["reward"].get("pool", 0)})
            if not info["reward"].has_key("pool"):
                amount = 0
            else:
                amount = int(info["reward"]["pool"]) * int(info["cdkey_use"])
            code_info.update({"amount": amount})
            code_list.append(code_info)

        create_redeem_code(code_list)


def get_redeem_overview(phone):
    keys = 'redeem_total:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day", "channel", "gift_name"])
    start_day, end_day, channel, cdkey_name = result[0], result[1], result[2], result[3]
    def_info = {"start_day": start_day, "end_day": end_day, "channel": channel, "gift_name": cdkey_name}
    start_date = Time.str_to_datetime(start_day, '%Y-%m-%d')
    end_date = Time.str_to_datetime(end_day, '%Y-%m-%d')

    if channel == "0":
        if cdkey_name == "":
            res_info = General.objects.filter(day_time__range=[start_date, end_date]).values("cdkey_name", "channel","version", "pool", "count","used", "unused", "reward","create_time", "lose_time","amount")
        else:
            res_info = General.objects.filter(day_time__range=[start_date, end_date], cdkey_name=cdkey_name).values("cdkey_name", "channel", "version", "pool", "count", "used", "unused", "reward", "create_time","lose_time", "amount")
    else:
        if cdkey_name == "":
            res_info = General.objects.filter(day_time__range=[start_date, end_date], channel=channel).values("cdkey_name", "channel", "version", "pool", "count", "used", "unused", "reward", "create_time","lose_time", "amount")
        else:
            res_info = General.objects.filter(day_time__range=[start_date, end_date], channel=channel,cdkey_name=cdkey_name).values("cdkey_name", "channel", "version", "pool","count", "used", "unused", "reward","create_time", "lose_time", "amount")

    redeem_list, code_id = [], 1
    for redeem in res_info:
        redeem.update({"code_id": code_id})
        redeem_list.append(redeem)
        code_id += 1
    return redeem_list, def_info


def create_redeem_code(code_list):
    # General.objects.all().delete()
    code_data = []
    for m_info in code_list:
        day_time = m_info["create_time"][:10]
        cdkey_name, channel, version, pool, count = m_info["cdkey_name"], m_info["channel"], m_info["version"], m_info["pool"], m_info["count"]
        used, unused, reward, create_time, lose_time,amount = m_info["used"], m_info["unused"], m_info["reward"], m_info["create_time"], m_info["lose_time"], m_info["amount"]
        res = General.objects.filter(day_time=day_time, version=version).first()
        if res:
            General.objects.filter(day_time=day_time, version=version).update(
                day_time=day_time,
                cdkey_name=cdkey_name,
                channel=channel,
                version=version,
                pool=pool,
                count=count,
                used=used,
                unused=unused,
                reward=Context.json_dumps(reward),
                create_time=create_time,
                lose_time=lose_time,
                amount=amount,
            )
        else:
            new_order = General(
                day_time=day_time,
                cdkey_name=cdkey_name,
                channel=channel,
                version=version,
                pool=pool,
                count=count,
                used=used,
                unused=unused,
                reward=Context.json_dumps(reward),
                create_time=create_time,
                lose_time=lose_time,
                amount=amount,
            )
            code_data.append(new_order)

        if len(code_data) > 1000:
            General.objects.bulk_create(code_data)
            code_data = []

    General.objects.bulk_create(code_data)


@decorator
def deal_redeem(request):
    """生成兑换码"""
    create_code = {}
    phone = request.session.get('uid')
    dic = request.POST
    pid = int(dic.get('pid'))
    if pid == 1: # 生成兑换码
        describe = dic.get('classify_name')
        redeem_price = dic.get('redeem_price').encode('utf-8')
        count = dic.get('count')
        channel = dic.get('channel').encode('utf-8')
        start_time = dic.get('start_time').encode('utf-8')
        times = Time.str_to_timestamp(start_time)
        name_list = dic.getlist("reward_name")
        number_list = dic.getlist("reward_number")
        barrel_day = dic.getlist("barrel_day")

        reward = ProcessInfo.deal_props_reward(name_list, number_list, barrel_day)
        if isinstance(reward, list):
            reward_info = reward[0]
        else:
            reward_info = reward

        if redeem_price != "0":
            reward_info.update({"pool": int(redeem_price)})
        url = '/v2/shell/gm/deal_redeem_code'
        context = {"pid": pid, "phone": phone, "reward": reward_info, "count": count, "time": times, "describe": describe, "channel": channel}
        ret = Context.Controller.request(url, context)
        if ret.status_code == 200:
            pool = redeem_price.encode('utf-8')
            if pool == 0:
                pool = "免费码"
            else:
                pool = "{}元兑换码".format(pool)

            record_data = {"status_type": "{}(生成)".format(describe), "info": "{}*{}".format(pool,count)}
            insert_record_data(phone, Record, record_data)
            msg = "兑换码生成成功！"
            status = True
        else:
            msg = "兑换码生成失败！"
            status = False
        create_code.update({"status": status, "msg": msg})
    else: # 兑换码失效
        version = dic.get('version')
        url = '/v1/shell/alter_cdkey'
        context = {"pid": pid, "phone": phone, "version": version}
        ret = Context.Controller.request(url, context)
        if ret.status_code == 200:
            result = General.objects.get(version=version)
            General.objects.filter(version=version).update(end_time=result.create_time)

            record_data = {"status_type": "标识ID{}(失效)".format(version), "info": ""}
            insert_record_data(phone, Record, record_data)
            status, msg = True, "兑换码生效!"
        else:
            status, msg = False, "兑换码未生效!"
        create_code.update({"status": status, "msg": msg})
    return JsonResponse(create_code)


def derived_redeem_info(request):
    """兑换码总览--导出xls"""
    record_info = []
    phone = request.session.get('uid')
    ver = request.GET.get('version')
    version = ver.encode('utf-8').replace('.', '')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=redeem.xls'
    wb = Workbook(encoding='utf8')
    sheet = wb.add_sheet('redeem-sheet')
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
    sheet.write(0, 1, '兑换码ID', style)
    sheet.write(0, 2, '分类名称', style)
    sheet.write(0, 3, '生成人', style)
    sheet.write(0, 4, '使用情况', style)
    sheet.write(0, 5, '玩家ID', style)
    sheet.write(0, 6, '渠道ID', style)
    sheet.write(0, 7, '奖励类容', style)
    sheet.write(0, 8, '生成日期', style)
    sheet.write(0, 9, '有效期至', style)
    sheet.write(0, 10, '使用时间', style)

    url = '/v2/shell/gm/deal_redeem_code'
    context = {"phone":phone,"version": version,"pid":5}
    ret = Context.Controller.request(url, context)
    info_code = Context.json_loads(ret.content)
    if not info_code.has_key(u"cdk") or not info_code.has_key(u"info"):
        return 0
    else:
        code_conf = Context.json_loads(info_code["info"])
        prop_info = convert_reward(code_conf["reward"])
        reward = ",".join(prop_info["reward_info"])
        end_time, create_time = Time.timestamp_to_str(code_conf["end_time"]), Time.timestamp_to_str(code_conf["creat_time"])
        channel, people, describe = code_conf["channel"], code_conf["people"], code_conf["describe"]
        for key, values in info_code["cdk"].items():
            conf_code = {}
            value = Context.json_loads(values)
            conf_code.update({"key":key,"code": value["code"],"ex_time": value.get("ex_time", 0),"reward":reward,"end_time": end_time,"creat_time": create_time})
            if conf_code["ex_time"] != 0:
                use = 1
            else:
                use = 2
            conf_code.update({"channel": channel,"uid": value.get("uid", 0),"use": use,"people": people,"describe": describe})
            record_info.append(conf_code)

        record_data = {"status_type": "{}(导出xls)".format(describe), "info": ""}
        insert_record_data(phone, Record, record_data)

        data_row = 1
        for info in record_info:
            sheet.write(data_row, 0, data_row)
            sheet.write(data_row, 1, info["key"])
            sheet.write(data_row, 2, info["describe"])
            sheet.write(data_row, 3, info["people"])
            if int(info["use"]) == 1:
                used = "√"
            else:
                used = "x"
            sheet.write(data_row, 4, used)
            sheet.write(data_row, 5, info["uid"])
            sheet.write(data_row, 6, info["channel"])
            sheet.write(data_row, 7, info["reward"])
            sheet.write(data_row, 8, info["creat_time"])
            sheet.write(data_row, 9, info["end_time"])
            sheet.write(data_row, 10, info["ex_time"])
            data_row = data_row + 1

        # 写出到IO
        output = BytesIO()
        wb.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response


@decorator
def redeem_query(request):
    """兑换码查询"""
    url_date, number, phone = "/redeem_code/redeem_query/", 1, request.session.get('uid')
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info["1000"]
    employ_list = redeem_Info.get_employ_status()
    give_reward = Activity_Info.give_props_data()  # 道具
    weapon_list = Activity_Info.give_weapon_data()  # 武器
    give_reward.extend(weapon_list)
    day_time = datetime.date.today().strftime('%Y-%m-%d')
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page:
            conf, code_info = get_redeem_query(phone)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            code_info.update({"number": number, "page": page})
        else:
            code_info = {"channel": "0", "start_day": day_time, "end_day": day_time, "number": number,"day_time": day_time,"used": "0", "userId": ""}
    else:
        dic = request.POST
        start_time = dic.get('start_time')[:10]
        end_time = dic.get('stop_time')[:10]
        channel = dic.get('channel').encode('utf-8')
        used = dic.get('used').encode('utf-8')
        userId = dic.get('userId').encode('utf-8').strip()
        gift_name = dic.get('gift_name').encode('utf-8').strip()

        code_info = {"channel": channel, "employ": used, "start_day": start_time, "end_day": end_time, "userId": userId, "gift_name": gift_name}
        keys = 'redeem_query:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, code_info)
        get_query_redeem_code(phone, start_time, end_time)
        sorted_info = get_query_redeem_info(code_info)

        paginator = Paginator(sorted_info, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        code_info.update({"page": page, "number": number})

    code_info.update({"chanel_info": chanel_info,"employ_list":employ_list, "url_date":url_date})
    return render(request, 'redeem_code/redeem_query.html', code_info)


def get_query_redeem_code(phone, start_time, end_time):
    url = "/v2/shell/gm/deal_redeem_code"
    start_stamp = Time.str_to_timestamp(start_time + " 00:00:00")
    end_stamp = Time.str_to_timestamp(end_time + " 23:59:59")
    context = {"pid": 4, "phone": phone, "start": start_stamp, "end": end_stamp}
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.content)
    if not config.has_key("cdkey"):
        return 0
    else:
        code_list = []
        for coded in config["cdkey"]:
            code_info = {}
            info = coded["info"]
            end_time, creat_time = Time.timestamp_to_str(coded["end_time"]), Time.timestamp_to_str(coded["creat_time"])
            ex_time, uid, code_key = info.get("ex_time", 0), info.get("uid", 0), info.get("key", 0)
            if ex_time != 0 and uid != 0:
                use = 1
            else:
                ex_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                use = 2
            code_info.update({"lose_time": end_time, "create_time": creat_time, "describe": coded["describe"], "ex_time": ex_time,"uid": uid})
            code_info.update({"reward": coded["reward"], "cdkey_id": code_key, "used": use, "people": coded["people"],"channel": coded["channel"]})
            code_list.append(code_info)

        insert_query_info(code_list)


def insert_query_info(redeem_list):
    """兑换码查询"""
    # Query.objects.all().delete()
    code_data = []
    for m_info in redeem_list:
        cdkey_id, cdkey_name, channel, people, used, uid = m_info["cdkey_id"], m_info["describe"], m_info["channel"], m_info["people"], m_info["used"], m_info["uid"]
        reward, create_time, lose_time, employ_time = m_info["reward"], m_info["create_time"], m_info["lose_time"], m_info["ex_time"]
        res = Query.objects.filter(cdkey_id=cdkey_id, cdkey_name=cdkey_name).first()
        if res:
            Query.objects.filter(cdkey_id=cdkey_id, cdkey_name=cdkey_name).update(
                cdkey_id=cdkey_id,
                cdkey_name=cdkey_name,
                channel=channel,
                people=people,
                used=used,
                uid=uid,
                reward=Context.json_dumps(reward),
                create_time=create_time,
                lose_time=lose_time,
                employ_time=employ_time,
            )
        else:
            new_info = Query(
                cdkey_id=cdkey_id,
                cdkey_name=cdkey_name,
                channel=channel,
                people=people,
                used=used,
                uid=uid,
                reward=Context.json_dumps(reward),
                create_time=create_time,
                lose_time=lose_time,
                employ_time=employ_time,
            )
            code_data.append(new_info)

        if len(code_data) > 1000:
            Query.objects.bulk_create(code_data)
            code_data = []

    Query.objects.bulk_create(code_data)


def get_query_redeem_info(code_info):
    start_time, end_time, channel, used, userId, gift_name = code_info["start_day"], code_info["end_day"],code_info["channel"], code_info["employ"], code_info["userId"], code_info["gift_name"]
    start_date = Time.str_to_datetime(start_time + " 00:00:00")
    end_date = Time.str_to_datetime(end_time + " 23:59:59")

    res_info = []
    if channel == '0' and used == '0' and userId == '' and gift_name == '':
        res_info = Query.objects.filter(create_time__range=[start_date, end_date]).values("cdkey_id","cdkey_name", "channel", "people", "used", "uid", "reward","create_time", "lose_time","employ_time")

    if channel == '0' and used != '0' and userId == '' and gift_name != '':
        used = int(used)
        res_info = Query.objects.filter(create_time__range=[start_date, end_date], used=used, cdkey_name=gift_name).values("cdkey_id","cdkey_name", "channel", "people", "used", "uid", "reward","create_time", "lose_time","employ_time")

    if channel == '0' and used == '0' and userId == '' and gift_name != '':
        res_info = Query.objects.filter(create_time__range=[start_date, end_date],cdkey_name=gift_name).values("cdkey_id", "cdkey_name", "channel","people", "used", "uid", "reward","create_time", "lose_time","employ_time")

    if channel == '0' and used == '0' and userId != '' and gift_name == '':
        userId = int(userId)
        res_info = Query.objects.filter(create_time__range=[start_date, end_date],uid=userId).values("cdkey_id", "cdkey_name", "channel", "people","used", "uid", "reward", "create_time","lose_time", "employ_time")

    if channel == '0' and used != '0' and userId != '' and gift_name != '':
        used, userId = int(userId), int(userId)
        res_info = Query.objects.filter(create_time__range=[start_date, end_date],used=used, uid=userId, cdkey_name=gift_name).values("cdkey_id", "cdkey_name", "channel", "people", "used","uid", "reward", "create_time", "lose_time","employ_time")

    if channel == '0' and used == '0' and userId != '' and gift_name != '':
        userId = int(userId)
        res_info = Query.objects.filter(create_time__range=[start_date, end_date], uid=userId, cdkey_name=gift_name).values("cdkey_id", "cdkey_name","channel", "people","used", "uid", "reward","create_time","lose_time","employ_time")

    if channel == '0' and used != '0' and userId == '' and gift_name == '':
        userId = int(userId)
        res_info = Query.objects.filter(create_time__range=[start_date, end_date], uid=userId, cdkey_name=gift_name).values("cdkey_id", "cdkey_name","channel", "people","used", "uid", "reward","create_time","lose_time","employ_time")

    if channel != '0' and used == '0' and userId != '' and gift_name != '':
        userId = int(userId)
        res_info = Query.objects.filter(create_time__range=[start_date, end_date],channel=channel, uid=userId, cdkey_name=gift_name).values("cdkey_id", "cdkey_name","channel", "people","used", "uid", "reward","create_time","lose_time","employ_time")

    if channel != '0' and used == '0' and userId == '' and gift_name != '':
        res_info = Query.objects.filter(create_time__range=[start_date, end_date],channel=channel, cdkey_name=gift_name).values("cdkey_id","cdkey_name","channel", "people","used", "uid","reward","create_time","lose_time","employ_time")

    if channel != '0' and used != '0' and userId == '' and gift_name == '':
        used = int(used)
        res_info = Query.objects.filter(create_time__range=[start_date, end_date], channel=channel, used=used).values("cdkey_id","cdkey_name","channel", "people","used", "uid","reward","create_time","lose_time","employ_time")

    if channel != '0' and used != '0' and userId != '' and gift_name == '':
        res_info = Query.objects.filter(create_time__range=[start_date, end_date],channel=channel,uid=userId, used=used).values("cdkey_id","cdkey_name","channel", "people","used", "uid","reward","create_time","lose_time","employ_time")

    if channel != '0' and used != '0' and userId != '' and gift_name != '':
        used, userId = int(userId), int(userId)
        res_info = Query.objects.filter(create_time__range=[start_date, end_date],channel=channel, uid=userId, used=used, cdkey_name=gift_name).values("cdkey_id","cdkey_name","channel", "people","used", "uid","reward","create_time","lose_time","employ_time")

    if channel != '0' and used == '0' and userId == '' and gift_name == u'':
        res_info = Query.objects.filter(create_time__range=[start_date, end_date],channel=channel).values("cdkey_id","cdkey_name","channel", "people","used", "uid","reward","create_time","lose_time","employ_time")

    redeem_list, code_id = [], 1
    for redeem in res_info:
        redeem.update({"code_id": code_id,"reward":Context.json_loads(redeem.get("reward",{}))})
        redeem_list.append(redeem)
        code_id += 1
    return redeem_list


def get_redeem_query(phone):
    keys = 'redeem_query:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day", "channel", "userId", "employ", "gift_name"])
    start_day, end_day, channel, userId, used, gift_name = result[0], result[1], result[2], result[3], result[4], result[5]
    def_info = {"start_day": start_day, "end_day": end_day, "channel": channel, "employ": used, "userId": userId, "gift_name": gift_name}
    sorted_info = get_query_redeem_info(def_info)
    return sorted_info, def_info


def derived_query_info(request):
    """查询数据--导出xls"""
    phone = request.session.get('uid')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=redeem_query.xls'
    wb = Workbook(encoding='utf8')
    sheet = wb.add_sheet('redeem-sheet')
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
    sheet.write(0, 1, '兑换码ID', style)
    sheet.write(0, 2, '分类名称', style)
    sheet.write(0, 3, '生成人', style)
    sheet.write(0, 4, '使用情况', style)
    sheet.write(0, 5, '玩家ID', style)
    sheet.write(0, 6, '渠道ID', style)
    sheet.write(0, 7, '奖励类容', style)
    sheet.write(0, 8, '生成日期', style)
    sheet.write(0, 9, '有效期至', style)
    sheet.write(0, 10, '使用时间', style)

    redeem_info, _ = get_redeem_query(phone)

    record_data = {"status_type": "(查询数据导出xls)", "info": ""}
    insert_record_data(phone, Record, record_data)

    data_row = 1
    for info in redeem_info:
        sheet.write(data_row, 0, info["code_id"])
        sheet.write(data_row, 1, info["cdkey_id"])
        sheet.write(data_row, 2, info["cdkey_name"])
        sheet.write(data_row, 3, info["people"])
        if int(info["used"]) == 1:
            used = "√"
            employ_time = Time.datetime_to_str(info["employ_time"])
        else:
            used = "x"
            employ_time = "0"

        create_time = Time.datetime_to_str(info["create_time"])
        lose_time = Time.datetime_to_str(info["lose_time"])
        sheet.write(data_row, 4, used)
        sheet.write(data_row, 5, info["uid"])
        sheet.write(data_row, 6, info["channel"])
        prop_info = convert_reward(info["reward"])
        reward = ",".join(prop_info["reward_info"])
        sheet.write(data_row, 7, reward)
        sheet.write(data_row, 8, create_time)
        sheet.write(data_row, 9, lose_time)
        sheet.write(data_row, 10, employ_time)
        data_row = data_row + 1

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response


def all_record(request):
    url_date = "/redeem_code/all_record/"
    index, number = 1, 1
    dic = request.GET
    pid = dic.get('pid').encode('utf-8')
    one_page = dic.get('page')
    if pid == "redeem_overview":
        result_list = Record.objects.all().values("insert_time", "login_user", "record_data").order_by("-insert_time")
    else:
        result_list = Record.objects.all().values("insert_time", "login_user", "record_data").order_by("-insert_time")

    if one_page != None:
        one_page = int(one_page.encode('utf-8'))
        number, index = one_page, one_page

    record_list = []
    for info in result_list:
        insert_time, login_user = info.get("insert_time"), info.get("login_user")
        record_data = Context.json_loads(info.get("record_data"))
        record_data.update({"insert_time": insert_time, "login_user": login_user})
        record_list.append(record_data)

    paginator = Paginator(record_list, 30)
    page, plist = Context.paging(paginator, index)
    num_page = paginator.num_pages
    if one_page > num_page:
        number = num_page

    record_info = {'record_list': page, "number": number, "url_date": url_date}
    return render(request, 'record/{}.html'.format(pid), record_info)


def insert_record_data(phone, Record, record_data):
    """操作记录"""
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    Record.objects.create(
        insert_time=insert_time,
        login_user=phone,
        record_data=Context.json_dumps(record_data),
    )


def convert_reward(rewards_info):
    reward_info = []
    code_info ={}
    if 'coin' in rewards_info:
        result = "金币"
        value = rewards_info['coin']
        reward = "{}:{}".format(result, value)
        reward_info.append(reward)
    if 'diamond' in rewards_info:
        result = "钻石"
        value = rewards_info['diamond']
        reward = "{}:{}".format(result, value)
        reward_info.append(reward)
    if 'silver_coupon' in rewards_info:
        result = "话费劵"
        value = rewards_info['silver_coupon']
        reward = "{}:{}".format(result, value)
        reward_info.append(reward)
    if 'power' in rewards_info:
        result = "鸟蛋"
        value = rewards_info['power']
        reward = "{}:{}".format(result, value)
        reward_info.append(reward)
    if 'props' in rewards_info:
        for pro in rewards_info['props']:
            number = int(pro["id"])
            if number < 20001000:
                if pro["id"] == 202:
                    result = "冰冻"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 203:
                    result = "狂暴"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 205:
                    result = "召唤"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 211:
                    result = "青铜宝箱"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 212:
                    result = "白银宝箱"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 213:
                    result = "黄金宝箱"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 214:
                    result = "至尊宝箱"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 215:
                    result = "绿灵石"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 216:
                    result = "蓝魔石"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 217:
                    result = "紫晶石"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 218:
                    result = "血精石"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 219:
                    result = "强化石"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 220:
                    result = "创房卡"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 301:
                    result = "灵魂宝石"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1303:
                    result = "风暴结晶"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1304:
                    result = "逐风者的碎片"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1302:
                    result = "大福袋"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1305:
                    result = "礼盒"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1311:
                    result = "神秘礼盒"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1611:
                    result = "许愿卡"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1328:
                    result = "白银钥匙"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1329:
                    result = "黄金钥匙"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1330:
                    result = "白金钥匙"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1331:
                    result = "白银宝箱"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1332:
                    result = "黄金宝箱"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1333:
                    result = "白金宝箱"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1207:
                    result = "风暴狮角"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1351:
                    result = "龙舟券"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1321:
                    result = "八宝粽子"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1327:
                    result = "捕鸟宝箱"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 601:
                    result = "青铜宝箱"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 602:
                    result = "白银宝箱"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 603:
                    result = "黄金宝箱"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 604:
                    result = "至尊宝箱"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 701:
                    result = "毒龙蛋"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 702:
                    result = "冰龙蛋"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 703:
                    result = "火龙蛋"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 704:
                    result = "圣龙蛋"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1201:
                    result = "锁定"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1202:
                    result = "冰冻"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1203:
                    result = "狂暴无双"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1205:
                    result = "赏金传送"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1301:
                    result = "灵魂宝石"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1303:
                    result = "风暴结晶"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1304:
                    result = "逐风者的碎片"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1215:
                    result = "绿灵石"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1216:
                    result = "蓝魔石"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1217:
                    result = "紫晶石"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1218:
                    result = "血精石"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1219:
                    result = "强化石"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1220:
                    result = "创房卡"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1701:
                    result = "毒龙蛋"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1702:
                    result = "冰龙蛋"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1703:
                    result = "火龙蛋"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if pro["id"] == 1704:
                    result = "圣龙蛋"
                    value = pro["count"]
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
            elif number > 200010000:
                weapon = number / 10000
                if weapon == 20001:
                    day = deal_weapon_day(number)
                    result = "流沙之鳞{}分钟".format(day)
                    value = number % 10000
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if weapon == 20002:
                    day = deal_weapon_day(number)
                    result = "冰翼猎手{}分钟".format(day)
                    value = number % 10000
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if weapon == 20003:
                    day = deal_weapon_day(number)
                    result = "翡翠荆棘{}分钟".format(day)
                    value = number % 10000
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if weapon == 20004:
                    day = deal_weapon_day(number)
                    result = "狂怒炎龙{}分钟".format(day)
                    value = number % 10000
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if weapon == 20005:
                    day = deal_weapon_day(number)
                    result = "死亡之翼{}分钟".format(day)
                    value = number % 10000
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if weapon == 20006:
                    day = deal_weapon_day(number)
                    result = "雷鸣宙斯{}分钟".format(day)
                    value = number % 10000
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if weapon == 20007:
                    day = deal_weapon_day(number)
                    result = "暗夜魅影{}分钟".format(day)
                    value = number % 10000
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if weapon == 20008:
                    day = deal_weapon_day(number)
                    result = "九五至尊{}分钟".format(day)
                    value = number % 10000
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if weapon == 20009:
                    day = deal_weapon_day(number)
                    result = "恭贺新春{}分钟".format(day)
                    value = number % 10000
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
            else:
                weapon = number / 1000
                if weapon == 20001:
                    day = deal_weapon_day(number)
                    result = "流沙之鳞{}天".format(day)
                    value = number % 1000
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if weapon == 20002:
                    day = deal_weapon_day(number)
                    result = "冰翼猎手{}天".format(day)
                    value = number % 1000
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if weapon == 20003:
                    day = deal_weapon_day(number)
                    result = "翡翠荆棘{}天".format(day)
                    value = number % 1000
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if weapon == 20004:
                    day = deal_weapon_day(number)
                    result = "狂怒炎龙{}天".format(day)
                    value = number % 1000
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if weapon == 20005:
                    day = deal_weapon_day(number)
                    result = "死亡之翼{}天".format(day)
                    value = number % 1000
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if weapon == 20006:
                    day = deal_weapon_day(number)
                    result = "雷鸣宙斯{}天".format(day)
                    value = number % 1000
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if weapon == 20007:
                    day = deal_weapon_day(number)
                    result = "暗夜魅影{}天".format(day)
                    value = number % 1000
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if weapon == 20008:
                    day = deal_weapon_day(number)
                    result = "九五至尊{}天".format(day)
                    value = number % 1000
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)
                if weapon == 20009:
                    day = deal_weapon_day(number)
                    result = "恭贺新春{}天".format(day)
                    value = number % 1000
                    reward = "{}:{}".format(result, value)
                    reward_info.append(reward)

    if 'pool' in rewards_info:
        result = "元兑换码"
        value = rewards_info['pool']
        reward = "{}{}".format(value, result)
        code_info.update({"pool": reward})
    else:
        result = "免费码"
        code_info.update({"pool": result})

    code_info.update({"reward_info": reward_info})
    return code_info


def deal_weapon_day(result):
    weapon = result / 1000
    hundreds = (result - weapon * 1000) / 100
    tens = (result - weapon * 1000 - hundreds * 100) / 10
    ones = (result - weapon * 1000 - hundreds * 100 - tens * 10) % 10
    day = int(hundreds * 100 + tens * 10 + ones)
    return day


@csrf_exempt
def page_permission_denied(request):

    return render_to_response('403.html')

#404页面
@csrf_exempt
def page_not_found(request):

    return render_to_response('404.html')

@csrf_exempt
def page_error(request):

    return render_to_response('500.html')