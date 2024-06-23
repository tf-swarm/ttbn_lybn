# -*- coding: utf-8 -*-

from datetime import datetime,date, timedelta
import time
from util.context import Context
from util.tool import Time
from run_manage.models import OrderQuery, GameCollect, RunCollect


def t_activity_deal():
    phone = "system"
    keys = 'timers_task:%d:%s' % (2, 'activity_set')
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

    keys = 'total_pay:{}:{}'.format(phone, 'activity')
    result = Context.RedisMatch.hash_mget(keys, ["start_day", "end_day", "cg", "c", "open_time"])  # cg 保留数据状态
    start_time, end_time, cg, config, days = str(result[0]), str(result[1]), result[2], result[3], int(result[4])
    print("-----------start_time:", start_time, end_time)

    day_time = (Time.str_to_datetime(start_time[:10], "%Y-%m-%d") + timedelta(days=days)).strftime("%Y-%m-%d")
    end_stamp = Time.str_to_timestamp(end_time)
    print("-----------activity:", Time.current_time("%Y-%m-%d"), Time.current_ts())
    print("-----------activity_deal", day_time, end_stamp)
    if day_time == Time.current_time("%Y-%m-%d") and Time.current_ts() <= end_stamp:
        url = '/v2/shell/activity/total_pay'
        context = {"phone": phone, "pid": 2, "cg": cg, "c": config}
        ret = Context.Controller.request(url, context)
        server = Context.json_loads(ret.text)
        if ret.status_code == 200:
            day_info = {"start_day": day_time + " 00:00:00"}
            keys = 'total_pay:{}:{}'.format("system", 'activity')
            Context.RedisMatch.hash_mset(keys, day_info)
            info = "累积充值返奖设置成功！"
        else:
            info = "累积充值返奖设置失败！"
    else:
        server = ""
    print('total_pay_activity:', "开始时间:{}--结束时间:{}".format(start_time,end_time), 'update_status:{}'.format(server))


