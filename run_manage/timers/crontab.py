# -*- coding: utf-8 -*-

from datetime import datetime,date, timedelta
import time
from util.context import Context
from util.tool import Time
from run_manage.models import *
from limit_time_shop.models import ExchangeInfo
from django.db.models import Count
from run_manage.views import insert_order_info, insert_mysql_collect, insert_hardcore_info, insert_redis_collect, insert_retention_info, insert_ltv_info
from limit_time_shop.views import insert_mysql_exchange


def delete_game():
    ret = Context.RedisCache.hget_keys('game_collect:*:*:*')
    cur_time = int(time.mktime(date.today().timetuple()))
    if ret:
        for del_key in ret:
            days = Time.str_to_timestamp(del_key.split(':')[2], '%Y-%m-%d')
            if days < cur_time:
                Context.RedisCache.delete(del_key)
            else:
                continue

    ret = Context.RedisMatch.hget_keys('game_collect:*:query')
    if ret:
        for del_key in ret:
            Context.RedisMatch.delete(del_key)


def delete_run():
    ret = Context.RedisCache.hget_keys('run_collect:*:*:*')
    cur_time = int(time.mktime(date.today().timetuple()))
    if ret:
        for del_key in ret:
            days = Time.str_to_timestamp(del_key.split(':')[2], '%Y-%m-%d')
            if days < cur_time:
                Context.RedisCache.delete(del_key)
            else:
                continue

    ret = Context.RedisMatch.hget_keys('run_collect:*:query')
    if ret:
        for del_key in ret:
            Context.RedisMatch.delete(del_key)


def delete_order():
    ret = Context.RedisCache.hget_keys('pay_order:*:*:*')
    cur_time = int(time.mktime(date.today().timetuple()))
    if ret:
        for del_key in ret:
            days = Time.str_to_timestamp(del_key.split(':')[2], '%Y-%m-%d')
            if days <= cur_time:
                Context.RedisCache.delete(del_key)
            else:
                continue

    ret = Context.RedisCache.hget_keys('channel_total:*:*:*')
    cur_time = int(time.mktime(date.today().timetuple()))
    if ret:
        for del_key in ret:
            days = Time.str_to_timestamp(del_key.split(':')[2], '%Y-%m-%d')
            if days <= cur_time:
                Context.RedisCache.delete(del_key)
            else:
                continue

    ret = Context.RedisCache.hget_keys('day_shop_record:*:*:*:*')
    cur_time = int(time.mktime(date.today().timetuple()))
    if ret:
        for del_key in ret:
            days = Time.str_to_timestamp(del_key.split(':')[2], '%Y-%m-%d')
            if days <= cur_time:
                Context.RedisCache.delete(del_key)
            else:
                continue

    ret = Context.RedisCache.hget_keys('relax_overview:*:*')
    if ret:
        for item in ret:
            Context.RedisCache.delete(item)

    ret = Context.RedisCache.hget_keys('power_overview:*:*')
    if ret:
        for item in ret:
            Context.RedisCache.delete(item)


