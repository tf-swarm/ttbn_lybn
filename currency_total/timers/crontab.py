# -*- coding: utf-8 -*-
from currency_total.views import insert_coupon_rate, insert_period_total
from datetime import date, timedelta
from util.context import Context
from util.tool import Time


def temp_calc_old():
    print 'xx11'
    days = 7
    day_time = "2019-12-23"
    for i in range(0, days):
        old_day = (Time.str_to_datetime(day_time, "%Y-%m-%d") + timedelta(days=i)).strftime("%Y-%m-%d")
        insert_coupon_rate("system", old_day)
        insert_period_total(old_day, old_day)  # 数据汇总

    # Context.RedisCluster.hash_set('global.info.hash', 'max.user.id', 1165230)
    # ret = Context.RedisMix.hget_keys('game:2:*')
    # add_list = sorted(ret)
    # uid_str = "game:2:{}".format(1165231)
    # index = [i for i, x in enumerate(add_list) if x == uid_str][0]
    # print("--------------add_list11", add_list[index:])
    # for del_game in add_list[index:]:
    #     Context.RedisMix.delete(del_game)
    #
    # ret = Context.RedisMix.hget_keys('user:*')
    # user_list = sorted(ret)
    # uid = "user:{}".format(1165231)
    # u_index = [i for i, x in enumerate(user_list) if x == uid][0]
    # print("--------------add_list22", user_list[u_index:])
    # for del_game in user_list[u_index:]:
    #     Context.RedisMix.delete(del_game)
    print 'xx22'


def Calc_Coupon_Rate():
    temp_calc_old()
    print 'xx33'
    yesterday = (date.today() + timedelta(days=-1)).strftime("%Y-%m-%d")  # 昨天日期
    keys = 'timers_task:%d:%s' % (2, 'silver_coupon_rate')
    Context.RedisCache.hash_mset(keys, {"state": 0, "insert_time": Time.current_ts()})
    result = Context.RedisCache.hash_mget(keys, ["state", "insert_time"])
    if result[0]:
        if result[0] == 1:
            return 0
        else:
            Context.RedisCache.hash_mset(keys, {"state": 1, "insert_time": Time.current_ts()})
    else:
        Context.RedisCache.hash_mset(keys, {"state": 0, "insert_time": Time.current_ts()})

    msg = insert_coupon_rate("system", yesterday)
    if msg:
        print("data is insert succeed...")
    else:
        print("data is insert be defeated...")

    insert_period_total(yesterday, yesterday)  # 数据汇总
    Context.RedisCache.hash_mset(keys, {"state": 0, "insert_time": Time.current_ts()})


# if __name__ == '__main__':
#     Calc_Coupon_Rate()
