# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render_to_response, render, redirect
from util.context import Context
from util.tool import Time
import time
import xlrd
from xlwt import *
from io import BytesIO
import random
from util.process import ProcessInfo
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.http import JsonResponse,HttpResponse
from util.gamedate import *
import json
from login_manage.models import LoginInfo, ChannelList
from login_manage.views import decorator
from .models import *
import datetime
from hashlib import sha1
from control_manage.models import Account
from run_manage.models import EarlyWarning
from django.conf import settings
import os
from util.tool import Prpcrypt
from django.db.models import Q
# from gift_bag_shop.models import GiftInfo
import sys
reload(sys)
sys.setdefaultencoding('utf8')


@decorator
def limit_time_shop(request):
    # ret = Context.RedisMatch.hget_keys('limit_time_shop:*:prop')
    # if ret:
    #     for del_key in ret:
    #         Context.RedisMatch.delete(del_key)
    # for ch_id in ["2001_0"]:
    #     keys = 'limit_time_shop:{}:{}'.format(ch_id, 'prop')
    #     shop_icon = Shop.shop_type_name()
    #     shop_icon = {"good_list": Context.json_dumps(shop_icon)}
    #     Context.RedisMatch.hash_mset(keys, shop_icon)

    # del_record = Context.RedisCache.hget_keys('day_shop_record:{}:*:*:*'.format("15522541231"))
    # if del_record:
    #     for del_key in del_record:
    #         Context.RedisCache.delete(del_key)

    switch_info, shop_icon, product_list = Shop.shop_switch(), Shop.shop_type_name(), Shop.good_type_name()   # 1、实物，2、充值卡，3、游戏道具，4、卡密
    money_list, hot_list, vip_list, game_props = Shop.money_type(), Activity_Info.get_hot_type(), Shop.vip_grade(), Activity_Info.give_props_data()  # vip等级
    phone, number = request.session.get('uid'), 1
    deal_channel = ['0', '1000', "1001_1", "1001_2", "1001_3", "1001_4", "1001_5", "1003_1", "1004_1", "1005_1",
                    "1006_0", "1007_1", "1008_0", "1008_1", "1000_1", "1000_2", "1000_3"]
    dic = request.GET
    channel_id = dic.get('channel', "1001_0")
    context = {'pid': 1, "channel": channel_id, "phone": phone}
    url = '/v2/shell/gm/limit_time_shop'
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.content)
    if "config" not in config:
        shop_info = {"chanel_info": {channel_id: "官方", "1004_0": "OPPO"}, "number": number, "channel": channel_id, "switch": 0, "page": []}
    else:
        keys = 'limit_time_shop:{}:{}'.format(channel_id, 'prop')
        result = Context.RedisMatch.hash_mget(keys, ["good_list"])[0]
        if result:
            good_info = Context.json_loads(result)
            if len(good_info) != len(shop_icon):
                good_list = {"good_list": Context.json_dumps(shop_icon)}
                Context.RedisMatch.hash_mset(keys, good_list)

        else:
            good_list = {"good_list": Context.json_dumps(shop_icon)}
            Context.RedisMatch.hash_mset(keys, good_list)
        shop_list = []
        shop_config, switch, channel_info = config["config"], int(config["switch"]), config["channel"]
        for channel, name in channel_info.items():
            if channel in deal_channel:
                del channel_info[channel]
            else:
                continue

        for shop_id, product in shop_config.items():
            result = GoodCost.objects.filter(channelID=channel_id, goodID=shop_id).values("cost").last()
            if result:
                product['cost'] = int(float(result.get("cost", 0)))
            else:
                cost = float(ProcessInfo.get_good_cost(shop_id))
                product['cost'] = int(cost)
                GoodCost.objects.create(
                    channelID=channel_id,
                    goodID=shop_id,
                    cost=cost,
                )
            res = LimitInfo.objects.filter(good_id=shop_id, channel=channel_id).values("update_time").first()
            if res:
                update_time = Time.datetime_to_str(res.get("update_time"))[:19]
            else:
                update_time = Time.current_time("%Y-%m-%d %H:%M:%S")

            # print("-------shop_id---", shop_id, product["name"])
            product.update({"gid": shop_id, "update_time": update_time})
            create_limit_time_shop(product, channel_id)  # 插入数据
            shop_list.append(product)

        sort_list = sorted(shop_list, key=lambda s: (s['on'], int(s['gid'])), reverse=True)

        one_page = dic.get('page')
        # print("-------one_page---", one_page)
        if one_page:
            one_page = int(one_page.encode('utf-8'))
            number, index = one_page, one_page
            paginator = Paginator(sort_list, 30)
            page, plist = Context.paging(paginator, index)

            num_page = paginator.num_pages
            if one_page > num_page:
                number = num_page
            else:
                number = number
        else:
            number = 1
            paginator = Paginator(sort_list, 30)
            page, plist = Context.paging(paginator, 1)

        shop_info = {"chanel_info": channel_info, "page": page, "number": number, "switch": switch, "channel": channel_id}
    box_list = [{"vale": "601", "content": "蓝色宝箱"},{"vale": "602", "content": "紫色宝箱"},{"vale": "603", "content": "钻石宝箱"}]
    game_props.extend(box_list)
    shop_info.update({"game_props": game_props, "money_list": money_list, "shop_icon": shop_icon, "hot_list": hot_list, "vip_list": vip_list, "switch_info": switch_info, "product_list": product_list})
    return render(request, 'limit_time_shop/query_shop.html', shop_info)


def deal_with_limit_shop(request):
    phone = request.session.get('uid')
    dic = request.POST
    pid = int(dic.get('pid'))

    if pid == 1:  # 更新
        print("-----dic-----", dic)
        good_id, channel, good_type, extra_type = dic.get('gid'), dic.get('channel'), int(dic.get('goods_type')), int(dic.get('extra_type'))
        good_name, count, one_limit_num = dic.get('good_name'), int(dic.get('count')), int(dic.get('one_num'))
        all_limit_num, good_price, good_cost = int(dic.get("all_num")), int(dic.get('good_coupon')), int(dic.get('good_cost'))
        money_type, vip_limit, line, hot = int(dic.get('money_type')), int(dic.get('vip_limit')), int(dic.get('line')), int(dic.get('hot'))

        update_info = {"shop_type": 1, "channel": channel, "good_id": good_id, "type": extra_type, "hot": hot,
                       "price": good_price, "count": count, "one_limit": one_limit_num, "all_limit": all_limit_num,
                       "limit_type": vip_limit, "money_type": money_type, "on": line, "extra_type": extra_type}
        reward = {}
        if extra_type == 3:
            prop_name, props = ProcessInfo.deal_integral_info(good_name, count)
        else:
            prop = int(good_id)
            prop_id = prop / 10000 * 100 + prop % 1000
            props = {'props': [{'id': prop_id, 'count': count}]}
            prop_name = good_name
        reward.update(props)
        update_info.update({"name": prop_name, "reward": reward})
        print("-----update_info-----", update_info)
        url = '/v2/shell/gm/limit_time_shop'
        update_info.update({"phone": phone, "pid": 3})
        ret = Context.Controller.request(url, update_info)
        if ret.status_code == 200:
            good_data = ProcessInfo.good_type_info(good_type)

            line_info = ("暂不上线" if line == 0 else "上线出售")
            money_name = ("话费券" if money_type == 7 else "火龙蛋" if money_type == 8 else "圣龙蛋" if money_type == 9 else "冰龙蛋" if money_type == 10 else "龙舟券")
            update_str = "商品ID:{}".format(good_id) + "     " + "商品类别:{}".format(good_data) + "     " + "商品名称/数量:{}/{}".format(prop_name, count) + "     " \
                         + "个人兑换限制:{}_全服兑换限制:{}".format(one_limit_num, all_limit_num) + "     " + "商品单价:{}_{}".format(good_price, money_name) + "   " + "商品成本:{}_元".format(good_cost) + "     " \
                         + "vip等级限制购买要求:VIP{}".format(vip_limit) + "     " + "是否上线:{}".format(line_info)

            record_data = {"status_type": "更新", "info": update_str}
            insert_record_data(phone, LimitRecord, record_data)
            GoodCost.objects.filter(channelID=channel, goodID=good_id).update(cost=good_cost)  # 更新商城成本
            update_time = Time.current_time('%Y-%m-%d %H:%M:%S')

            res = LimitInfo.objects.filter(good_id=good_id, channel=channel).values("json_data").first()
            json_info = Context.json_loads(res.get("json_data"))
            json_info["hot"], json_info["extra_type"], json_info["name"] = hot, extra_type, prop_name
            json_info["limit_num"][0]["num"], json_info["price"] = one_limit_num, good_price
            json_info["limit_num"][1]["num"] = all_limit_num
            json_info["limit_type"], json_info["on"] = vip_limit, line
            LimitInfo.objects.filter(good_id=good_id, channel=channel).update(
                good_type=good_type,
                json_data=Context.json_dumps(json_info),
                update_time=update_time,
            )
            keys = 'limit_time_shop:{}:{}'.format(channel, 'prop')
            result = Context.RedisMatch.hash_mget(keys, ["good_list"])[0]
            good_list = Context.json_loads(result)
            update_info.update({"cost": good_cost, "good_list": good_list, 'status': True, "msg": "更新成功!", "alter_time": update_time})
            return JsonResponse(update_info)
        else:
            info = {'status': False, "msg": "更新失败!"}
            return JsonResponse(info)
    elif pid == 2:  # 显示成功
        good_id, channel = dic.get('good_id').encode('utf-8'), dic.get('channel')
        result = LimitInfo.objects.filter(good_id=good_id, channel=channel).values("json_data").first()
        if result:
            pic = LimitPictures.objects.filter(pic_id=good_id).values("pic_path", "pic_name").first()
            if pic:
                image = "/static/media/{}".format(pic.get("pic_path"))
            else:
                image = "/static/images/default.jpg"
            good_data = Context.json_loads(result.get("json_data"))

            good_type = int(good_data["extra_type"])
            if good_type == 3 or good_type == 5:
                reward_info = ProcessInfo.deal_gift_reward(good_data["reward"])
                reward = reward_info[0]
            elif good_type == -1:
                value = 1
                name = good_data["name"]
                reward = {"name": name, "value": value}
            else:
                value = good_data["reward"]["props"][0]["count"]
                name = good_data["name"]
                reward = {"name": name, "value": value}
            buy_type = str(good_data.get("money", "7"))

            good_data.update({"one_limit": good_data["limit_num"][0]["num"], "all_limit": good_data["limit_num"][1]["num"]})
            good_data.update({'status': True, 'msg': "显示成功", "channel": channel,"buy_type": buy_type, "reward": reward, "image": image})
        else:
            good_data = {"status": False, "msg": "数据处理异常!"}
        print("--------good_data-------", good_data)
        return JsonResponse(good_data)
    else:  # 商城开关
        switch = int(dic.get("shop_switch"))
        url = '/v2/shell/gm/limit_time_shop'
        context = {'pid': 4, 'open': switch, "phone": phone}
        ret = Context.Controller.request(url, context)
        if switch == 0:
            open_close = "开启"
        else:
            open_close = "关闭"
        if ret.status_code == 200:
            status = True
            msg = "商城{}成功！".format(open_close)
        else:
            status = False
            msg = "商城{}失败！".format(open_close)
        return JsonResponse({'status': status, 'msg': msg, "switch": switch})


