# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.shortcuts import render
from django.core.paginator import Paginator
from login_manage.views import decorator
from util.context import Context
from login_manage.models import *
from control_manage.models import Account
from gift_bag_shop.models import GiftInfo
from util.gamedate import *
from xlwt import *
from io import BytesIO
from util.process import ProcessInfo
from django.http import HttpResponse, JsonResponse
from util.tool import Time
from .models import *
from util.Tips_show import Tips
import re


@decorator
def channel_total(request):
    phone, number = request.session.get('uid'), 1
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    req_url = "/currency_total/channel_total/"
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page:
            conf, resp_info = get_redis_channel(phone)
            pages = int(one_page.encode('utf-8'))
            number, index = pages, pages
            paginator = Paginator(conf, 30)
            page, plist = Context.paging(paginator, index)
            num_page = paginator.num_pages
            if pages > num_page:
                number = num_page
            resp_info.update({"number": number, "page": page})
        else:
            end_day = datetime.date.today().strftime('%Y-%m-%d')
            resp_info = {"channel": "0", "start_day": end_day, "end_day": end_day, "number": number, "page": []}
    else:
        dic = request.POST
        channel = dic.get('channel').encode('utf-8')
        start_time = dic.get("start_time").encode('utf-8')[:10]
        end_time = dic.get("stop_time").encode('utf-8')[:10]

        start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')

        day_list = []
        while start_date <= end_date:
            res = ChannelTotal.objects.filter(day_time=start_date).first()
            every_day = Time.datetime_to_str(start_date, '%Y-%m-%d')
            if res:
                start_date = Time.next_days(start_date)
                continue
            else:
                day_order = Context.RedisCache.hget_keys('channel_total:{}:{}:*'.format(phone, every_day))
                if day_order:
                    day_list.append(every_day)
                    if every_day == datetime.datetime.now().strftime('%Y-%m-%d'):
                        insert_redis_relax_total(phone, every_day, every_day)  # 插入数据
                    else:
                        start_date = Time.next_days(start_date)
                        continue
                else:
                    day_list.append(every_day)
                    insert_redis_relax_total(phone, every_day, every_day)  # 插入数据
            start_date = Time.next_days(start_date)

        resp_info = {"start_day": start_time, "end_day": end_time, "channel": channel, "day_list": day_list}
        keys = 'channel_total:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, resp_info)

        result_info = get_insert_redis_info(phone, start_time, end_time, channel, day_list)
        paginator = Paginator(result_info, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        resp_info.update({"page": page, "number": number})

    resp_info.update({"chanel_info": chanel_info, "url_date": req_url})
    return render(request, "currency_total/channel_total.html", resp_info)


def insert_redis_relax_total(phone, start_time, end_time):
    url = '/v2/shell/gm/query/channel_everyday_info'
    context = {"start": start_time, "end": end_time}
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.text)

    if "stat" not in config:
        return 0
    else:
        result = config["stat"]
        for day_time, day_info in result.items():
            for channel_info in day_info:
                for chanel_id, info in channel_info.items():
                    info.update({"channel": chanel_id})
                    Context.RedisCache.hash_mset('channel_total:{}:{}:{}'.format(phone, day_time, chanel_id), info)


def get_insert_redis_info(phone, start_time, end_time, channel, day_list):
    sort_info, total_list, number = [], [], 1
    if channel == '0':
        res_info = ChannelTotal.objects.filter(day_time__range=(start_time, end_time)).values('json_data').order_by("-day_time")
        total_list = get_deal_redis_data(phone, day_list, channel)
    else:
        res_info = ChannelTotal.objects.filter(day_time__range=(start_time, end_time), channel=channel).values('json_data').order_by("-day_time")
        total_list = get_deal_redis_data(phone, day_list, channel)

    all_new_user = 0
    for info in res_info:
        new_data = {}
        data = Context.json_loads(info.get("json_data"))
        all_new_user += int(data.get("new_user_count", 0))
        new_data.update({"all_new_user": all_new_user})
        new_data.update(data)
        sort_info.append(new_data)
    if sort_info:
        sort_info.extend(total_list)
        result_info = sorted(sort_info, key=lambda x: Time.str_to_timestamp(x["day_time"], '%Y-%m-%d'), reverse=True)
    else:
        result_info = sorted(total_list, key=lambda x: Time.str_to_timestamp(x["day_time"], '%Y-%m-%d'), reverse=True)
    return result_info