def t_order_query():
    keys = 'timers_task:%d:%s' % (2, 'order_query')
    print("key", keys)

    Context.RedisCache.hash_mset(keys, {"state": 0, "insert_time": Time.current_ts()})
    result = Context.RedisCache.hash_mget(keys, ["state", "insert_time"])
    if result[0]:
        if int(result[0]) == 1:
            return 0
        else:
            Context.RedisCache.hash_mset(keys, {"state": 1, "insert_time": Time.current_ts()})
    else:
        Context.RedisCache.hash_mset(keys, {"state": 0, "insert_time": Time.current_ts()})

    res_info = OrderQuery.objects.all().order_by('-day_time', '-id')[:1]
    if res_info:
        last_time = Context.json_loads(res_info[0].json_data)['createTime']
    else:
        last_time = '2019-12-23 00:00:00'
    start_time = last_time[:10]

    cur_time = (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
    end_time = cur_time[:10]
    print("-----order_query:", start_time, end_time)
    start_date = Time.str_to_datetime(start_time, '%Y-%m-%d')
    end_date = Time.str_to_datetime(end_time, '%Y-%m-%d')

    while start_date <= end_date:
        res = OrderQuery.objects.filter(day_time=start_date).first()
        cur_day = Time.datetime_to_str(start_date, '%Y-%m-%d')
        if res:
            if res.day_time == res.insert_time:
                insert_order_info("system", cur_day, cur_day)  # 插入数据
            else:
                start_date = Time.next_days(start_date)
                continue
        else:
            insert_order_info("system", cur_day, cur_day)  # 插入数据
        start_date = Time.next_days(start_date)

    count = OrderQuery.objects.filter(day_time=end_date).aggregate(cur_time_count=Count('*'))

    res_info = ExchangeInfo.objects.all().order_by('-day_time', '-id')[:1]
    if res_info:
        last_time = Context.json_loads(res_info[0].json_data)['end_time']
    else:
        last_time = '2019-12-23 00:00:00'
    start_time = last_time[:10]

    cur_time = (datetime.now() + timedelta(days=-2)).strftime("%Y-%m-%d %H:%M:%S")
    end_time = cur_time[:10]

    start_day = Time.str_to_datetime(start_time, '%Y-%m-%d')
    end_day = Time.str_to_datetime(end_time, '%Y-%m-%d')

    while start_day <= end_day:
        res = ExchangeInfo.objects.filter(day_time=start_day).first()
        cur_day = Time.datetime_to_str(start_day, '%Y-%m-%d')
        if res:
            if res.day_time == res.insert_time:
                insert_mysql_exchange("system",cur_day, cur_day)  # 插入数据
            else:
                start_day = Time.next_days(start_day)
                continue
        else:
            insert_mysql_exchange("system", cur_day, cur_day)  # 插入数据
        start_day = Time.next_days(start_day)

    delete_order()
    Context.RedisCache.hash_mset(keys, {"state": 0, "insert_time": Time.current_ts()})
    print('update_time:', cur_time, 'count={}'.format(count['cur_time_count']))


def t_query_game_data():
    print("timers_task_Game_2019")
    keys = 'timers_task:%d:%s' % (2, 'game_collect')
    print("key", keys)
    Context.RedisCache.hash_mset(keys, {"state": 0, "insert_time": Time.current_ts()})
    result = Context.RedisCache.hash_mget(keys, ["state", "insert_time"])
    print("-----game_query_state:", result[0], type(result[0]))
    if result[0]:
        if int(result[0]) == 1:
            return 0
        else:
            Context.RedisCache.hash_mset(keys, {"state": 1, "insert_time": Time.current_ts()})
    else:
        Context.RedisCache.hash_mset(keys, {"state": 0, "insert_time": Time.current_ts()})

    initial_time = Time.str_to_datetime("2019-12-23", '%Y-%m-%d')
    res = GameCollect.objects.all().values("day_time").last()
    yesterday = Time.str_to_datetime(((datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%d")), "%Y-%m-%d")
    if res:
        last_time = (yesterday + timedelta(days=-120)).strftime("%Y-%m-%d") + " 00:00:00"
        day_stamp = Time.datetime_to_timestamp(res.get("day_time", 0))  # 2019-12-23
        last_stamp = Time.str_to_timestamp(last_time)
        if last_stamp < day_stamp and last_stamp > Time.str_to_timestamp("2019-12-23 00:00:00"):
            start_time = Time.str_to_datetime(last_time[:10], "%Y-%m-%d")
        else:
            start_time = initial_time
    else:
        start_time = initial_time

    print("-----game_collect777:", start_time, yesterday)
    # start_date, end_date = Time.str_to_datetime("2019-12-23", '%Y-%m-%d'), Time.str_to_datetime("2020-06-10", '%Y-%m-%d')
    start_date, end_date = start_time, yesterday
    cur_time = Time.datetime_to_str(end_date)

    print("-----game_collect_insert_time:", start_date, end_date)
    while start_date <= end_date:
        res = GameCollect.objects.filter(day_time=start_date).first()
        cur_day = Time.datetime_to_str(start_date, '%Y-%m-%d')
        if res:
            day_number = (Time.current_ts() - Time.datetime_to_timestamp(res.day_time)) / (3600 * 24)
            if res.day_time == res.insert_time or day_number <= 120:
                insert_mysql_collect(cur_day, cur_day, 1)  # 插入数据
            else:
                start_date = Time.next_days(start_date)
                continue
        else:
            insert_mysql_collect(cur_day, cur_day, 1)  # 插入数据
        start_date = Time.next_days(start_date)

    delete_game()  # 删除redis记录
    count = GameCollect.objects.filter(day_time=end_date).aggregate(cur_time_count=Count('*'))
    Context.RedisCache.hash_mset(keys, {"state": 0, "insert_time": Time.current_ts()})
    print('update_time:', cur_time, 'count={}'.format(count['cur_time_count']))


def t_query_run_data():
    print("timers_task_Run_2019")
    keys = 'timers_task:%d:%s' % (2, 'run_collect')
    print("timers_task", keys)
    Context.RedisCache.hash_mset(keys, {"state": 0, "insert_time": Time.current_ts()})
    result = Context.RedisCache.hash_mget(keys, ["state", "insert_time"])
    print("-----run_query_state:", result[0], type(result[0]))
    if result[0]:
        if int(result[0]) == 1:
            return 0
        else:
            Context.RedisCache.hash_mset(keys, {"state": 1, "insert_time": Time.current_ts()})
    else:
        Context.RedisCache.hash_mset(keys, {"state": 0, "insert_time": Time.current_ts()})

    initial_time = Time.str_to_datetime("2019-12-23", '%Y-%m-%d')
    res = RunCollect.objects.all().values("day_time").last()
    yesterday = Time.str_to_datetime(((datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%d")), "%Y-%m-%d")
    if res:
        last_time = (yesterday + timedelta(days=-120)).strftime("%Y-%m-%d") + " 00:00:00"
        day_stamp = Time.datetime_to_timestamp(res.get("day_time", 0))
        last_stamp = Time.str_to_timestamp(last_time)
        if last_stamp < day_stamp and last_stamp > Time.str_to_timestamp("2019-12-23 00:00:00"):
            start_time = Time.str_to_datetime(last_time[:10], "%Y-%m-%d")
        else:
            start_time = initial_time
    else:
        start_time = initial_time

    start_date, end_date = start_time, yesterday
    # start_date, end_date = Time.str_to_datetime("2019-12-23", '%Y-%m-%d'), Time.str_to_datetime("2020-06-10", '%Y-%m-%d')
    cur_time = Time.datetime_to_str(end_date)
    all_channel = "1000"
    print("-----run_collect_insert_time:", start_date, end_date)
    while start_date <= end_date:
        res = RunCollect.objects.filter(day_time=start_date).first()
        cur_day = Time.datetime_to_str(start_date, '%Y-%m-%d')
        if res:
            day_number = (Time.current_ts() - Time.datetime_to_timestamp(res.day_time)) / (3600 * 24)
            if res.day_time == res.insert_time or day_number <= 120:
                insert_mysql_collect(cur_day, cur_day, 2)  # 插入数据
                insert_hardcore_info(cur_day, "0")
            else:
                start_date = Time.next_days(start_date)
                continue
        else:
            insert_mysql_collect(cur_day, cur_day, 2)  # 插入数据
            insert_hardcore_info(cur_day, "0")
        start_date = Time.next_days(start_date)

    delete_run()  # 删除redis记录
    count = RunCollect.objects.filter(day_time=end_date).aggregate(cur_time_count=Count('*'))
    Context.RedisCache.hash_mset(keys, {"state": 0, "insert_time": Time.current_ts()})
    print('update_time:', cur_time, 'count={}'.format(count['cur_time_count']))


def deal_retention_ltv():
    print("timers_retention_ltv_2020")
    keys = 'timers_task:%d:%s' % (2, 'retention_ltv')
    Context.RedisCache.hash_mset(keys, {"state": 0, "insert_time": Time.current_ts()})
    result = Context.RedisCache.hash_mget(keys, ["state", "insert_time"])
    print("-----retention_ltv:", result[0], type(result[0]))
    if result[0]:
        if int(result[0]) == 1:
            return 0
        else:
            Context.RedisCache.hash_mset(keys, {"state": 1, "insert_time": Time.current_ts()})
    else:
        Context.RedisCache.hash_mset(keys, {"state": 0, "insert_time": Time.current_ts()})

    initial_time = Time.str_to_datetime("2019-12-23", '%Y-%m-%d')
    res = Retention.objects.all().values("day_time").last()
    yesterday = Time.str_to_datetime(((datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%d")), "%Y-%m-%d")
    if res:
        last_time = (yesterday + timedelta(days=-120)).strftime("%Y-%m-%d") + " 00:00:00"
        day_stamp = Time.datetime_to_timestamp(res.get("day_time", 0))
        last_stamp = Time.str_to_timestamp(last_time)
        if last_stamp < day_stamp and last_stamp > Time.str_to_timestamp("2019-12-23 00:00:00"):
            start_time = Time.str_to_datetime(last_time[:10], "%Y-%m-%d")
        else:
            start_time = initial_time
    else:
        start_time = initial_time

    start_date, end_date = start_time, yesterday
    # start_date, end_date = Time.str_to_datetime("2019-12-23", '%Y-%m-%d'), Time.str_to_datetime("2020-06-10", '%Y-%m-%d')
    cur_time = Time.datetime_to_str(end_date)
    all_channel = "1000"
    print("-----retention_ltv_insert_time:", start_date, end_date)
    while start_date <= end_date:
        res = Retention.objects.filter(day_time=start_date).first()
        cur_day = Time.datetime_to_str(start_date, '%Y-%m-%d')
        if res:
            day_number = (Time.current_ts() - Time.datetime_to_timestamp(res.day_time)) / (3600 * 24)
            print("-----day_number:", day_number)
            if res.day_time == res.insert_time or day_number <= 120:
                print("-----res:", res.day_time)
                insert_retention_info(cur_day, cur_day, all_channel)
                insert_ltv_info(cur_day, cur_day, all_channel)
            else:
                start_date = Time.next_days(start_date)
                continue
        else:
            insert_retention_info(cur_day, cur_day, all_channel)
            insert_ltv_info(cur_day, cur_day, all_channel)
        start_date = Time.next_days(start_date)

    count = Retention.objects.filter(day_time=end_date).aggregate(cur_time_count=Count('*'))
    Context.RedisCache.hash_mset(keys, {"state": 0, "insert_time": Time.current_ts()})
    print('update_time:', cur_time, 'count={}'.format(count['cur_time_count']))


def half_hour_request_data():
    print("half_hour")
    keys = 'timers_task:%d:%s' % (2, 'half_hour_deal')
    Context.RedisCache.hash_mset(keys, {"state": 0, "insert_time": Time.current_ts()})
    result = Context.RedisCache.hash_mget(keys, ["state", "insert_time"])
    print("-----half_hour_request:", result[0], type(result[0]))
    if result[0]:
        if int(result[0]) == 1:
            return 0
        else:
            Context.RedisCache.hash_mset(keys, {"state": 1, "insert_time": Time.current_ts()})
    else:
        Context.RedisCache.hash_mset(keys, {"state": 0, "insert_time": Time.current_ts()})

    day_time = Time.current_time('%Y-%m-%d')  # "2020-05-27"
    game_type, run_type = 1, 2  # 1.游戏数据 2.运营数据
    channel = "0"

    insert_redis_collect("system", day_time, day_time, channel, game_type)
    insert_redis_collect("system", day_time, day_time, channel, run_type)