@decorator
def deal_shop_picture(request):
    # 添加新的商品
    address = request.get_host()
    phone = request.session.get('uid')
    dic = request.POST
    sid = int(dic.get('sid'))
    channel = dic.get('channel').encode("utf-8")
    if sid == 1:
        prop_id = LimitGoodId.objects.all().values("prop_id").last()
        if prop_id:
            prop_id = int(prop_id.get("prop_id", 0)) + 1
            LimitGoodId.objects.create(
                prop_id=prop_id,
            )
        else:
            good_id = 160000
            prop_id = 1000
            LimitGoodId.objects.create(
                good_id=good_id,
                prop_id=prop_id,
            )
        ret = LimitGoodId.objects.filter(prop_id=prop_id).values("good_id").first()
        pic_id = str(ret.get("good_id"))
        img_file = request.FILES.get("picture")
        add_id, msg, status, img_file = insert_picture(phone, img_file, pic_id, address, sid, channel)
    else:
        pic_id = int(request.POST.get("pic_id"))
        img_file = request.FILES.get("picture")
        add_id, msg, status, img_file = insert_picture(phone, img_file, pic_id, address, sid, channel)

    return JsonResponse({"status": status, "msg": msg, "img_file": img_file, "add_id": add_id})


def insert_picture(phone, img_file, pic_id, address, deal_img, channel):
    add_id, status = 0, False
    default_img = "/static/images/default.jpg"
    if img_file:
        suffix = os.path.splitext(img_file.name)[1].lower()
        # upload_name = img_file.name.encode('utf-8')
        type_list = ['.png']  # '.png', '.gif'
        pic_name = 'picture_{}'.format(pic_id)
        joint_path = "limit_time_shop/{}/".format(channel)

        if os.path.splitext(img_file.name)[1].lower() in type_list:
            picture_name = "{}{}".format(pic_name, suffix)
            result = LimitPictures.objects.filter(pic_id=pic_id, channel=channel).values("pic_name")
            if result:
                LimitPictures.objects.filter(pic_id=pic_id).update(
                    pic_name=picture_name,
                    channel=channel,
                    pic_path=joint_path + picture_name
                )
            else:
                LimitPictures.objects.create(
                    pic_id=pic_id,
                    pic_name=picture_name,
                    channel=channel,
                    pic_path=joint_path + picture_name,
                )

            img_path = "/limit_time_shop/{}".format(channel)
            image_path = settings.MEDIA_ROOT + img_path
            if not os.path.exists(image_path):
                os.makedirs(image_path)

            file_img = "/limit_time_shop/{}/".format(channel)
            file_name = settings.MEDIA_ROOT + file_img + picture_name
            if deal_img == 2:
                if os.path.isfile(file_name):
                    os.remove(file_name)

                with open(file_name, 'wb') as pic:
                    pic.write(img_file.read())
            else:
                with open(file_name, 'wb') as pic:
                    pic.write(img_file.read())
                # for c in img_file.chunks():
                #     pic.write(c)

            path = LimitPictures.objects.filter(pic_id=pic_id,channel=channel).values("pic_path", "pic_name").first()
            if path:
                new_path = path.get("pic_path")
                pic_name = path.get("pic_name")

                rank_picture = "http://{}/static/media/{}".format(address, new_path).encode('utf-8')
                url = '/v2/game/product/update_picture_version'
                context = {"pn": pic_name, "pu": rank_picture}
                context.update({"phone": phone})
                ret = Context.Controller.request(url, context)
                if ret.status_code == 200:
                    msg = "上传图片成功!"
                    add_id, status = int(pic_id), True
                    rand_str = ""
                    for s in range(6):
                        ch = chr(random.randrange(ord('0'), ord('9') + 1))
                        rand_str += ch
                    default_img = "/static/media/{}?{}".format(new_path, rand_str)
                    print("------------default11", default_img, type(default_img))
                else:
                    msg = "上传图片失败!"
                # msg = "上传图片成功!"
                # add_id, status = int(pic_id), True
                # default_img = "/static/media/{}".format(new_path)
            else:
                msg = "上传图片不存在!"
        else:
            msg = "上传图片格式错误!"
    else:
        msg = "未选择图片!"
    return add_id, msg, status, default_img


@decorator
def add_shop_good(request):
    """限时商城--添加商品"""
    good_list = Shop.shop_type_name()
    phone = request.session.get('uid')
    dic = request.POST
    good_id = dic.get("good_id")
    channel = dic.get("channel").encode('utf-8')
    hot = int(dic.get("hot"))
    good_type = int(dic.get("good_type", 1))
    new_type_name = dic.get("new_type_name", "").encode('utf-8')
    one_limit = int(dic.get("one_limit_num", 0))
    good_name = dic.get("good_name", "").encode('utf-8')
    count = int(dic.get("count", 0))
    cost = float(dic.get("good_cost", 0))
    limit_type = int(dic.get("limit_type", 0))
    limit_num = int(dic.get("all_limit_num", 0))
    price = int(dic.get("price", 0))
    extra_type = int(dic.get("add_extra_type", 0))  # 额外类型
    money_type = int(dic.get("money_type", 0))
    vip_limit = int(dic.get("vip_limit", 0))
    line = int(dic.get("line", 0))

    reward = {}
    if extra_type == 3:
        game_name, props = ProcessInfo.deal_integral_info(good_name, count)
    else:
        prop = int(good_id)
        prop_id = prop / 10000 * 100 + prop % 1000
        props = {'props': [{'id': prop_id, 'count': count}]}
        game_name = good_name

    limit_list = [{"type": 1, "num": one_limit}, {"type": 2, "num": limit_num}]
    print("------------------props6666666", props)
    reward.update(props)
    good_info = {
            "name": game_name,
            "reward": reward,
            "money": money_type,
            "price": price,
            "limit_type": vip_limit,
            "limit_num": limit_list,
            "detail": u"暂无描述",
            "on": line,
            "extra_type": extra_type,
            "hot": hot,
        }
    if good_type == 0:
        #  存储redis
        add_type = {"vale": str(extra_type), "content": new_type_name}
        good_list.append(add_type)
        redis_info = {"good_list": Context.json_dumps(good_list)}
        keys = 'limit_time_shop:{}:{}'.format(channel, 'prop')
        Context.RedisMatch.hash_mset(keys, redis_info)
        good_info.update({"type": extra_type, "type_name": new_type_name})
    else:
        good_info.update({"type": good_type})

    url = '/v2/shell/gm/limit_time_shop'
    context = {"pid": 2, "phone": phone, "channel_id": channel, "product_id": good_id, "config": good_info}
    print("------------------context6666666", context)
    ret = Context.Controller.request(url, context)
    server = Context.json_loads(ret.content)
    if server:
        info = {'status': False, "msg": "添加失败!"}
    else:
        good_info.update({"gid": good_id})
        create_limit_time_shop(good_info, channel)
        GoodCost.objects.create(
            channelID=channel,
            goodID=good_id,
            cost=cost,
        )
        info = {'status': True, "msg": "添加成功!"}
    return JsonResponse(info)