def get_deal_redis_data(phone, every_list, channel):
    day_list = []
    for every_day in every_list:
        all_total = {}
        day_order = Context.RedisCache.hget_keys('channel_total:{}:{}:*'.format(phone, every_day))
        for keys in day_order:
            day_info = {}
            result = Context.RedisCache.hash_getall(keys)
            channel_id = str(result['channel'])
            print("-----channel_id------", channel_id, channel)

            one_channel = deal_channel_data(result, channel_id, every_day)
            day_info.update(one_channel)
            day_list.append(day_info)

            # 全渠道计算
            for keys, values in day_info.items():
                if keys != 'day_time' and keys != 'channel' and keys != 'pay_total_popup' and keys != 'coin_award_rate' and keys != 'power_award_rate' and keys != 'day_in_power_pop' and keys != 'day_out_power_pop' \
                        and keys != 'in_silver_coupon_pop' and keys != 'out_silver_coupon_pop' and keys != 'in_props_701_pop' and keys != 'in_props_702_pop' and keys != 'in_props_703_pop' and keys != 'in_props_704_pop' \
                        and keys != 'day_in_power_pop' and keys != 'day_out_power_pop' and keys != 'out_props_701_pop' and keys != 'out_props_702_pop' and keys != 'out_props_703_pop' and keys != 'out_props_704_pop':
                    all_total.update({keys: int(all_total.get(keys, 0)) + int(values)})

            all_pay_total = int(all_total['all_pay_total'])
            pay_total_popup = Tips.get_pay_popup(all_total, all_pay_total)
            all_total.update({"pay_total_popup": pay_total_popup})

            chip_price = (float(all_total["in_props_701"]) / 2) + (float(all_total["in_props_702"]) * 10 / 2) + (
                    float(all_total["in_props_703"]) * 50 / 2) + (float(all_total["in_props_704"]) * 100 / 2)
            all_silver_coupon = all_total["in_silver_coupon"]
            silver_coupon_price = float(all_silver_coupon) / 100
            if all_pay_total == 0:
                coin_award_rate = 0
            else:
                coin_award_rate = round((chip_price + silver_coupon_price) / all_pay_total, 2)
            # 鸟蛋场当日出奖率=(当前剩余鸟蛋+今日兑出鸟蛋)/(昨日剩余鸟蛋+ 当日兑入鸟蛋)

            power_price = int(all_total["last_surplus_power"]) + int(all_total["day_exchange_in"])
            if power_price == 0:
                power_award_rate = 0
            else:
                power_award_rate = round(
                    ((int(all_total["surplus_power"]) + int(all_total["day_exchange_out"])) / float(power_price)), 2)
            all_total.update({"coin_award_rate": coin_award_rate, "power_award_rate": power_award_rate})

            in_silver_coupon, out_silver_coupon = all_total['in_silver_coupon'], all_total['out_silver_coupon']
            in_silver_coupon_popup = Tips.get_in_silver_coupon_popup(all_total, in_silver_coupon)
            out_silver_coupon_popup = Tips.get_out_silver_coupon_popup(all_total, out_silver_coupon)
            # 今日消耗 =（昨日剩余 + 今日产出 - 今日剩余）

            all_total.update(
                {"in_silver_coupon_pop": in_silver_coupon_popup, "out_silver_coupon_pop": out_silver_coupon_popup})
            in_props_701, in_props_702 = all_total['in_props_701'], all_total['in_props_702']
            in_props_703, in_props_704 = all_total['in_props_703'], all_total['in_props_704']
            in_props_701_popup = Tips.get_in_props_701_popup(all_total, in_props_701)
            in_props_702_popup = Tips.get_in_props_702_popup(all_total, in_props_702)
            in_props_703_popup = Tips.get_in_props_703_popup(all_total, in_props_703)
            in_props_704_popup = Tips.get_in_props_704_popup(all_total, in_props_704)

            all_total.update({"in_props_701_pop": in_props_701_popup, "in_props_702_pop": in_props_702_popup,
                              "in_props_703_pop": in_props_703_popup, "in_props_704_pop": in_props_704_popup})

            out_props_701, out_props_702 = all_total['out_props_701'], all_total['out_props_702']
            out_props_703, out_props_704 = all_total['out_props_703'], all_total['out_props_704']
            out_props_701_popup = Tips.get_out_props_701_popup(all_total, out_props_701)
            out_props_702_popup = Tips.get_out_props_702_popup(all_total, out_props_702)
            out_props_703_popup = Tips.get_out_props_703_popup(all_total, out_props_703)
            out_props_704_popup = Tips.get_out_props_704_popup(all_total, out_props_704)

            all_total.update({"out_props_701_pop": out_props_701_popup, "out_props_702_pop": out_props_702_popup,
                              "out_props_703_pop": out_props_703_popup, "out_props_704_pop": out_props_704_popup,
                              "out_props_701": out_props_701, "out_props_702": out_props_702,
                              "out_props_703": out_props_703, "out_props_704": out_props_704})

            day_in_power, day_out_power = all_total['day_in_power'], all_total['day_out_power']
            day_in_power_popup = Tips.get_in_power_popup(all_total, day_in_power)
            day_out_power_popup = Tips.get_out_power_popup(all_total, day_out_power)
            all_total.update({"day_in_power_pop": day_in_power_popup, "day_out_power_pop": day_out_power_popup})
            all_total.update({"day_time": every_day, "channel": "1000"})

        if len(all_total) > 1:
            day_list.append(all_total)
        else:
            continue

    if channel == "0":
        channel_list = day_list
    else:
        channel_list = []
        if channel == "1000":
            for chl in day_list:
                chl_id = chl["channel"]
                if channel == chl_id:
                    channel_list.append(chl)
                else:
                    continue
        else:
            for chl in day_list:
                chl_id = chl["channel"]
                if channel == chl_id:
                    channel_list.append(chl)
                else:
                    continue
    return channel_list