@decorator
def shop_exchange_info(request):
    # file_name = settings.MEDIA_ROOT + "/upload_files/" + "20200826.xls"
    # if os.path.exists(file_name):
    #     print("-----file_name------", file_name)
    #     wb = xlrd.open_workbook(file_name, encoding_override="UTF-8-SIG")
    #     table = wb.sheets()[0]
    #     rows = table.nrows  # 总行数
    #     row_info = []
    #     for i in range(1, rows):
    #         row_dict = {}
    #         row = table.row_values(i)
    #         row_dict.update({"card_number": str(row[5])})
    #         row_info.append(row_dict)
    #     for info in row_info:
    #         card_number = info["card_number"]
    #         SetCardsClose.objects.filter(card_number=card_number).delete()
    phone, url_date, number = request.session.get('uid'), "/limit_time_shop/shop_exchange_info/", 1
    good_list = Shop.shop_filter_name()  # 商品筛选条件
    filter_record = Shop.get_convert_record()  # 兑换记录筛选条件
    shipping_list = Shop.get_ship_status_data()  # 发货状态筛选
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    del chanel_info['1000']
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page:
            conf, record_info = get_exchange_record_info(phone)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            record_info.update({"number": number, "page": page})
        else:
            end_day = datetime.date.today().strftime('%Y-%m-%d')
            record_info = {"start_day": end_day, "end_day": end_day, "channel": "0", "good_style": "0","screen_info": "uid", "input_data": "", "ship_status": "3", "cost_total": 0, "page": [],"number": number}
    else:
        dic = request.POST
        start_time = dic.get("start_time")[:10]
        end_time = dic.get("stop_time")[:10]
        channel = dic.get("channel").encode('utf-8')
        screen_info = dic.get("screen_info").encode('utf-8')
        good_style = dic.get("good_style").encode('utf-8')
        ship_status = dic.get("ship_status").encode('utf-8')
        input_data = dic.get("input_data").encode('utf-8').strip()

        start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')

        day_list = []
        while start_date <= end_date:
            res = ExchangeInfo.objects.filter(day_time=start_date).first()
            every_day = Time.datetime_to_str(start_date, '%Y-%m-%d')
            if res:
                start_date = Time.next_days(start_date)
                continue
            else:
                day_order = Context.RedisCache.hget_keys('day_shop_record:{}:{}:*:*'.format(phone, every_day))
                if day_order:
                    day_list.append(every_day)
                    if every_day == datetime.datetime.now().strftime('%Y-%m-%d'):
                        msg = insert_redis_exchange(phone, every_day, every_day,screen_info,input_data)  # 插入数据
                    else:
                        start_date = Time.next_days(start_date)
                        continue
                else:
                    day_list.append(every_day)
                    msg = insert_redis_exchange(phone, every_day, every_day,screen_info,input_data)  # 插入数据
            start_date = Time.next_days(start_date)

        record_info = {"start_day": start_time, "end_day": end_time, "channel": channel, "screen_info": screen_info,"good_style": good_style, "ship_status": ship_status, "input_data": input_data,"day_list": day_list}
        keys = 'shop_exchange:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, record_info)

        start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')
        record_data, cost_total = query_redis_data(phone,start_date, end_date, channel, screen_info, good_style, ship_status,input_data,day_list)

        paginator = Paginator(record_data, 30)
        page, plist = Context.paging(paginator, 1)

        record_info.update({"number": number, "page": page, "cost_total": cost_total})

    user_limit = Context.get_user_limit(phone)
    record_info.update({'user_limit': user_limit, 'json_limit': Context.json_dumps(user_limit), "good_list": good_list, "filter_record": filter_record, "chanel_info": chanel_info,"shipping_list": shipping_list, "url_date": url_date})
    return render(request, 'limit_time_shop/shop_convert_record.html', record_info)


def insert_mysql_exchange(phone, start_time, end_time):
    """插入--商城兑换记录"""
    url = '/v1/shell/shop/exchange_record'
    context = {"start": start_time + " 00:00:00", "end": end_time + " 23:59:59"}
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    event = Context.json_loads(ret.content)
    if not event.has_key("ret"):
        return 0
    else:
        config = event["ret"]
        record_info = []
        for info in config:
            for key, values in info.items():
                event_time = Time.timestamp_to_str(int(key) / 1000)
                stats, uid, pid, channel = int(values.get("stat")),str(values.get("uid")),values.get("pid", 0),values.get("pay_channel", 0)
                result = GoodCost.objects.filter(channelID=channel, goodID=pid).values("cost").last()
                if result:
                    cost = int(float(result.get("cost", 0)))
                else:
                    cost = int(float(ProcessInfo.get_good_cost(pid)))
                    GoodCost.objects.create(channelID=channel, goodID=pid, cost=cost)

                values.update({'cost': cost,'order_id': key,'stat': stats,'start_time': event_time})
                day_times = values.get("times", 0)
                keys_list = Context.RedisCache.hget_keys('day_shop_record:*:{}:{}:{}'.format(day_times, uid, key))
                if keys_list:
                    new_result = Context.RedisCache.hash_mget(keys_list[0], ["stat", "end_time"])
                    original_state = int(new_result[0])
                    if original_state != 2:
                        end_time = event_time
                        values.update({'stat': original_state, 'end_time': end_time})
                    else:
                        end_time = new_result[1]
                        values.update({'end_time': end_time})
                else:
                    result = ExchangeInfo.objects.filter(order_id=key, uid=uid).values("status", "json_data").first()
                    if result:
                        json_info = Context.json_loads(result.get("json_data"))
                        up_time = json_info.get("end_time")
                        insert_status = int(result.get("status"))
                        values.update({'stat': insert_status,'end_time': up_time})
                    else:
                        end_time = int(values.get("end_time", Time.current_ts()))
                        values.update({'end_time': Time.timestamp_to_str(end_time)})
                record_info.append(values)
                ret = Context.RedisCache.hget_keys('day_shop_record:*:{}:{}:{}'.format(day_times, uid, key))
                if ret:
                    for del_key in ret:
                        Context.RedisCache.delete(del_key)
        create_exchange_record(record_info)


def insert_redis_exchange(phone,start_time,end_time,screen_info,input_data):
    start_day, end_day = start_time + " 00:00:00", end_time + " 23:59:59"
    if input_data != "":
        context = {"start": start_day, "end": end_day, "screen_info": screen_info, "input_data": input_data}
    else:
        context = {"start": start_day, "end": end_day}

    url = '/v1/shell/shop/exchange_record'
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    ret_dict = Context.json_loads(ret.content)
    if "ret" not in ret_dict:
        return 0
    else:
        # del_record = Context.RedisCache.hget_keys('day_shop_record:{}:*:*'.format(phone))
        # if del_record:
        #     for del_key in del_record:
        #         Context.RedisCache.delete(del_key)
        config = ret_dict["ret"]
        user_dict = {}
        for info in config:
            for key, values in info.items():
                day_time, uid = values.get("times"), str(values.get("uid"))
                pid, channel = values.get("pid", 0), values.get("pay_channel", 0)
                result = GoodCost.objects.filter(channelID=channel, goodID=pid).values("cost").last()
                if result:
                    cost = int(float(result.get("cost", 0)))
                else:
                    cost = int(float(ProcessInfo.get_good_cost(pid)))
                if not user_dict.has_key(day_time):
                    user_dict[day_time] = {}
                user_dict[day_time][uid] = user_dict[day_time].get(uid, 0) + cost

        for info in config:
            for key, values in info.items():
                event_time = Time.timestamp_to_str(int(key) / 1000)
                good_type = int(values.get("good_type", 0))
                stats, uid, pid, channel = int(values.get("stat")), str(values.get("uid")), values.get("pid", 0), values.get("pay_channel", 0)
                up_status = update_status(phone, values, user_dict, stats)  # 处理异常预警
                result = GoodCost.objects.filter(channelID=channel, goodID=pid).values("cost").last()
                if result:
                    cost = int(float(result.get("cost", 0)))
                else:
                    cost = int(ProcessInfo.get_good_cost(pid))
                    GoodCost.objects.create(channelID=channel, goodID=pid, cost=cost)

                values.update({'cost': cost, 'order_id': key, 'stat': up_status, 'start_time': event_time})
                day_times = values.get("times", 0)
                shop_keys = 'day_shop_record:{}:{}:{}:{}'.format(phone, day_times, uid, key)
                ret_redis = Context.RedisCache.hash_mget(shop_keys, ["stat", "end_time"])
                if ret_redis[0]:
                    if int(stats) == 2:
                        insert_status = stats
                        end_time = ret_redis[1]
                    else:
                        insert_status = int(ret_redis[0])
                        end_time = ret_redis[1]
                    values.update({'stat': insert_status, 'end_time': end_time})
                else:
                    keys_list = Context.RedisCache.hget_keys('day_shop_record:*:{}:{}:{}'.format(day_times, uid, key))
                    if keys_list:
                        new_result = Context.RedisCache.hash_mget(keys_list[0], ["stat", "end_time"])
                        if int(stats) == 2:
                            insert_status = stats
                            end_time = new_result[1]
                        else:
                            insert_status = int(new_result[0])
                            end_time = new_result[1]
                    else:
                        if int(stats) == 2 and (good_type != 3 or good_type != 5):
                            good_id = str(key)
                            card_data = SetCardsClose.objects.filter(good_id=good_id, player_id=uid).values("change_time").first()
                            if card_data:
                                end_time = Time.datetime_to_str(card_data.get("change_time"), "%Y-%m-%d %H:%M:%S")
                            else:
                                end_time = event_time
                            insert_status = up_status
                        else:
                            insert_status = up_status
                            end_time = event_time
                    values.update({'stat': insert_status, 'end_time': end_time})
                Context.RedisCache.hash_mset('day_shop_record:{}:{}:{}:{}'.format(phone, values["times"], values["uid"], key), values)


def update_status(phone, values, user_dict, stats):
    uid = str(values.get("uid"))
    day_time = values.get("times")
    day_total = int(values.get("day_total")) * 3
    day_cdkey = int(values.get("day_cdkey"))
    day_good_price = user_dict[day_time].get(uid, 0)

    if (day_good_price >= day_total) or (day_cdkey >= 500 and day_good_price >= 300):
        res_over = EarlyWarning.objects.filter(user_status=1).values("user_list", "user_length").first()
        if res_over:
            o_list = Context.json_loads(res_over.get("user_list", []))
        else:
            o_list = []
        res_for = EarlyWarning.objects.filter(user_status=3).values("user_list", "user_length").first()
        if res_for:
            f_list = Context.json_loads(res_for.get("user_list", []))
        else:
            f_list = []

        if uid in o_list:
            up_status = stats

        elif uid in f_list:
            up_status = 6
        else:
            if int(stats) == 2:
                up_status = stats
            else:
                up_status = 6
    else:
        # user_count = ExchangeInfo.objects.filter(uid=uid, status=6).aggregate(Count("id"))
        # u_count = int(user_count.get("id__count", 0))
        u_count = 0
        day_record = Context.RedisCache.hget_keys('day_shop_record:{}:{}:{}:*'.format(phone, day_time, uid))
        for key in day_record:
            ret = Context.RedisCache.hash_getall(key)
            if str(ret["uid"]) == uid and int(ret["stat"]) == 6:
                u_count = u_count + 1
            else:
                continue

        if u_count > 0:
            up_status = 6
        else:
            up_status = stats

    return up_status


@decorator
def alter_check_status(request):
    url = '/v2/shell/shop/many_approve_status'
    dic = request.POST
    pid = int(dic.get("pid"))
    phone = request.session.get('uid')
    if pid == 1:  # 处理单个
        exchange_info, deal_status = deal_one_exchange(dic)
    elif pid == 2:  # 处理多个
        exchange_info, deal_status = deal_many_exchange(phone, dic)
    elif pid == 3:  # 客服处理单个
        exchange_info, _ = deal_one_exchange(dic)
        context = {'exchange_list': exchange_info}
        context.update({"phone": phone})
        ret = Context.Controller.request(url, context)
        if ret.status_code == 200:
            deal_status = True
        else:
            deal_status = False
    else:  # 客服处理多个
        exchange_info, _ = deal_many_exchange(phone,dic)
        context = {'exchange_list': exchange_info}
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)
        if ret.status_code == 200:
            deal_status = True
        else:
            deal_status = False
    update_exchange_id(phone,exchange_info)
    return JsonResponse({'status': deal_status,"u_list":exchange_info})


def update_exchange_id(phone, ex_info):
    for info in ex_info:
        good_id = info["exchange_id"]
        user_id = info["user_id"]
        status = int(info["status"])
        if status == 0:
            insert_status = "未审核"
        elif status == 1:
            insert_status = "未发货"
        elif status == 6:
            insert_status = "审核异常"
        else:
            insert_status = "暂不通过"
        record_data = {"status_type": insert_status, "info":  good_id}
        insert_record_data(phone, ExchangeRecord, record_data)
        result = ExchangeInfo.objects.filter(order_id=good_id,uid=user_id).values("status","json_data").first()
        if result:
            json_info = Context.json_loads(result.get("json_data"))
            local_status = int(json_info.get("stat", 0))
            if local_status == 2 or (local_status == 6 and status == 1) or (local_status == 1 and status == 0) :
                json_info["stat"] = local_status
                ExchangeInfo.objects.filter(order_id=good_id, uid=user_id).update(
                    status=local_status,
                    json_data=Context.json_dumps(json_info),
                )
            else:
                json_info["stat"] = status
                ExchangeInfo.objects.filter(order_id=good_id, uid=user_id).update(
                    status=status,
                    json_data=Context.json_dumps(json_info),
                )
        else:
            day_time = Time.timestamp_to_str(int(good_id) / 1000)[:10]
            keys_list = Context.RedisCache.hget_keys('day_shop_record:*:{}:{}:{}'.format(day_time, user_id, good_id))
            for deal_key in keys_list:
                ret_redis = Context.RedisCache.hash_mget(deal_key, ["stat"])
                local_status = int(ret_redis[0])
                if local_status == 2 or (local_status == 6 and status == 1) or (local_status == 1 and status == 0):
                    new_status = local_status
                else:
                    new_status = status
                Context.RedisCache.hash_mset(deal_key, {"stat": new_status})


def deal_one_exchange(dic):
    exchange_info = []
    deal_status = True
    status = dic.get("status")
    exchange_id = dic.get("exchange_id")
    user_id = dic.get("user_ID")
    good_type = dic.get("good_type")
    Pid = dic.get("Pid")
    one_dict = {"status": status, "exchange_id": exchange_id, "user_id": user_id, "good_type": good_type, "pid": Pid}
    exchange_info.append(one_dict)
    return exchange_info,deal_status


def deal_many_exchange(phone,dic):
    exchange_info = []
    deal_status = True
    exchange_list = dic.getlist("order_id")
    status = dic.get("status")
    for order in exchange_list:
        str_info = order.encode('utf-8').split(':')
        exchange_id, user_id, good_type, Pid = str_info[0], str_info[1], str_info[2], str_info[3]
        result = ExchangeInfo.objects.filter(order_id=exchange_id, uid=user_id).values("json_data").first()
        if result:
            json_info = Context.json_loads(result.get("json_data"))
            local_status = int(json_info.get("stat", 0))
        else:
            day_time = Time.timestamp_to_str(int(exchange_id) / 1000)[:10]
            deal_key = 'day_shop_record:{}:{}:{}:{}'.format(phone, day_time, user_id, exchange_id)
            ret_redis = Context.RedisCache.hash_mget(deal_key, ["stat"])
            local_status = int(ret_redis[0])

        if local_status == 2 or (local_status == 6 and status == 1) or (local_status == 1 and status == 0):
            continue
        else:
            many_dict = {"status": status, "exchange_id": exchange_id, "user_id": user_id, "good_type": good_type,"pid": Pid}
            exchange_info.append(many_dict)
    return exchange_info,deal_status