def deal_channel_data(result, channel_id, every_day):
    day_info = {}
    day_pay_total, day_in_power_pop, day_out_power_pop = {}, {}, {}
    weixin, alipay, sdk_pay, cdkey_pay, gm_pay, day_in_power, day_out_power = 0, 0, 0, 0, 0, 0, 0
    in_silver_coupon, out_silver_coupon = 0, 0
    in_props_701, out_props_701, in_props_702, out_props_702 = 0, 0, 0, 0
    in_props_703, out_props_703, in_props_704, out_props_704 = 0, 0, 0, 0
    day_exchange_in, day_exchange_out = 0, 0
    for key, value in result.items():
        # 微信
        if key.startswith('{}.weixin_pay.user.pay_total'.format(channel_id)):
            weixin = int(value)

        # 支付宝
        elif key.startswith('{}.ali_pay.user.pay_total'.format(channel_id)):
            alipay = int(value)

        # 兑换码
        elif key.startswith('{}.cdkey_pay.user.pay_total'.format(channel_id)):
            cdkey_pay = int(value)

        # sdk
        elif key.startswith('{}.sdk_pay.user.pay_total'.format(channel_id)):
            sdk_pay = int(value)

        # gm充值额度
        elif key.startswith('{}.gm_pay.user.pay_total'.format(channel_id)):
            gm_pay = int(value)

        # 当日话费券产出
        elif key.startswith('in.silver_coupon.'):
            day_info[key] = int(day_info.get(key, 0)) + int(value)
            in_silver_coupon += int(value)

        # 当日话费券消耗
        elif key.startswith('out.silver_coupon.'):
            day_info[key] = int(day_info.get(key, 0)) + int(value)
            out_silver_coupon += int(value)

        # 金币场龙蛋产出
        if key.startswith('in.props.701.') or key.startswith('in.props.1701.'):
            day_info[key] = int(day_info.get(key, 0)) + int(value)
            in_props_701 += int(value)

        if key.startswith('in.props.702.') or key.startswith('in.props.1702.'):
            day_info[key] = int(day_info.get(key, 0)) + int(value)
            in_props_702 += int(value)

        if key.startswith('in.props.703.') or key.startswith('in.props.1703.'):
            day_info[key] = int(day_info.get(key, 0)) + int(value)
            in_props_703 += int(value)

        if key.startswith('in.props.704.') or key.startswith('in.props.1704.'):
            day_info[key] = int(day_info.get(key, 0)) + int(value)
            in_props_704 += int(value)

        # 金币场-龙蛋消耗
        if key.startswith('out.props.701.') or key.startswith('out.props.1701.'):
            day_info[key] = int(day_info.get(key, 0)) + -int(value)
            out_props_701 += -int(value)
        if key.startswith('out.props.702.') or key.startswith('out.props.1702.'):
            day_info[key] = int(day_info.get(key, 0)) + -int(value)
            out_props_702 += -int(value)
        if key.startswith('out.props.703.') or key.startswith('out.props.1703.'):
            day_info[key] = int(day_info.get(key, 0)) + -int(value)
            out_props_703 += -int(value)
        if key.startswith('out.props.704.') or key.startswith('out.props.1704.'):
            day_info[key] = int(day_info.get(key, 0)) + -int(value)
            out_props_704 += -int(value)

        # 当日产出鸟蛋
        if key.startswith('in.power.') and not key.startswith("in.power.power.shot.703.exchange") \
                and not key.startswith("in.power.power.shot.704.exchange") and not key.startswith("in.power.catch.bird."):
            day_info[key] = int(day_info.get(key, 0)) + int(value)
            day_in_power += int(value)

        # 当天兑入鸟蛋
        if key.startswith('in.power.power.shot.703.exchange') or key.startswith(
                'in.power.power.shot.704.exchange'):
            day_exchange_in += int(value)

        # 当天兑出鸟蛋
        if key.startswith('out.power.power.shot.703.exchange') \
                or key.startswith('out.power.power.shot.704.exchange'):
            day_exchange_out += int(value)

        # 当日鸟蛋产出
        if key.startswith('in.power.'):
            if not key.startswith('in.power.catch.bird.400') and not key.startswith('in.power.catch.bird.401') and not \
                    key.startswith('in.power.catch.bird.402') and not key.startswith('in.power.catch.bird.403') and \
                    not key.startswith("in.power.power.shot.703.exchange") and not key.startswith("in.power.power.shot.704.exchange"):
                day_info[key] = int(day_info.get(key, 0)) + int(value)
                day_in_power += int(value)

        # 洗码量
        if key.startswith('out.power.game.shot.bullet.400') or key.startswith('out.power.game.shot.bullet.401') \
                or key.startswith('out.power.game.shot.bullet.402') or key.startswith('out.power.game.shot.bullet.403'):
            day_info[key] = int(day_info.get(key, 0)) + int(value)
            day_out_power += int(value)

    surplus_silver_coupon, surplus_props_701, surplus_props_702 = result.get("server_silver_coupon", 0), result.get("server_props_701", 0), result.get("server_props_702", 0)
    surplus_props_703, surplus_props_704, surplus_power, last_surplus_power = result.get("server_props_703", 0), result.get("server_props_704", 0), result.get("server_power", 0), result["last_power"]
    relax_bonus_consume, power_bonus_consume = result.get("use_relax_bonus_consume", 0), result.get("use_power_bonus_consume", 0)
    day_info.update({"surplus_silver_coupon": surplus_silver_coupon, "surplus_props_701": surplus_props_701, "surplus_props_702": surplus_props_702,
                     "surplus_props_703": surplus_props_703, "surplus_props_704": surplus_props_704, "surplus_power": surplus_power, "last_surplus_power": last_surplus_power,
                     "relax_bonus_consume": relax_bonus_consume, "power_bonus_consume": power_bonus_consume
                     })

    day_pay_total.update({"weixin_pay_total": weixin, "ali_pay_total": alipay, "sdk_pay_total": sdk_pay, "gm_pay_total": gm_pay, "cdkey_pay_total": cdkey_pay})
    all_pay_total = weixin + alipay + sdk_pay + gm_pay + cdkey_pay
    pay_total_popup = Tips.get_pay_popup(day_pay_total, all_pay_total)
    day_info.update({"all_pay_total": all_pay_total, "pay_total_popup": pay_total_popup})

    # 金币场当日出奖率=((当日产出毒龙蛋*1/2)+(冰龙蛋*10/2)+(火龙蛋*50/2)+(圣龙蛋*100/2) + 当日话费券产出/100)/当日充值
    chip_price = (float(in_props_701) / 2) + (float(in_props_702) * 10 / 2) + (float(in_props_703) * 50 / 2) + (float(in_props_704) * 100 / 2)
    silver_coupon_price = float(in_silver_coupon) / 100
    if all_pay_total == 0:
        coin_award_rate = 0
    else:
        coin_award_rate = round((chip_price + silver_coupon_price) / all_pay_total, 2)
    # 鸟蛋场当日出奖率=(当前剩余鸟蛋+今日兑出鸟蛋)/(昨日剩余鸟蛋+ 当日兑入鸟蛋)
    power_price = int(result["last_power"]) + day_exchange_in
    if power_price == 0:
        power_award_rate = 0
    else:
        power_award_rate = round(((int(surplus_power) + day_exchange_out) / float(power_price)), 2)
    day_info.update({"coin_award_rate": coin_award_rate, "power_award_rate": power_award_rate})

    in_silver_coupon_popup = Tips.get_in_silver_coupon_popup(day_info, in_silver_coupon)
    out_silver_coupon_popup = Tips.get_out_silver_coupon_popup(day_info, out_silver_coupon)
    # 今日消耗 =（昨日剩余 + 今日产出 - 今日剩余）

    day_info.update({"in_silver_coupon": in_silver_coupon, "out_silver_coupon": out_silver_coupon,
                     "in_silver_coupon_pop": in_silver_coupon_popup, "out_silver_coupon_pop": out_silver_coupon_popup})

    in_props_701_popup = Tips.get_in_props_701_popup(day_info, in_props_701)
    in_props_702_popup = Tips.get_in_props_702_popup(day_info, in_props_702)
    in_props_703_popup = Tips.get_in_props_703_popup(day_info, in_props_703)
    in_props_704_popup = Tips.get_in_props_704_popup(day_info, in_props_704)

    day_info.update({"in_props_701_pop": in_props_701_popup, "in_props_702_pop": in_props_702_popup,
                     "in_props_703_pop": in_props_703_popup, "in_props_704_pop": in_props_704_popup,
                     "in_props_701": in_props_701, "in_props_702": in_props_702,
                     "in_props_703": in_props_703, "in_props_704": in_props_704})

    out_props_701_popup = Tips.get_out_props_701_popup(day_info, out_props_701)
    out_props_702_popup = Tips.get_out_props_702_popup(day_info, out_props_702)
    out_props_703_popup = Tips.get_out_props_703_popup(day_info, out_props_703)
    out_props_704_popup = Tips.get_out_props_704_popup(day_info, out_props_704)

    day_info.update({"out_props_701_pop": out_props_701_popup, "out_props_702_pop": out_props_702_popup,
                     "out_props_703_pop": out_props_703_popup, "out_props_704_pop": out_props_704_popup,
                     "out_props_701": out_props_701, "out_props_702": out_props_702,
                     "out_props_703": out_props_703, "out_props_704": out_props_704})

    day_info.update({"day_exchange_in": day_exchange_in, "day_exchange_out": day_exchange_out})
    day_in_power_popup = Tips.get_in_power_popup(day_info, day_in_power)

    day_out_power_popup = Tips.get_out_power_popup(day_info, day_out_power)
    day_info.update({"day_in_power": day_in_power, "day_in_power_pop": day_in_power_popup,
                     "day_out_power_pop": day_out_power_popup, "day_out_power": day_out_power})

    # 鸟蛋场抽水(收益) = 洗码量 * 千分之五 0.005
    # power_yield = day_out_power * 0.005
    day_info.update({"day_time": every_day, "channel": channel_id})
    return day_info


def get_redis_channel(phone):
    """"""
    keys = 'channel_total:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day", "channel", "day_list"])  # 筛选条件
    start_time, end_time, channel, day_list = result[0], result[1], result[2], eval(result[3])
    config = get_insert_redis_info(phone, start_time, end_time, channel, day_list)

    def_info = {"start_day": start_time, "end_day": end_time, "channel": channel}
    return config, def_info