@decorator
def shipping_info(request):
    """兑换记录--发货信息显示"""
    # 1:道具或实物，1是数码设备、2是充值卡、3是虚拟道具、4卡密、5卡类实物
    phone = request.session.get('uid')
    url = '/v1/shell/shop/shipping_info'
    dic = request.POST
    shop_id = int(dic.get('shop_id'))
    print("---------------shop_id", shop_id)
    if shop_id == 1:
        uid = dic.get('uid')
        order = dic.get('order')
        good_type = dic.get('good_type')
        pid = dic.get('pid')
        context = {'uid': uid, "phone": phone}
        ret = Context.Controller.request(url, context)
        event = Context.json_loads(ret.content)
        if not event.has_key("info"):
            result = {'status': False, 'msg': "服务器返回数据异常!"}
            return JsonResponse(result)
        else:
            print("---------------event77", event, good_type)
            ship_info = event['info']
            if len(ship_info) <= 0:
                good_type = int(good_type)
                res_info = ExchangeInfo.objects.filter(uid=uid, order_id=order).values('json_data').first()
                if res_info:
                    json_info = Context.json_loads(res_info.get("json_data"))
                    good_name = json_info.get("good_name", "0")
                else:
                    day_time = Time.timestamp_to_str(int(order) / 1000)[:10]
                    deal_key = 'day_shop_record:{}:{}:{}:{}'.format(phone, day_time, uid, order)
                    ret_redis = Context.RedisCache.hash_mget(deal_key, ["good_name", "uid"])
                    good_name = str(ret_redis[0])

                good_info = {'uid': uid, 'order': order, 'good_type': good_type, "good_name": good_name, 'pid': pid}
                if good_type == 2 or good_type == 4 or good_type == -1:
                    card_number = "2019052217192216574"
                    card_secret = "2019052217192216574"
                else:
                    card_number = ""
                    card_secret = ""

                send_info = {"phone": "", "address": "", "area": "", "name": ""}
                result = {'status': True, 'msg': "收货信息不存在!", 'ship_info': send_info, 'good_info': good_info, "card_number": card_number, "card_secret": card_secret}
                return JsonResponse(result)
            else:
                good_type = int(good_type)
                res_info = ExchangeInfo.objects.filter(uid=uid, order_id=order).values('json_data').first()
                if res_info:
                    json_info = Context.json_loads(res_info.get("json_data"))
                    good_name = json_info.get("good_name", "0")
                else:
                    day_time = Time.timestamp_to_str(int(order) / 1000)[:10]
                    deal_key = 'day_shop_record:{}:{}:{}:{}'.format(phone, day_time, uid, order)
                    ret_redis = Context.RedisCache.hash_mget(deal_key, ["good_name", "uid"])
                    good_name = str(ret_redis[0])

                good_info = {'uid': uid, 'order': order, 'good_type': good_type, "good_name": good_name, 'pid': pid}
                if good_type == 2 or good_type == 4 or good_type == -1:
                    card_number = "2019052217192216574"
                    card_secret = "2019052217192216574"
                else:
                    card_number = ""
                    card_secret = ""
                result = {'status': True, 'msg': "收货信息正确!", 'ship_info': ship_info, 'good_info': good_info, "card_number": card_number, "card_secret": card_secret}
                return JsonResponse(result, safe=False)
    else:
        order = dic.get('order')
        player_id = dic.get('uid')
        page = dic.get('page')
        context = {'uid': player_id, 'order_id': order}
        context.update({"phone": phone})
        ret = Context.Controller.request(url, context)
        event = Context.json_loads(ret.content)
        particulars = event['info']
        print("---tf", particulars)
        if "order_number" in particulars:
            send_order = particulars["order_number"]
            particulars.update({"status": True, "page": page, "order": order, "send": send_order})
            return JsonResponse(particulars, safe=False)
        elif particulars["good_type"] == 3:
            particulars.update({"status": True})
            return JsonResponse(particulars, safe=False)
        else:
            result = {'status': False, 'msg': "服务器返回数据异常!"}
            return JsonResponse(result)


@decorator
def alter_shipping_status(request):
    """兑换记录--修改发货状态"""
    info = request.POST
    good_id, player_id, payer_nick = info.get('order_id'), str(info.get('uid')), info.get('payer_name')
    player_phone, good_type, good_name = info.get('phone'), int(info.get('good_type')), info.get('good_name')
    pid, sex, area, address = info.get('pid'), info.get('sex'), info.get('area'), info.get('address')
    u_phone, email = info.get('phone'), info.get('mail')

    order_number, card_number, card_secret, order_info, salt_status = 0, 0, 0, {}, 0
    phone = request.session.get('uid')
    update_time = Time.current_time('%Y-%m-%d %H:%M:%S')
    mobile_list = ["140028", "140030", "150002"]  # 移动
    unicom_list = ["140027", "140029", "150003"]  # 联通
    jd_list = ["140037", "150001", "150004", "150005", "150006", "150007", "150008", "150009", "150010", "150011", "150012"]  # 京东卡

    print("-------good_type--------", good_type, player_id)
    # 1 实物 2 卡密 3和5 游戏道具
    if good_type == 1:
        order_number = info.get('express_number')
        order_info['express_number'] = order_number
    elif good_type == 3 or good_type == 5:
        order_info['qb'] = 0
    elif good_type == 2 or good_type == 4 or good_type == -1:
        order_id = SetCardsClose.objects.filter(good_id=good_id, player_id=player_id).values("good_id").first()
        if order_id:
            code, msg = False, "订单已发货请重新查询状态!"
            return JsonResponse({'code': code, 'msg': msg})
        else:
            import re
            good_name = good_name.encode('utf-8')
            print(good_name)
            if "月卡" in good_name:
                card_price = 20
            elif "季卡" in good_name:
                card_price = 60
            else:
                card_price = re.findall(r"\d+", good_name)[0]

            good_info = pid.encode('utf-8')
            if good_info in mobile_list:
                card_type = "移动"
            elif good_info in unicom_list:
                card_type = "联通"
            elif good_info in jd_list:
                card_type = "京东"
            else:
                card_type = good_name
            print(card_type)
            user_id = SetCardsClose.objects.filter(good_id=good_id, player_id=player_id).values("player_id").first()
            if user_id:
                code, msg = False, "订单已发货请联系技术解决!"
                return JsonResponse({'code': code, 'msg': msg})
            else:
                card = SetCardsClose.objects.filter(change_state=2, card_price=card_price, card_type=card_type).values("card_number","card_secret").first()
                if card:
                    order_info.update({'card_number': card.get("card_number")})
                    card_str = str(card.get("card_secret"))
                    if card_str.isdigit():
                        card_close = card_str
                    else:
                        salt_status = 1
                        card_close = Prpcrypt.decrypt(card_str)
                    order_info.update({'card_close': card_close})
                else:
                    code, msg = False, "卡密已用完请上传卡密!"
                    return JsonResponse({'code': code, 'msg': msg})
    else:
        order_number = info.get('express_number')
        order_info['express_number'] = order_number

    order_id = SetCardsClose.objects.filter(good_id=good_id, player_id=player_id).values("good_id").first()
    if order_id:
        code, msg = False, "订单已发货请联系技术处理!"
    else:
        url = '/v1/shell/shop/shipping_state'
        context = {"phone": phone, 'uid': player_id, 'order_id': good_id, 'order_info': order_info}
        ret = Context.Controller.request(url, context)
        send_info = Context.json_loads(ret.content)
        if not send_info:
            status = 2
            result = ExchangeInfo.objects.filter(order_id=good_id, uid=player_id).values("status", "json_data").first()
            if result:
                json_info = Context.json_loads(result.get("json_data"))
                json_info["stat"] = status
                json_info["end_time"] = update_time
                ExchangeInfo.objects.filter(order_id=good_id, uid=player_id).update(
                    status=status,
                    json_data=Context.json_dumps(json_info),
                )
            else:
                day_time = Time.timestamp_to_str(int(good_id) / 1000)[:10]
                keys_list = Context.RedisCache.hget_keys('day_shop_record:*:{}:{}:{}'.format(day_time, player_id, good_id))
                for deal_key in keys_list:
                    Context.RedisCache.hash_mset(deal_key, {"stat": status, "end_time": update_time})

            if good_type == 2 or good_type == 4 or good_type == -1:
                card_number, card_secret = order_info["card_number"], str(order_info["card_close"])
                if salt_status == 1:
                    salt_card = Prpcrypt.encrypt(str(card_secret))
                else:
                    salt_card = card_secret

                SetCardsClose.objects.filter(card_number=card_number, card_secret=salt_card).update(
                    good_id=good_id,
                    player_id=player_id,
                    player_nick=payer_nick,
                    player_phone=player_phone,
                    change_time=datetime.datetime.now(),
                    change_state=1,
                )
                mail_info = {"name": good_name, "card_number": card_number, "card_secret": card_secret}
            elif good_type == 1:
                mail_info = {"name": good_name, "express_number": order_number}
            elif good_type == 3 or good_type == 5:
                mail_info = {"name": good_name, "express_number": order_number}
            else:
                mail_info = {"name": good_name}
            tl = ProcessInfo.exchange_info(good_type, mail_info)
            # tips:邮件内容  tl邮件标题
            context = {"phone": phone, 't': 1, "r": {"tips": tl}, "u": int(player_id), "tl": good_name}
            url = '/v1/shell/gm/reward/add_mail'
            ret = Context.Controller.request(url, context)
            if ret.status_code == 200:
                msg = "发货成功！"
            else:
                msg = "发货通知邮件失败！"
            code = True
            record_data = {"status_type": "发货", "info": good_id}
            insert_record_data(phone, ExchangeRecord, record_data)
        else:
            code, msg = False, "发货失败!"
    return JsonResponse({'code': code, 'msg': msg, "uptime": update_time})


@decorator
def query_card_secret(request):
    phone, number, url_date = request.session.get('uid'), 1, "/limit_time_shop/card_secret/"
    filter_supplier = Shop.get_card_supplier()  # 供应商
    filter_price = Shop.get_card_price()  # 价格
    filter_status = Shop.get_card_status()  # 兑换状态
    filter_info = Shop.get_card_info()  # 筛选条件
    inventory = Shop.get_inventory_info()  # 剩余库存
    surplus_list, change_state = [], 2
    for info in inventory:
        money = int(info["vale"])
        surplus = SetCardsClose.objects.filter(card_price=money, change_state=change_state).count()
        info.update({"surplus": surplus})
        surplus_list.append(info)
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page:
            conf, card_info = get_cards_info(phone)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            card_info.update({"number": number, "page": page})
        else:
            end_day = datetime.date.today().strftime('%Y-%m-%d')
            supplier, price, status, card_screen, input_data,page = "0", "0", "0", "0", "",[]
            card_info = {"start_day": end_day, "end_day": end_day,"supplier": supplier, "price": price,"status": status, "card_screen": card_screen, "input_data": input_data, "number": number,"page": page}
    else:
        dic = request.POST
        start_time = dic.get("start_time")[:10]  # 查询开始时间
        end_time = dic.get("stop_time")[:10]  # 查询结束时间
        supplier = dic.get('supplier').encode('utf-8')
        price = dic.get('price').encode('utf-8')
        status = dic.get('status').encode('utf-8')
        card_screen = dic.get('card_screen').encode('utf-8')
        input_data = dic.get('input_data').encode('utf-8').strip()
        # 记录
        card_str = "{}_{}_{}_{}_{}_{}_{}_{}".format(phone, start_time, end_time, supplier, price, status, card_screen, input_data)
        record_data = {"status_type": "卡密查询", "info": card_str}
        insert_record_data(phone, ExchangeRecord, record_data)

        card_info = {"start_day": start_time, "end_day": end_time, "supplier": supplier, "price": price, "status": status, "card_screen": card_screen, "input_data": input_data}
        keys = 'card_secret:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, card_info)

        card_data = filter_data(supplier, price, status, card_screen, input_data, start_time, end_time)
        sorted_info = []
        o_rid = 1
        for card in card_data:
            card.update({"orid": o_rid})
            sorted_info.append(card)
            o_rid = o_rid + 1

        paginator = Paginator(sorted_info, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        card_info.update({"number": number, "page": page})

    card_info.update({"filter_supplier":filter_supplier,"surplus_list":surplus_list,"filter_price":filter_price,"filter_status":filter_status,"filter_info":filter_info})
    return render(request, 'limit_time_shop/set_cards_close.html', card_info)


@decorator
def excel_handle(request):
    phone = request.session.get('uid')
    time_now = str(Time.current_ms())
    print("-------time_now------", time_now)
    record_data = {"status_type": "上传卡密", "info": phone}
    insert_record_data(phone, ExchangeRecord, record_data)
    from django.db import transaction
    if request.method == 'POST':
        file_obj = request.FILES.get('cards_file')
        # file_obj = request.FILES.get('file')
        excel_type = file_obj.name.split('.')[1]
        if excel_type in ['xlsx','xls']:
            # 开始解析上传的excel表格
            wb = xlrd.open_workbook(filename=None, file_contents=file_obj.read())
            table = wb.sheets()[0]
            rows = table.nrows  # 总行数
            upload_path = settings.MEDIA_ROOT + "/upload_files"
            print("-------upload_path------", upload_path)
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            file_name = settings.MEDIA_ROOT + "/upload_files/" + time_now + file_obj.name  # 上传文件本地保存路径
            print("-------file_name------", file_name)
            with open(file_name, 'wb') as f:
                for c in file_obj.chunks():
                    f.write(c)
            f.close()
            try:
                with transaction.atomic():  # 控制数据库事务交易
                    row_info = []
                    for i in range(1, rows):
                        row_dict = {}
                        row = table.row_values(i)
                        row_dict.update({"card_number": row[0], "card_secret": row[1], "card_type": row[2],"card_price": int(row[3])})
                        row_info.append(row_dict)
                    result, repeat_str = import_xls_data(row_info)
            except:
                # 数据库存储异常
                return JsonResponse({'msg': '解析excel文件或者数据插入错误！', "code": False})
            if result:
                return JsonResponse({'msg': '上传数据成功！',"code": True})
            else:
                return JsonResponse({'msg': '上传的数据出现重复数据:{}'.format(repeat_str),"code": False})
        else:
            return JsonResponse({'msg': '上传文件类型错误', "code": False})

    return JsonResponse({'msg': '不是post请求', "code": False})


def filter_data(supplier,price,status,card_screen,input_date,start_time,end_time):
    """筛选条件"""
    start_day = start_time + " 00:00:00"
    end_day = end_time + " 23:59:59"
    start_date = Time.str_to_datetime(start_day)
    end_date = Time.str_to_datetime(end_day)

    if card_screen == "card_number" and input_date!="":
        cards = SetCardsClose.objects.filter(card_number=input_date).values()
        return cards
    elif card_screen == "card_secret"and input_date!="":
        cards = SetCardsClose.objects.filter(card_secret=input_date).values()
        return cards
    elif card_screen == "player_id"and input_date!="":
        cards = SetCardsClose.objects.filter(player_id=input_date).values()
        return cards
    elif card_screen == "player_nick"and input_date!="":
        cards = SetCardsClose.objects.filter(player_nick=input_date).values()
        return cards
    elif supplier == "0" and status == "0" and price == "0":
        cards = SetCardsClose.objects.filter(upload_time__range=[start_date, end_date]).values()
        return cards
    elif supplier != "0" and status == "0" and price == "0":
        cards = SetCardsClose.objects.filter(upload_time__range=[start_date, end_date],card_type=supplier).values()
        return cards
    elif supplier == "0" and status != "0" and price == "0":
        cards = SetCardsClose.objects.filter(upload_time__range=[start_date, end_date],change_state=status).values()
        return cards
    elif supplier == "0" and status == "0" and price != "0":
        cards = SetCardsClose.objects.filter(upload_time__range=[start_date, end_date],card_price=price).values()
        return cards
    elif supplier != "0" and status != "0" and price == "0":
        cards = SetCardsClose.objects.filter(upload_time__range=[start_date, end_date],card_type=supplier,change_state=status).values()
        return cards
    elif supplier != "0" and status == "0" and price != "0":
        cards = SetCardsClose.objects.filter(upload_time__range=[start_date, end_date],card_type=supplier,card_price=price).values()
        return cards
    elif supplier == "0" and status != "0" and price != "0":
        cards = SetCardsClose.objects.filter(upload_time__range=[start_date, end_date],change_state=status,card_price=price).values()
        return cards
    elif supplier != "0" and status != "0" and price != "0":
        cards = SetCardsClose.objects.filter(upload_time__range=[start_date, end_date],card_type=supplier,change_state=status,card_price=price).values()
        return cards


def get_cards_info(phone):
    """获取数据库数据"""
    card_list = []
    keys = 'card_secret:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day","end_day","supplier","price","status","card_screen","input_data"])  # 筛选条件
    start_time, end_time, supplier, price, status, card_screen, input_data = result[0], result[1], result[2], result[3], result[4], result[5],result[6]
    def_info = {"start_day": start_time, "end_day": end_time, "supplier": supplier, "price": price,"status": status, "card_screen": card_screen, "input_data": input_data}

    card_data = filter_data(supplier, price, status, card_screen, input_data, start_time, end_time)
    o_rid = 1
    for card in card_data:
        card.update({"orid": o_rid})
        card_list.append(card)
        o_rid = o_rid + 1
    return card_list,def_info

@decorator
def card_secret_xls(request):
    phone = request.session.get('uid')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=card_secret.xls'
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
    sheet.write(0, 1, '上传日期', style)
    sheet.write(0, 2, '卡号', style)
    sheet.write(0, 3, '卡密', style)
    sheet.write(0, 4, '类型', style)
    sheet.write(0, 5, '金额', style)
    sheet.write(0, 6, '商品ID', style)
    sheet.write(0, 7, '兑换玩家ID', style)
    sheet.write(0, 8, '兑换玩家昵称', style)
    sheet.write(0, 9, '兑换玩家手机', style)
    sheet.write(0, 10, '兑换时间', style)

    card_info,data = get_cards_info(phone)
    data_row = 1
    for info in card_info:
        sheet.write(data_row, 0, data_row)
        upload_time = Time.datetime_to_str(info["upload_time"])
        sheet.write(data_row, 1, upload_time)
        sheet.write(data_row, 2, info["card_number"])
        sheet.write(data_row, 3, info["card_secret"])
        sheet.write(data_row, 4, info["card_type"])
        sheet.write(data_row, 5, info["card_price"])
        if info["good_id"]:
            good_id = info["good_id"]
        else:
            good_id = "--"
        sheet.write(data_row, 6, good_id)

        if info["player_id"]:
            uid = info["player_id"]
        else:
            uid = "--"
        sheet.write(data_row, 7, uid)
        if info["player_nick"]:
            nick = info["player_nick"]
        else:
            nick = "--"
        sheet.write(data_row, 8, nick)
        if info["player_phone"]:
            phone = info["player_phone"]
        else:
            phone = "--"
        sheet.write(data_row, 9, phone)
        if info["change_time"]:
            change_time = info["change_time"]
        else:
            change_time = "--"
        sheet.write(data_row, 10, change_time)
        data_row = data_row + 1

    # 写出到IO
    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response


@decorator
def exchange_record_xls(request):
    phone = request.session.get('uid')
    good_list = Shop.shop_filter_name()
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=exchange_record.xls'
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
    sheet.write(0, 1, '兑换ID', style)
    sheet.write(0, 2, '注册渠道', style)
    sheet.write(0, 3, '兑换渠道', style)
    sheet.write(0, 4, '兑换时间|发货时间', style)
    sheet.write(0, 5, '商城类别', style)
    sheet.write(0, 6, '商品ID', style)
    sheet.write(0, 7, '商品类别', style)
    sheet.write(0, 8, '商品名称', style)
    sheet.write(0, 9, '商品单价', style)
    sheet.write(0, 10, '商品成本', style)
    sheet.write(0, 11, '兑换人', style)
    sheet.write(0, 12, '兑换人ID', style)
    sheet.write(0, 13, '期间充值', style)
    sheet.write(0, 14, '充值', style)
    sheet.write(0, 15, '话费券', style)
    sheet.write(0, 16, '发货状态', style)

    exchange_info, _ = get_exchange_record_info(phone)
    data_row = 1
    for info in exchange_info:
        sheet.write(data_row, 0, data_row)
        sheet.write(data_row, 1, info["order_id"])
        sheet.write(data_row, 2, info["channelid"])
        sheet.write(data_row, 3, info.get("pay_channel",0))
        sheet.write(data_row, 4, str(info["start_time"])+'|'+str(info["end_time"]))
        shop = int(info["shop"])
        if shop == 6:
            shop = "限时商城"
        else:
            shop = "白送50元"
        sheet.write(data_row, 5, shop)
        sheet.write(data_row, 6, info["pid"])
        good_type = int(info["good_type"])
        category = ""
        for g_name in good_list:
            if int(g_name["vale"]) == good_type:
                category = g_name["content"]

        sheet.write(data_row, 7, category)
        sheet.write(data_row, 8, info["good_name"])
        money = int(info["buy_type"])
        money_name = ("话费券" if money == -1 else "话费券" if money == 7 else "火龙蛋" if money == 8 else "圣龙蛋" if money == 9 else "冰龙蛋" if money == 10 else "龙舟券")
        sheet.write(data_row, 9, str(info["price"])+"{}".format(money_name))
        sheet.write(data_row, 10, info.get("cost", 0))

        sheet.write(data_row, 11, info["nick"])
        sheet.write(data_row, 12, info["uid"])
        sheet.write(data_row, 13, info["all_pay"])
        sheet.write(data_row, 14, str(info["ali_pay"])+'|'+str(info["weixin_pay"])+'|'+str(info["sdk_pay"])+'|'+str(info["cdkey_pay"]))
        sheet.write(data_row, 15, str(info["in_silver_coupon"])+'|'+str(info["other_coupon"])+'|'+str(info["silver_coupon"]))
        stat = int(info["stat"])
        if stat == 0 or stat == 6 or stat == 7:
            check_status = "未审核"
        elif stat == 1:
            check_status = "未发货"
        else:
            check_status = "已发货"
        sheet.write(data_row, 16, check_status)
        data_row = data_row + 1

    record_data = {"status_type": "导出xls", "info": ""}
    insert_record_data(phone, ExchangeRecord, record_data)
    # 写出到IO
    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response


def create_limit_time_shop(result, channel):
    """插入限时商城数据"""
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d')
    good_id, good_type = result["gid"], result["type"]
    res = LimitInfo.objects.filter(good_id=good_id, channel=channel)
    if not res:
        LimitInfo.objects.create(
            good_id=good_id,
            channel=channel,
            good_type=good_type,
            update_time=insert_time,
            json_data=Context.json_dumps(result),
        )
    else:
        LimitInfo.objects.filter(good_id=good_id, channel=channel).update(
            good_type=good_type,
            json_data=Context.json_dumps(result),
        )


def create_exchange_record(result):
    """插入兑换记录"""
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d')
    record_data = []
    for m_info in result:
        day_time = m_info["start_time"][:10]
        day_stamp = Time.str_to_timestamp(m_info["start_time"])
        channel,order_id,good_type = m_info["channelid"],m_info["order_id"],m_info["good_type"]
        status,pid = m_info["stat"],m_info["pid"]
        res = ExchangeInfo.objects.filter(day_stamp=day_stamp,channel=channel,order_id=order_id)
        if res:
            ExchangeInfo.objects.filter(day_stamp=day_stamp,channel=channel,order_id=order_id).update(
                uid=m_info["uid"],
                nick=m_info["nick"],
                order_id=m_info["order_id"],
                channel=channel,
                status=status,
                good_type = good_type,
                day_time=day_time,
                day_stamp=day_stamp,
                json_data=json.dumps(m_info),
                insert_time=insert_time
            )
        else:
            new_record = ExchangeInfo(
                uid=m_info["uid"],
                nick=m_info["nick"],
                order_id=m_info["order_id"],
                channel=channel,
                status=status,
                good_type=good_type,
                day_time=day_time,
                day_stamp=day_stamp,
                json_data=json.dumps(m_info),
                insert_time=insert_time
            )
            record_data.append(new_record)

        if len(record_data) > 1000:
            ExchangeInfo.objects.bulk_create(record_data)
            record_data = []

    ExchangeInfo.objects.bulk_create(record_data)


def import_xls_data(card_info):
    """插入xls--数据"""
    card_list, card_status, xls_info = [], 1, True
    repeat_str = ""
    for card in card_info:
        card_secret = Prpcrypt.encrypt(str(card["card_secret"]))
        card_number = card["card_number"].encode('utf-8')
        result = SetCardsClose.objects.filter(Q(card_number=card_number) | Q(card_secret=card_secret))
        print("----import_xls-----", result)
        if not result:
            new_cards = SetCardsClose(
                upload_time=datetime.datetime.now(),
                card_number=card_number,
                card_secret=card_secret,
                card_type=card["card_type"].encode('utf-8'),
                card_price=card["card_price"],
            )
            card_list.append(new_cards)
        else:
            repeat_str = "卡号:{}_卡密:{}".format(card_number, card_secret)
            card_status, xls_info = 2, False

    if card_status == 1:
        SetCardsClose.objects.bulk_create(card_list)
        return xls_info, repeat_str
    else:
        return xls_info, repeat_str


def get_exchange_record_info(phone):
    """获取兑换记录"""
    keys = 'shop_exchange:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day","end_day","channel","screen_info","good_style","ship_status","input_data","day_list"])  # 筛选条件
    start_day, end_day,channel,screen_info,good_style,ship_status,input_data,day_list = result[0], result[1], result[2], result[3], result[4], result[5], result[6], eval(result[7])
    def_info = {"start_day": start_day, "end_day": end_day, "channel": channel, "screen_info": screen_info,"good_style": good_style, "ship_status": ship_status, "input_data": input_data}
    start_date = Time.str_to_datetime(start_day, '%Y-%m-%d')
    end_date = Time.str_to_datetime(end_day, '%Y-%m-%d')

    record_data, cost_total = query_redis_data(phone,start_date, end_date, channel, screen_info, good_style, ship_status, input_data,day_list)
    sorted_info = sorted(record_data, key=lambda x: Time.str_to_timestamp(x['start_time']), reverse=True)

    def_info.update({"cost_total":cost_total})
    return sorted_info, def_info


def query_redis_data(phone,start_date,end_date,channel,screen_info,good_style,ship_status,input_data,day_list):
    shop_list = []
    if input_data == "":
        if channel == "0" and good_style == "0" and ship_status == "3":
            res_info = ExchangeInfo.objects.filter(day_time__range=[start_date, end_date]).values('json_data').order_by("day_stamp")
            for every_day in day_list:
                day_record = Context.RedisCache.hget_keys('day_shop_record:{}:{}:*:*'.format(phone, every_day))
                for key in day_record:
                    ret = Context.RedisCache.hash_getall(key)
                    shop_list.append(ret)
        elif channel != "0" and good_style == "0" and ship_status == "3":
            res_info = ExchangeInfo.objects.filter(day_time__range=[start_date, end_date], channel=channel).values('json_data').order_by("day_stamp")

            for every_day in day_list:
                day_record = Context.RedisCache.hget_keys('day_shop_record:{}:{}:*:*'.format(phone, every_day))
                for key in day_record:
                    ret = Context.RedisCache.hash_getall(key)
                    if ret["channelid"].encode('utf-8') == channel:
                        shop_list.append(ret)
                    else:
                        continue
        elif channel == "0" and good_style != "0" and ship_status == "3":
            res_info = ExchangeInfo.objects.filter(day_time__range=[start_date, end_date],good_type=good_style).values('json_data').order_by("day_stamp")
            for every_day in day_list:
                day_record = Context.RedisCache.hget_keys('day_shop_record:{}:{}:*:*'.format(phone, every_day))
                for key in day_record:
                    ret = Context.RedisCache.hash_getall(key)
                    if str(ret["good_type"]) == good_style:
                        shop_list.append(ret)
                    else:
                        continue
        elif channel == "0" and good_style == "0" and ship_status != "3":
            res_info = ExchangeInfo.objects.filter(day_time__range=[start_date, end_date],status=int(ship_status)).values('json_data').order_by("day_stamp")
            for every_day in day_list:
                day_record = Context.RedisCache.hget_keys('day_shop_record:{}:{}:*:*'.format(phone, every_day))
                for key in day_record:
                    ret = Context.RedisCache.hash_getall(key)
                    if str(ret["stat"]) == ship_status:
                        shop_list.append(ret)
                    else:
                        continue
        elif channel != "0" and good_style != "0" and ship_status == "3":
            res_info = ExchangeInfo.objects.filter(day_time__range=[start_date, end_date], channel=channel,good_type=good_style).values('json_data').order_by("day_stamp")
            for every_day in day_list:
                day_record = Context.RedisCache.hget_keys('day_shop_record:{}:{}:*:*'.format(phone, every_day))
                for key in day_record:
                    ret = Context.RedisCache.hash_getall(key)
                    if str(ret["good_type"]) == good_style and ret["channelid"].encode('utf-8') == channel:
                        shop_list.append(ret)
                    else:
                        continue
        elif channel != "0" and good_style == "0" and ship_status != "3":
            res_info = ExchangeInfo.objects.filter(day_time__range=[start_date, end_date], channel=channel,status=int(ship_status)).values('json_data').order_by("day_stamp")
            for every_day in day_list:
                day_record = Context.RedisCache.hget_keys('day_shop_record:{}:{}:*:*'.format(phone, every_day))
                for key in day_record:
                    ret = Context.RedisCache.hash_getall(key)
                    if str(ret["stat"]) == ship_status and ret["channelid"].encode('utf-8') == channel:
                        shop_list.append(ret)
                    else:
                        continue
        elif channel == "0" and good_style != "0" and ship_status != "3":
            res_info = ExchangeInfo.objects.filter(day_time__range=[start_date, end_date], good_type=good_style,status=int(ship_status)).values('json_data').order_by("day_stamp")
            for every_day in day_list:
                day_record = Context.RedisCache.hget_keys('day_shop_record:{}:{}:*:*'.format(phone, every_day))
                for key in day_record:
                    ret = Context.RedisCache.hash_getall(key)
                    if str(ret["good_type"]) == good_style and str(ret["stat"]) == ship_status:
                        shop_list.append(ret)
                    else:
                        continue
        else:
            res_info = ExchangeInfo.objects.filter(day_time__range=[start_date, end_date], channel=channel, good_type=good_style, status=int(ship_status)).values('json_data').order_by("day_stamp")
            for every_day in day_list:
                day_record = Context.RedisCache.hget_keys('day_shop_record:{}:{}:*:*'.format(phone, every_day))
                for key in day_record:
                    ret = Context.RedisCache.hash_getall(key)
                    if str(ret["good_type"]) == good_style and ret["channelid"].encode('utf-8') == channel and str(ret["stat"]) == ship_status:
                        shop_list.append(ret)
                    else:
                        continue
    else:
        if screen_info == "uid":
            res_info = ExchangeInfo.objects.filter(uid=input_data).values('json_data').order_by("day_stamp")
            for every_day in day_list:
                day_record = Context.RedisCache.hget_keys('day_shop_record:{}:{}:*:*'.format(phone, every_day))
                for key in day_record:
                    ret = Context.RedisCache.hash_getall(key)
                    if str(ret["uid"]) == input_data:
                        shop_list.append(ret)
                    else:
                        continue
        else:
            res_info = ExchangeInfo.objects.filter(nick=input_data).values('json_data').order_by("day_stamp")
            for every_day in day_list:
                day_record = Context.RedisCache.hget_keys('day_shop_record:{}:{}:*:*'.format(phone, every_day))
                for key in day_record:
                    ret = Context.RedisCache.hash_getall(key)
                    if str(ret["nick"]) == input_data:
                        shop_list.append(ret)
                    else:
                        continue
    record_list = []
    for date in res_info:
        json_data = json.loads(date['json_data'])
        json_data["stat"] = int(json_data["stat"])
        json_data["good_type"] = str(json_data["good_type"])
        record_list.append(json_data)
    record_list.extend(shop_list)

    record_data, cost_total = [], 0
    for info in record_list:
        shop_type, stat, good_type = int(info.get("shop", 0)), int(info.get("stat", 0)), str(info.get("good_type", 0))
        info.update({"shop": shop_type, "stat": stat, "good_type": good_type})
        if stat == 2 and (good_type != 3 or good_type != 5):
            cost_total += float(info.get("cost", 0))
        record_data.append(info)

    sorted_info = sorted(record_data, key=lambda x: Time.str_to_timestamp(x['start_time']), reverse=True)
    return sorted_info, cost_total

# ==========================兑换详情==============================
@decorator
def shop_exchange_details(request):
    """商城管理--兑换详情"""
    if request.method == "GET":
        url = '/v2/shell/get_shop_tips'
        context = {}
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)
        gift = Context.json_loads(ret.content)
        if "ret" not in gift:
            return render(request, 'limit_time_shop/shop_exchange_details.html', {"info_dict": {}})
        else:
            recharge = gift["ret"]
            del recharge['0']
            del recharge['1000']
            return render(request, 'limit_time_shop/shop_exchange_details.html', {"info_dict": recharge})
    else:
        dic = request.POST
        channel_info = dic.getlist("channel")
        data_info = dic.getlist("in_data")
        old_data = ChannelList.objects.all().values('channel_data').first()
        chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道

        gift_info = {}
        for channel, info in zip(channel_info, data_info):
            new_channel = channel
            for key, value in chanel_info.items():
                if str(channel) == str(value):
                    new_channel = key
                else:
                    continue
            gift_info.update({new_channel: info})

        url = "/v2/shell/modify_shop_tips"
        context = {'ret': gift_info}
        context.update({"phone": request.session.get('uid')})
        ret = Context.Controller.request(url, context)

        if ret.status_code == 200:
            code = True
            msg = "兑换详情设置成功！"
        else:
            code = True
            msg = "兑换详情设置失败！"
        return JsonResponse({'code': code, 'msg': msg})