def insert_coupon_rate(phone, day_time):
    url = '/v2/shell/gm/calc/out_coupon_rate'
    context = {"day_time": day_time}
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    coin_conf = Context.json_loads(ret.text)
    if "ret" not in coin_conf:
        msg = False
    else:
        config_info = coin_conf["ret"]
        if not config_info:
            msg = False
        else:
            for info in config_info:
                for channel, values in info.items():
                    (fmt, user_info), = values.items()
                    (uid, data), = user_info.items()
                    keys = 'user_daily:%s:%s:%s' % (channel, fmt, uid)
                    if data:
                        Context.RedisCache.hash_mset(keys, data)
                    else:
                        continue
            msg = True
    return msg


def insert_period_total(start, end):
    url = '/v2/shell/gm/redis/get_server_data'
    user_id = Context.RedisCluster.hash_get('global.info.hash', 'max.user.id')
    print("----------user_id77", user_id)
    if user_id:
        context = {"start": start, "end": end, "uid": user_id}
    else:
        context = {"start": start, "end": end}
    context.update({"phone": "system"})
    ret = Context.Controller.request(url, context)
    coin_conf = Context.json_loads(ret.text)
    if "stat" not in coin_conf or "game" not in coin_conf or "user" not in coin_conf or "max_user" not in coin_conf:
        return 0
    else:
        gid = 2
        stat_info,game_info,user_info,max_user = coin_conf["stat"],coin_conf["game"],coin_conf["user"],coin_conf["max_user"]
        for stat in stat_info:
            for chanel,info in stat.items():
                keys = 'stat:%s:%s' % (chanel, info["day_time"])
                if info:
                    Context.RedisCache.hash_mset(keys, info)
                else:
                    continue
        for game, user in zip(game_info, user_info):
            for uid, g_info in game.items():
                keys = 'game:%s:%s' % (gid, uid)
                if g_info:
                    Context.RedisMix.hash_mset(keys, g_info)
                else:
                    continue

            for uid, u_info in user.items():
                keys = 'user:{}'.format(uid)
                if u_info:
                    Context.RedisMix.hash_mset(keys, u_info)
                else:
                    continue

        Context.RedisCluster.hash_set('global.info.hash', 'max.user.id', max_user)