def insert_record_data(phone, Record, record_data):
    """操作记录"""
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    Record.objects.create(
        insert_time=insert_time,
        login_user=phone,
        record_data=Context.json_dumps(record_data),
    )


# @decorator
# def gift_total(request):
#     old_data = ChannelList.objects.all().values('channel_data').first()
#     chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
#     del chanel_info['1000']
#     day_time = datetime.date.today().strftime('%Y-%m-%d')
#     gift_info = []
#     gift_list = GiftInfo.objects.values("gift_id")[0:]
#     for gift in gift_list:
#         gift_id = gift.get("gift_id", 0).encode('utf-8')
#         gift_info.append(gift_id)
#
#     return render(request, 'limit_time_shop/gift_bag_total.html', {"chanel_info": chanel_info, "start_day": day_time, "end_day": day_time})
#
#
# @decorator
# def exchange_total(request):
#     old_data = ChannelList.objects.all().values('channel_data').first()
#     chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
#     del chanel_info['1000']
#     day_time = datetime.date.today().strftime('%Y-%m-%d')
#
#     return render(request, 'limit_time_shop/exchange_total.html', {"chanel_info": chanel_info, "start_day": day_time, "end_day": day_time})


@decorator
def All_record(request):
    """兑换记录--操作记录"""
    url_date = "/limit_time_shop/shop_all_record/"
    index, number = 1, 1
    dic = request.GET
    pid = dic.get('pid').encode('utf-8')
    one_page = dic.get('page')
    if pid == "exchange_record":
        result_list = ExchangeRecord.objects.all().values("insert_time", "login_user", "record_data").order_by("-insert_time")
    else:
        result_list = LimitRecord.objects.all().values("insert_time", "login_user", "record_data").order_by("-insert_time")
    if one_page:
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

    record_info = {'page': page, 'pid': pid, "number": number, "url_date": url_date}
    return render(request, 'record/{}.html'.format(pid), record_info)


def error(request):
    return render(request, 'all.html')

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