@decorator
def pay_total(request):
    """付费数据统计"""
    phone, index, number = request.session.get('uid'), 1, 1
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    hide_product = ["100900","100901","100902","100903","100904","100905","100906","100907","100908","100909","100910","100911","100601","100602","100603","100604","101111","101112","101113","101114"]
    del chanel_info['1000']
    product_list = ProductList.objects.all().values('product_id', 'product_data')
    good_info = {"0": "全部"}
    for product in product_list:
        product_id = str(product.get("product_id"))
        good_name = Context.json_loads(product['product_data'])["name"]
        if product_id not in hide_product:
            good_info[product_id] = good_name
    gift_list = GiftInfo.objects.all().values('gift_id','gift_name')
    for gift in gift_list:
        gift_id = str(gift.get("gift_id"))
        gift_name = gift.get("gift_name")
        good_info[gift_id] = gift_name

    url_date = "/currency_total/pay_total/"
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page:
            conf, day_info = get_pay_period(phone)
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
            day_info = {"start_day": day_time, "end_day": day_time, "number": number, "page": []}
    else:
        dic = request.POST
        start_time = dic.get("start_time")[:10]
        end_time = dic.get("stop_time")[:10]
        channel = dic.get("channel").encode('utf-8')
        good_name = dic.get("good").encode('utf-8')

        good_list = []
        if good_name == "0":
            for good_id, value in good_info.items():
                if len(good_id) > 5:
                    good_list.append(good_id)
                else:
                    continue
        else:
            good_list.append(good_name)

        day_info = {"start_day": start_time, "end_day": end_time, "channel": channel, "good_list": good_list}
        keys = 'pay_total_period:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, day_info)

        good_len = len(good_list)
        if good_len > 2:
            good_name = "0"
        else:
            good_name = good_list[0]
        insert_pay_total(phone, start_time, end_time, good_list)  # 插入数据
        start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')
        if channel == "0":
            if good_len > 2:
                res_info = PayTotal.objects.filter(day_time__range=[start_date, end_date]).values('json_data').order_by("day_time")
            else:
                good_id = good_list[0]
                res_info = PayTotal.objects.filter(day_time__range=[start_date, end_date], good_id=good_id).values('json_data').order_by("day_time")
        else:
            if good_len > 2:
                res_info = PayTotal.objects.filter(day_time__range=[start_date, end_date], channel=channel).values('json_data').order_by("day_time")
            else:
                good_id = good_list[0]
                res_info = PayTotal.objects.filter(day_time__range=[start_date, end_date], channel=channel,good_id=good_id).values('json_data').order_by("day_time")

        pay_list = []
        for r_data in res_info:
            gift_info = Context.json_loads(r_data.get("json_data"))
            pay_list.append(gift_info)

        paginator = Paginator(pay_list, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        day_info.update({'page': page, "url_date": url_date, "number": number, "good_name": good_name})
    day_info.update({"good_info": good_info,"chanel_info": chanel_info, "url_date": url_date})
    return render(request, 'currency_total/pay_total.html', day_info)


def insert_pay_total(phone, start_day, end_day, good_list):
    url = '/v2/shell/gm/query/pay_period_data'
    context = {"start": start_day, "end": end_day, "good_list": good_list}
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    ret_dict = Context.json_loads(ret.text)
    if "pay_data" not in ret_dict:
        return 0
    else:
        gift_list, pay_list = [], []
        result = ret_dict["pay_data"]
        for gift in result:
            pay_info = {}
            for day_time, good_info in gift.items():
                for channel, order_info in good_info.items():
                    if not pay_info.has_key(channel):
                        pay_info[channel] = {}

                    for key, value in order_info.items():
                        product_id = value.get("productId")
                        cost = int(float(value.get("cost")))
                        good_name = ProcessInfo.verify_productId(product_id, cost)
                        if not pay_info[channel].has_key(product_id):
                            pay_info[channel][product_id] = {"day_time": day_time, "channel": channel,"good_id": product_id,"good_name": good_name, "cost": cost, "pay_time": 0, "pay_sum": 0}
                        pay_status = int(value.get("state"))
                        if pay_status == 6:
                            pay_info[channel][product_id]["pay_time"] = int(pay_info[channel][product_id].get("pay_time", 0)) + 1
                            pay_info[channel][product_id]["pay_sum"] = int(pay_info[channel][product_id].get("pay_sum", 0)) + cost
            gift_list.append(pay_info)

        for info in gift_list:
            for channel, good_data in info.items():
                for keys, values in good_data.items():
                    pay_list.append(values)

        create_pay_data_total(pay_list)


def create_pay_data_total(pay_list):
    # PayTotal.objects.all().delete()
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d')
    play_data = []
    for m_info in pay_list:
        day_time = m_info["day_time"]
        good_id = m_info["good_id"]
        channel = m_info["channel"]
        res = PayTotal.objects.filter(day_time=day_time, channel=channel, good_id=good_id).first()
        if res:
            PayTotal.objects.filter(day_time=day_time, channel=channel, good_id=good_id).update(
                day_time=day_time,
                insert_time=insert_time,
                channel=channel,
                good_id=good_id,
                json_data=Context.json_dumps(m_info),
            )
        else:
            new_player = PayTotal(
                day_time=day_time,
                insert_time=insert_time,
                channel=channel,
                good_id=good_id,
                json_data=Context.json_dumps(m_info),
            )
            play_data.append(new_player)

        if len(play_data) > 1000:
            PayTotal.objects.bulk_create(play_data)
            play_data = []

    PayTotal.objects.bulk_create(play_data)


def get_pay_period(phone):
    """获取数据"""
    keys = 'pay_total_period:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day", "channel", "good_list"])  # 筛选条件
    start_time, end_time, channel, good_list = result[0], result[1], result[2], eval(result[3])

    good_len = len(good_list)
    if good_len > 2:
        good_name = "0"
    else:
        good_name = good_list[0]
    def_time = {"start_day": start_time, "end_day": end_time, "channel": channel, "good_name":good_name}
    conf_info = []
    start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
    end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')
    if channel == "0":
        if good_len> 2:
            res_info = PayTotal.objects.filter(day_time__range=[start_date, end_date]).values('json_data').order_by("day_time")
        else:
            good_id = good_list[0]
            res_info = PayTotal.objects.filter(day_time__range=[start_date, end_date], good_id=good_id).values('json_data').order_by("day_time")
    else:
        if good_len> 2:
            res_info = PayTotal.objects.filter(day_time__range=[start_date, end_date], channel=channel).values('json_data').order_by("day_time")
        else:
            good_id = good_list[0]
            res_info = PayTotal.objects.filter(day_time__range=[start_date, end_date], channel=channel, good_id=good_id).values('json_data').order_by("day_time")

    for r_data in res_info:
        gift_info = Context.json_loads(r_data.get("json_data"))
        conf_info.append(gift_info)
    return conf_info, def_time


@decorator
def times_total(request):
    """时段数据统计"""
    phone, index, number = request.session.get('uid'), 1, 1
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    times_period = Data_Info.get_times_total()
    url_date = "/currency_total/times_total/"
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page:
            conf, day_info = get_times_period(phone)
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
            day_info = {"start_day": day_time, "end_day": day_time, "number": number, "page": [], "query_info": "online"}
    else:
        dic = request.POST
        start_time = dic.get("start_time")[:10]
        end_time = dic.get("stop_time")[:10]
        channel = dic.get("channel").encode('utf-8')
        query_info = dic.get("query_info").encode('utf-8')

        day_info = {"start_day": start_time, "end_day": end_time, "channel": channel, "query_info": query_info}
        keys = 'times_total_period:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, day_info)

        times_list = []
        insert_time_total(phone, start_time, end_time, channel)  # 插入数据
        start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')
        if channel == "0":
            if query_info == "online":
                res_info = TimesTotal.objects.filter(day_time__range=[start_date, end_date]).values("day_time","channel","online").order_by("day_time")
            elif query_info == "online_pay":
                res_info = TimesTotal.objects.filter(day_time__range=[start_date, end_date]).values("day_time","channel","online_pay").order_by("day_time")
            else:
                res_info = TimesTotal.objects.filter(day_time__range=[start_date, end_date]).values("day_time","channel","online_vip").order_by("day_time")
        else:
            if query_info == "online":
                res_info = TimesTotal.objects.filter(day_time__range=[start_date, end_date], channel=channel).values("day_time","channel","online").order_by("day_time")
            elif query_info == "online_pay":
                res_info = TimesTotal.objects.filter(day_time__range=[start_date, end_date], channel=channel).values("day_time","channel","online_pay").order_by("day_time")
            else:
                res_info = TimesTotal.objects.filter(day_time__range=[start_date, end_date], channel=channel).values("day_time","channel","online_vip").order_by("day_time")

        for r_data in res_info:
            time_info = Context.json_loads(r_data.get("{}".format(query_info)))
            day_time = r_data.get("day_time","")
            channel = r_data.get("channel", "")
            time_info.update({"day_time":day_time, "channel":channel})
            times_list.append(time_info)

        paginator = Paginator(times_list, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        day_info.update({'page': page, "number": number})
    day_info.update({"times_period": times_period, "chanel_info": chanel_info, "url_date": url_date})
    return render(request, "currency_total/time_total.html",day_info)


def insert_time_total(phone, start_time, end_day,channel):
    url = '/v2/shell/gm/query/times_period_data'
    start_stamp = Time.str_to_timestamp(start_time, "%Y-%m-%d")
    initial_stamp = Time.str_to_timestamp("2020-01-10", "%Y-%m-%d")
    if start_stamp < initial_stamp:
        start_day = "2020-01-10"
    else:
        start_day = start_time
    if channel == "0":
        context = {"start": start_day, "end": end_day}
    else:
        context = {"start": start_day, "end": end_day, "channel": channel}
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    ret_dict = Context.json_loads(ret.text)
    if "times_data" not in ret_dict:
        return 0
    else:
        times_list = []
        times_data = ret_dict["times_data"]
        for info in times_data:
            for day_time, channel_info in info.items():
                for channel_id, values in channel_info.items():
                    if values:
                        values.update({"day_time": day_time, "channel": channel_id})
                        times_list.append(values)
                    else:
                        continue
        create_times_total(times_list)


def create_times_total(times_list):
    """时段统计数据"""
    time_data = []
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d')
    for m_info in times_list:
        day_time,channel,online,online_pay,online_vip = m_info["day_time"],m_info["channel"],m_info["online"],m_info["online_pay"],m_info["online_vip"]
        res = TimesTotal.objects.filter(day_time=day_time, channel=channel).first()
        if res:
            TimesTotal.objects.filter(day_time=day_time, channel=channel).update(
                day_time=day_time,
                insert_time = insert_time,
                channel = channel,
                online=Context.json_dumps(online),
                online_pay=Context.json_dumps(online_pay),
                online_vip=Context.json_dumps(online_vip),
            )
        else:
            new_time = TimesTotal(
                day_time=day_time,
                insert_time=insert_time,
                channel=channel,
                online=Context.json_dumps(online),
                online_pay=Context.json_dumps(online_pay),
                online_vip=Context.json_dumps(online_vip),
            )
            time_data.append(new_time)

        if len(time_data) > 1000:
            TimesTotal.objects.bulk_create(time_data)
            time_data = []
    TimesTotal.objects.bulk_create(time_data)


def get_times_period(phone):
    """获取数据"""
    keys = 'times_total_period:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day", "channel", "query_info"])  # 筛选条件
    start_time, end_time, channel, query_info = result[0], result[1], result[2], result[3]

    def_time = {"start_day": start_time, "end_day": end_time, "channel": channel, "query_info": query_info}
    conf_info = []
    start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
    end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')
    if channel == "0":
        if query_info == "online":
            res_info = TimesTotal.objects.filter(day_time__range=[start_date, end_date]).values("day_time", "channel", "online").order_by("day_time")
        elif query_info == "online_pay":
            res_info = TimesTotal.objects.filter(day_time__range=[start_date, end_date]).values("day_time", "channel", "online_pay").order_by("day_time")
        else:
            res_info = TimesTotal.objects.filter(day_time__range=[start_date, end_date]).values("day_time", "channel", "online_vip").order_by("day_time")
    else:
        if query_info == "online":
            res_info = TimesTotal.objects.filter(day_time__range=[start_date, end_date], channel=channel).values("day_time", "channel", "online").order_by("day_time")
        elif query_info == "online_pay":
            res_info = TimesTotal.objects.filter(day_time__range=[start_date, end_date], channel=channel).values("day_time", "channel", "online_pay").order_by("day_time")
        else:
            res_info = TimesTotal.objects.filter(day_time__range=[start_date, end_date], channel=channel).values("day_time", "channel", "online_vip").order_by("day_time")

    for r_data in res_info:
        time_info = Context.json_loads(r_data.get("{}".format(query_info)))
        day_time = r_data.get("day_time", "")
        channel = r_data.get("channel", "")
        time_info.update({"day_time": day_time, "channel": channel})
        conf_info.append(time_info)
    return conf_info, def_time


@decorator
def gift_box_total(request):
    """礼盒数据统计"""
    phone, index, number = request.session.get('uid'), 1, 1
    old_data = ChannelList.objects.all().values('channel_data').first()
    chanel_info = Context.json_loads(old_data['channel_data'])  # 渠道
    times_period = Data_Info.get_times_total()
    url_date = "/currency_total/gift_box_total/"
    if request.method == 'GET':
        one_page = request.GET.get('page')
        if one_page:
            conf, day_info = get_day_game_total(phone)
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
            day_info = {"start_day": day_time, "end_day": day_time, "number": number, "page": []}
    else:
        dic = request.POST
        start_time = dic.get("start_time")[:10]
        end_time = dic.get("stop_time")[:10]
        channel = dic.get("channel").encode('utf-8')

        day_info = {"start_day": start_time, "end_day": end_time, "channel": channel}
        keys = 'gift_box_total:{}:{}'.format(phone, 'query')
        Context.RedisMatch.hash_mset(keys, day_info)
        # insert_day_game_total(phone, start_time, end_time, channel)
        start_day = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_day = Time.str_to_datetime(end_time, '%Y-%m-%d')
        while start_day <= end_day:
            res = PropsTotal.objects.filter(day_time=start_day).first()
            cur_day = Time.datetime_to_str(start_day, '%Y-%m-%d')
            if res:
                if res.day_time == res.insert_time:
                    insert_day_game_total(phone, cur_day, cur_day, channel)  # 插入数据
                else:
                    start_day = Time.next_days(start_day)
                    continue
            else:
                insert_day_game_total(phone, cur_day, cur_day, channel)  # 插入数据
            start_day = Time.next_days(start_day)
        start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
        end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')
        if channel == "0":
            res_info = PropsTotal.objects.filter(day_time__range=[start_date, end_date]).values('json_data').order_by("-day_time")
        else:
            res_info = PropsTotal.objects.filter(day_time__range=[start_date, end_date], channel=channel).values('json_data').order_by("-day_time")

        game_list = []
        for info in res_info:
            game_list.append(Context.json_loads(info.get("json_data")))
        paginator = Paginator(game_list, 30)
        page, plist = Context.paging(paginator, 1)  # 翻页
        day_info.update({'page': page, "number": number})
    day_info.update({"times_period": times_period, "chanel_info": chanel_info, "url_date": url_date})
    return render(request, "currency_total/gift_box_total.html", day_info)


def insert_day_game_total(phone, start_time, end_time, channel):
    url = "/v2/shell/gm/query/day_game_total"
    if channel == "0":
        context = {"start": start_time, "end": end_time}
    else:
        context = {"start": start_time, "end": end_time, "channel": channel}
    context.update({"phone": phone})
    ret = Context.Controller.request(url, context)
    config = Context.json_loads(ret.text)
    if "info" not in config:
        return 0
    else:
        channel_list = []
        config = config["info"]
        for day_time, channel_data in config.items():
            all_total = {"day_time": day_time, "channel": "1000"}
            only_channel = {}
            for channel_id, channel_info in channel_data.items():
                day_info = {"day_time": day_time, "channel": channel_id}
                in_gift_rate = 0
                day_pay_total, in_props_601, in_props_602, in_props_603 = 0, 0, 0, 0
                in_props_1302, in_props_1305, in_props_1321, in_props_1327 = 0, 0, 0, 0
                out_props_601, out_props_602, out_props_603 = 0, 0, 0
                out_props_1302, out_props_1305, out_props_1321, out_props_1327 = 0, 0, 0, 0
                in_silver_coupon, in_props_702, in_props_703, in_props_704 = 0, 0, 0, 0
                for key, value in channel_info.items():
                    # 当日充值
                    if key.endswith('{}.pay.user.pay_total'.format(channel_id)):
                        day_pay_total = int(value)
                    # 福袋
                    if key.startswith("in.props.1302."):
                        day_info[key] = int(day_info.get(key, 0)) + int(value)
                        in_props_1302 += int(value)
                    if key.startswith("out.props.1302."):
                        out_props_1302 += -int(value)

                    # 捕鸟宝箱
                    if key.startswith("in.props.1327."):
                        day_info[key] = int(day_info.get(key, 0)) + int(value)
                        in_props_1327 += int(value)
                    if key.startswith("out.props.1327."):
                        out_props_1327 += -int(value)
                    # 粽子
                    if key.startswith("in.props.1321.") or key.startswith("in.props.1322.") or key.startswith("in.props.1323."):
                        day_info[key] = int(day_info.get(key, 0)) + int(value)
                        in_props_1321 += int(value)
                    if key.startswith("out.props.1321.") or key.startswith("out.props.1322.") or key.startswith("out.props.1323."):
                        out_props_1321 += -int(value)
                    # 礼盒
                    if key.startswith("in.props.1305."):
                        day_info[key] = int(day_info.get(key, 0)) + int(value)
                        in_props_1305 += int(value)
                    if key.startswith("out.props.1305."):
                        out_props_1305 += -int(value)
                    # 蓝色宝箱
                    if key.startswith("in.props.601."):
                        day_info[key] = int(day_info.get(key, 0)) + int(value)
                        in_props_601 += int(value)
                    if key.startswith("out.props.601."):
                        out_props_601 += -int(value)
                    # 紫色宝箱
                    if key.startswith("in.props.602."):
                        day_info[key] = int(day_info.get(key, 0)) + int(value)
                        in_props_602 += int(value)
                    if key.startswith("out.props.602."):
                        out_props_602 += -int(value)
                    # 钻石宝箱
                    if key.startswith("in.props.603."):
                        day_info[key] = int(day_info.get(key, 0)) + int(value)
                        in_props_603 += int(value)
                    if key.startswith("out.props.603."):
                        out_props_603 += -int(value)

                    # 话费券产出
                    if key.startswith('in.silver_coupon.open_box.'):
                        day_info[key] = int(day_info.get(key, 0)) + int(value)
                        in_silver_coupon += int(value)
                    # 冰龙蛋产出
                    if key.startswith('in.props.702.open_box.') or key.startswith('in.props.702.props.use.302') or \
                       key.startswith('in.props.702.props.use.305') or key.startswith('in.props.702.props.use.321') or \
                       key.startswith('in.props.702.props.use.327'):
                        day_info[key] = int(day_info.get(key, 0)) + int(value)
                        in_props_702 += int(value)
                    # 火龙蛋产出
                    if key.startswith('in.props.703.open_box.') or key.startswith('in.props.703.props.use.302') or \
                       key.startswith('in.props.703.props.use.305') or key.startswith('in.props.703.props.use.321') or \
                       key.startswith('in.props.703.props.use.327'):
                        day_info[key] = int(day_info.get(key, 0)) + int(value)
                        in_props_703 += int(value)
                    # 圣龙蛋产出
                    if key.startswith('in.props.704.open_box.') or key.startswith('in.props.704.props.use.302') or \
                            key.startswith('in.props.704.props.use.305') or key.startswith('in.props.704.props.use.321') or \
                            key.startswith('in.props.704.props.use.327'):
                        day_info[key] = int(day_info.get(key, 0)) + int(value)
                        in_props_704 += int(value)
                    gift_price = (in_props_1327 * 8.8 + in_props_1302 * 8.8 + in_props_1321 * 8.8 + in_props_1305 * 8.8 + in_props_601 * 25 + in_props_602 * 50 + in_props_603 * 250)
                    in_gift_rate = round((gift_price / day_pay_total if day_pay_total != 0 else 0), 2)
                day_info.update({"in_props_1302": in_props_1302, "in_props_1321": in_props_1321, "in_props_1305": in_props_1305, "in_props_1327": in_props_1327,
                                 "out_props_1302": out_props_1302, "out_props_1321": out_props_1321, "out_props_1305": out_props_1305, "out_props_1327": out_props_1327
                                 })
                day_info.update({"in_props_601": in_props_601, "in_props_602": in_props_602, "in_props_603": in_props_603,
                                 "out_props_601": out_props_601, "out_props_602": out_props_602, "out_props_603": out_props_603
                                 })

                in_props_1321_popup = Tips.get_in_props_1321_popup(day_info, int(in_props_1321))
                in_props_1305_popup = Tips.get_in_props_1305_popup(day_info, int(in_props_1305))
                in_props_1302_popup = Tips.get_in_props_1302_popup(day_info, int(in_props_1302))
                in_props_1327_popup = Tips.get_in_props_1327_popup(day_info, int(in_props_1327))
                in_props_601_popup = Tips.get_in_props_601_popup(day_info, int(in_props_601))
                in_props_602_popup = Tips.get_in_props_602_popup(day_info, int(in_props_602))
                in_props_603_popup = Tips.get_in_props_603_popup(day_info, int(in_props_603))
                day_info.update(
                            {"in_props_1321_pop": in_props_1321_popup, "in_props_1305_pop": in_props_1305_popup, "in_props_1302_pop": in_props_1302_popup,
                             "in_props_601_pop": in_props_601_popup, "in_props_602_pop": in_props_602_popup, "in_props_603_pop": in_props_603_popup,
                             "in_props_1327_pop": in_props_1327_popup
                             })

                in_silver_coupon_popup = Tips.get_in_silver_coupon_popup(day_info, int(in_silver_coupon))
                day_info.update({"in_gift_rate": in_gift_rate, "in_silver_coupon": in_silver_coupon, "in_silver_coupon_pop": in_silver_coupon_popup})

                in_props_702_popup = Tips.get_in_props_702_popup(day_info, int(in_props_702))
                in_props_703_popup = Tips.get_in_props_703_popup(day_info, int(in_props_703))
                in_props_704_popup = Tips.get_in_props_704_popup(day_info, int(in_props_704))
                day_info.update({"in_props_702_pop": in_props_702_popup, "in_props_703_pop": in_props_703_popup, "in_props_704_pop": in_props_704_popup,
                                 "in_props_702": in_props_702, "in_props_703": in_props_703, "in_props_704": in_props_704, "day_pay_total": day_pay_total})

                if in_props_702 > 0 or in_props_703 > 0 or in_props_704 > 0 or in_silver_coupon > 0:
                    only_channel[channel_id] = day_info
                    channel_list.append(day_info)
            for ch_id, ch_info in only_channel.items():
                for keys, values in ch_info.items():
                    if keys != 'day_time' and keys != 'channel' and keys != 'in_props_702_pop' and keys != 'in_props_703_pop' \
                            and keys != 'in_props_704_pop' and keys != 'in_silver_coupon_pop' and keys != 'in_props_1321_pop' \
                            and keys != 'in_props_1305_pop' and keys != 'in_props_1302_pop' and keys != 'in_props_601_pop' \
                            and keys != 'in_props_602_pop' and keys != 'in_props_603_pop' and keys != 'in_props_1327_pop':
                        print("-------keys--------", keys)
                        all_total.update({keys: int(all_total.get(keys, 0)) + int(values)})

            in_silver_coupon, in_props_702 = int(all_total["in_silver_coupon"]), int(all_total["in_props_702"])
            in_props_703, in_props_704 = int(all_total["in_props_703"]), int(all_total["in_props_704"])
            in_silver_coupon_popup = Tips.get_in_silver_coupon_popup(all_total, in_silver_coupon)
            all_total.update({"in_silver_coupon_pop": in_silver_coupon_popup})

            in_props_702_popup = Tips.get_in_props_702_popup(all_total, in_props_702)
            in_props_703_popup = Tips.get_in_props_703_popup(all_total, in_props_703)
            in_props_704_popup = Tips.get_in_props_704_popup(all_total, in_props_704)
            all_total.update({"in_props_702_pop": in_props_702_popup, "in_props_703_pop": in_props_703_popup,
                             "in_props_704_pop": in_props_704_popup})

            in_props_1321, in_props_1305 = int(all_total["in_props_1321"]), int(all_total["in_props_1305"])
            in_props_1302, in_props_601 = int(all_total["in_props_1302"]), int(all_total["in_props_601"])
            in_props_602, in_props_603 = int(all_total["in_props_602"]), int(all_total["in_props_603"])
            in_props_1327 = int(all_total["in_props_1327"])
            in_props_1321_popup = Tips.get_in_props_1321_popup(all_total, in_props_1321)
            in_props_1305_popup = Tips.get_in_props_1305_popup(all_total, in_props_1305)
            in_props_1302_popup = Tips.get_in_props_1302_popup(all_total, in_props_1302)
            in_props_1327_popup = Tips.get_in_props_1327_popup(all_total, in_props_1327)
            in_props_601_popup = Tips.get_in_props_601_popup(all_total, in_props_601)
            in_props_602_popup = Tips.get_in_props_602_popup(all_total, in_props_602)
            in_props_603_popup = Tips.get_in_props_603_popup(all_total, in_props_603)
            all_total.update(
                {"in_props_1321_pop": in_props_1321_popup, "in_props_1305_pop": in_props_1305_popup,
                 "in_props_1302_pop": in_props_1302_popup,"in_props_1327_pop": in_props_1327_popup,
                 "in_props_601_pop": in_props_601_popup, "in_props_602_pop": in_props_602_popup,
                 "in_props_603_pop": in_props_603_popup
                 })
            if in_props_702 > 0 or in_props_703 > 0 or in_props_704 > 0 or in_silver_coupon > 0:
                channel_list.append(all_total)
        create_day_game_info(channel_list)


def create_day_game_info(channel_list):
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d')
    day_data = []
    for m_info in channel_list:
        day_time, channel = m_info["day_time"], m_info["channel"]
        res = PropsTotal.objects.filter(day_time=day_time, channel=channel).first()
        if res:
            PropsTotal.objects.filter(day_time=day_time, channel=channel).update(
                day_time=day_time,
                insert_time=insert_time,
                channel=channel,
                json_data=Context.json_dumps(m_info)
            )
        else:
            new_info = PropsTotal(
                day_time=day_time,
                insert_time=insert_time,
                channel=channel,
                json_data=Context.json_dumps(m_info)
            )
            day_data.append(new_info)

        if len(day_data) > 1000:
            PropsTotal.objects.bulk_create(day_data)
            day_data = []
    PropsTotal.objects.bulk_create(day_data)


def get_day_game_total(phone):
    keys = 'gift_box_total:{}:{}'.format(phone, 'query')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day", "channel"])
    start_day, end_day, channel = result[0], result[1], str(result[2])
    def_info = {"start_day": start_day, "end_day": end_day, "channel": channel}
    start_date = Time.str_to_datetime(start_day, '%Y-%m-%d')
    end_date = Time.str_to_datetime(end_day, '%Y-%m-%d')
    if channel == "0":
        res_info = PropsTotal.objects.filter(day_time__range=[start_date, end_date]).values('json_data').order_by("-day_time")
    else:
        res_info = PropsTotal.objects.filter(day_time__range=[start_date, end_date], channel=channel).values('json_data').order_by("-day_time")

    sort_info = []
    for info in res_info:
        sort_info.append(Context.json_loads(info.get("json_data")))
    return sort_info, def_info



@decorator
def derived_pay_total(request):
    """付费数据统计--导出xls"""
    phone = request.session.get('uid')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=pay_data.xls'
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
    sheet.write(0, 2, '渠道ID', style)
    sheet.write(0, 3, '商品ID', style)
    sheet.write(0, 4, '商品名称', style)
    sheet.write(0, 5, '商品价值', style)
    sheet.write(0, 6, '购买次数', style)
    sheet.write(0, 7, '购买金额', style)

    pay_info, _ = get_pay_period(phone)

    data_row = 1
    for info in pay_info:
        sheet.write(data_row, 0, data_row)
        sheet.write(data_row, 1, info.get("day_time", 0))
        sheet.write(data_row, 2, info.get("channel", 0))
        sheet.write(data_row, 3, info.get("good_id", 0))
        sheet.write(data_row, 4, info.get("good_name", 0))
        sheet.write(data_row, 5, info.get("cost", 0))
        sheet.write(data_row, 6, info.get("pay_time", 0))
        sheet.write(data_row, 7, info.get("pay_sum", 0))
        data_row = data_row + 1
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response

@decorator
def derived_times_total(request):
    """时段数据统计--导出xls"""
    phone = request.session.get('uid')
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=times_data.xls'
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
    sheet.write(0, 2, '渠道ID', style)
    sheet.write(0, 3, '1', style)
    sheet.write(0, 4, '2', style)
    sheet.write(0, 5, '3', style)
    sheet.write(0, 6, '4', style)
    sheet.write(0, 7, '5', style)
    sheet.write(0, 8, '6', style)
    sheet.write(0, 9, '7', style)
    sheet.write(0, 10, '8', style)
    sheet.write(0, 11, '9', style)
    sheet.write(0, 12, '10', style)
    sheet.write(0, 13, '11', style)
    sheet.write(0, 14, '12', style)
    sheet.write(0, 15, '13', style)
    sheet.write(0, 16, '14', style)
    sheet.write(0, 17, '15', style)
    sheet.write(0, 18, '16', style)
    sheet.write(0, 19, '17', style)
    sheet.write(0, 20, '18', style)
    sheet.write(0, 21, '19', style)
    sheet.write(0, 22, '20', style)
    sheet.write(0, 23, '21', style)
    sheet.write(0, 24, '22', style)
    sheet.write(0, 25, '23', style)
    sheet.write(0, 26, '24', style)

    time_info, _ = get_times_period(phone)

    data_row = 1
    for info in time_info:
        sheet.write(data_row, 0, data_row)
        sheet.write(data_row, 1, info.get("day_time", 0))
        sheet.write(data_row, 2, info.get("channel", 0))
        sheet.write(data_row, 3, info.get("1", 0))
        sheet.write(data_row, 4, info.get("2", 0))
        sheet.write(data_row, 5, info.get("3", 0))
        sheet.write(data_row, 6, info.get("4", 0))
        sheet.write(data_row, 7, info.get("5", 0))
        sheet.write(data_row, 8, info.get("6", 0))
        sheet.write(data_row, 9, info.get("7", 0))
        sheet.write(data_row, 10, info.get("8", 0))
        sheet.write(data_row, 11, info.get("9", 0))
        sheet.write(data_row, 12, info.get("10", 0))
        sheet.write(data_row, 13, info.get("11", 0))
        sheet.write(data_row, 14, info.get("12", 0))
        sheet.write(data_row, 15, info.get("13", 0))
        sheet.write(data_row, 16, info.get("14", 0))
        sheet.write(data_row, 17, info.get("15", 0))
        sheet.write(data_row, 18, info.get("16", 0))
        sheet.write(data_row, 19, info.get("17", 0))
        sheet.write(data_row, 20, info.get("18", 0))
        sheet.write(data_row, 21, info.get("19", 0))
        sheet.write(data_row, 22, info.get("20", 0))
        sheet.write(data_row, 23, info.get("21", 0))
        sheet.write(data_row, 24, info.get("22", 0))
        sheet.write(data_row, 25, info.get("23", 0))
        sheet.write(data_row, 26, info.get("24", 0))

        data_row = data_row + 1
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response