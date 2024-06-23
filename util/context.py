#!/usr/bin/env python
# -*- coding=utf-8 -*-

import copy
import json
import random

from django.core.paginator import Paginator
from log import Logger
from strutil import Strutil
from tool import Time
from globals import Global

from controller import Controller
from cache_info import Cache_Info
from util.db.db_redis import RedisSingle
from util.deal_thread.thread import MyThread
from login_manage.models import LoginInfo
from control_manage.models import Account
from datetime import date, timedelta, datetime
import logging


class Context(object):
    def __init__(self):
        self.Log = Logger
        self.Global = Global
        self.init_log(self.Global.get_log_path())
        self.Strutil = Strutil
        self.Time = Time
        self.Controller = Controller
        self.Cache_Info = Cache_Info

        self.RedisConfig = RedisSingle(0)
        self.RedisCluster = RedisSingle(1)
        self.RedisMix = RedisSingle(2)
        self.RedisPay = RedisSingle(3)
        self.RedisCache = RedisSingle(4)
        self.RedisStat = RedisSingle(5)
        self.RedisActivity = RedisSingle(6)
        self.RedisRecord = RedisSingle(7)
        self.RedisMatch = RedisSingle(8)
        self.MyThread = MyThread


    def init_log(self, log_path):
        self.Log.open_log(log_path)
        self.Log.info('log init in')
        #flags = self.Global.debug_flag()
        #self.Log.show_debug_network('network' in flags)
        #self.Log.show_debug_redis('redis' in flags)
        #if 'debug' not in flags:
        #   self.Log.set_level(Context.Log.INFO)
        #   self.Log.info('log init out')

    @classmethod
    def json_loads(cls, s, ex=False):
        """
        @param ex: 兼容老数据, 慎用, 禁止将dict, list, set, tuple等类型的数据直接str成字符串
        """
        try:
            return json.loads(s)
        except Exception, e:
            if ex:
                return eval(s)
            else:
                raise e

    @classmethod
    def json_dumps(cls, o, **kwargs):
        if 'separators' not in kwargs:
            kwargs['separators'] = (',', ':')
        return json.dumps(o, **kwargs)

    @classmethod
    def copy_json_obj(cls, j):
        t = json.dumps(j)
        return json.loads(t)

    @classmethod
    def copy_obj(cls, o):
        return copy.deepcopy(o)

    @classmethod
    def gene_text(cls, n):
        source = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'Z',' X', 'Y']
        return ''.join(random.sample(source, n))  # number是生成验证码的位数

    @classmethod
    def paging(cls, paginator, pindex):
        # 验证当前页码的合法性
        pindex = pindex
        if pindex <= 1:
            pindex = 1
        if pindex > paginator.num_pages:
            pindex = paginator.num_pages
        # 获取当前页的数据
        page = paginator.page(pindex)
        # 构造页码列表
        if paginator.num_pages <= 5:
            # 特例1：如果不够5页则直接返回所有页码数字
            plist = paginator.page_range
        else:
            # 如果页码大于5则进行公式运算
            if pindex <= 2:
                # 特例2：如果是第1、2则固定为1,2,3,4,5
                plist = range(1, 6)
            elif pindex >= paginator.num_pages - 1:
                # 特例2：如果是末1、末2,已知总页数为n则固定为n-4,n-3,n-2,n-1,n
                plist = range(paginator.num_pages - 4, paginator.num_pages + 1)
            else:
                plist = range(pindex - 2, pindex + 3)
        return page, plist

    @classmethod
    def deal_Paginator(cls, conf, page):
        pages = int(page.encode('utf-8'))
        number = pages
        index = pages
        paginator = Paginator(conf, 30)
        info, plist = Context.paging(paginator, index)
        num_page = paginator.num_pages
        if pages > num_page:
            number = num_page
        return number, info

    @classmethod
    def get_Get_info(cls,url_date, pages_number, conf, compute_info):
        day_time = date.today().strftime('%Y-%m-%d')
        index, number = 1, 1
        if pages_number:
            number, page = cls.deal_Paginator(conf, pages_number)
        else:
            compute_info.update({"start_day": day_time, "end_day": day_time})
            page = []
        compute_info.update({"page": page, "url_date": url_date, "number": number})
        return compute_info

    @classmethod
    def get_server_data(cls, url, context, phone=None):
        if phone:
            context.update({"phone": phone})
        else:
            context.update({"phone": "system"})
        ret = Context.Controller.request(url, context)
        conf = Context.json_loads(ret.text)
        print("-------------get_server_data:", conf)
        config_info = {}
        if "ret" not in conf:
            msg = False
        else:
            config_info = conf["ret"]
            if not config_info and not isinstance(config_info,int):
                msg = False
            else:
                msg = True
        return msg, config_info

    @classmethod
    def get_user_limit(cls, phone):
        user_date = LoginInfo.objects.filter(phone=phone).values('nid')
        nid = user_date[0].get("nid")
        user = Account.objects.filter(nid=nid, phone=phone).values("control_list").first()
        if user:
            control_info = Context.json_loads(user.get("control_list"))
            control_list = [str(n) for n in control_info]
        else:
            control_list = []

        return control_list

    @classmethod
    def get_relax_barrel(cls,gid):
        relax_barrel_unlock_config = [
            {'level': 1, 'multiple': 5},
            {'level': 2, 'multiple': 10, 'diamond': 3, 'reward': {'coin': 1000}},
            {'level': 3, 'multiple': 30, 'diamond': 5, 'reward': {'coin': 1000}},
            {'level': 4, 'multiple': 50, 'diamond': 5, 'reward': {'coin': 2500}},
            {'level': 5, 'multiple': 70, 'diamond': 5, 'reward': {'coin': 2500}},
            {'level': 6, 'multiple': 100, 'diamond': 5, 'reward': {'coin': 3000}},
            {'level': 7, 'multiple': 150, 'diamond': 6, 'reward': {'coin': 3000}},
            {'level': 8, 'multiple': 200, 'diamond': 7, 'reward': {'coin': 3500}},
            {'level': 9, 'multiple': 250, 'diamond': 7, 'reward': {'coin': 3500}},
            {'level': 10, 'multiple': 300, 'diamond': 8, 'reward': {'coin': 4000}},
            {'level': 11, 'multiple': 400, 'diamond': 8, 'reward': {'coin': 4500}},
            {'level': 12, 'multiple': 500, 'diamond': 8, 'reward': {'coin': 5500}, 'add_pool': {'c': 50, 's': 1}},
            {'level': 13, 'multiple': 600, 'diamond': 8, 'reward': {'coin': 6500}},
            {'level': 14, 'multiple': 700, 'diamond': 8, 'reward': {'coin': 7500}},
            {'level': 15, 'multiple': 800, 'diamond': 8, 'reward': {'coin': 8500}},
            {'level': 16, 'multiple': 900, 'diamond': 10, 'reward': {'coin': 9500}},
            {'level': 17, 'multiple': 1000, 'diamond': 10, 'reward': {'coin': 10000}},
            {'level': 18, 'multiple': 1100, 'diamond': 10, 'reward': {'coin': 15000}},
            {'level': 19, 'multiple': 1200, 'diamond': 12, 'reward': {'coin': 15000}},
            {'level': 20, 'multiple': 1300, 'diamond': 12, 'reward': {'coin': 15000}},
            {'level': 21, 'multiple': 1400, 'diamond': 12, 'reward': {'coin': 15000}},
            {'level': 22, 'multiple': 1500, 'diamond': 15, 'reward': {'coin': 20000}},
            {'level': 23, 'multiple': 1600, 'diamond': 15, 'reward': {'coin': 20000}},
            {'level': 24, 'multiple': 1700, 'diamond': 15, 'reward': {'coin': 20000}},
            {'level': 25, 'multiple': 1800, 'diamond': 15, 'reward': {'coin': 20000}},
            {'level': 26, 'multiple': 1900, 'diamond': 15, 'reward': {'coin': 20000}, 'add_pool': {'c': 50, 's': 1}},
            {'level': 27, 'multiple': 2000, 'diamond': 20, 'reward': {'coin': 25000}},
            {'level': 28, 'multiple': 2200, 'diamond': 30, 'reward': {'coin': 25000}},
            {'level': 29, 'multiple': 2400, 'diamond': 40, 'reward': {'coin': 25000}},
            {'level': 30, 'multiple': 2600, 'diamond': 50, 'reward': {'coin': 30000}},
            {'level': 31, 'multiple': 2800, 'diamond': 50, 'reward': {'coin': 30000}, 'add_pool': {'c': 50, 's': 1}},
            {'level': 32, 'multiple': 3000, 'diamond': 50, 'reward': {'coin': 35000}},
            {'level': 33, 'multiple': 3500, 'diamond': 50, 'reward': {'coin': 40000}},
            {'level': 34, 'multiple': 4000, 'diamond': 50, 'reward': {'coin': 45000}},
            {'level': 35, 'multiple': 5000, 'diamond': 100, 'reward': {'coin': 55000}, 'add_pool': {'c': 50, 's': 1}},
            {'level': 36, 'multiple': 6000, 'diamond': 100, 'reward': {'coin': 65000}},
            {'level': 37, 'multiple': 7000, 'diamond': 150, 'reward': {'coin': 75000}},
            {'level': 38, 'multiple': 8000, 'diamond': 150, 'reward': {'coin': 85000}},
            {'level': 39, 'multiple': 9000, 'diamond': 150, 'reward': {'coin': 95000}},
            {'level': 40, 'multiple': 10000, 'diamond': 200, 'reward': {'coin': 100000}},

            {'level': 41, 'multiple': 15000, 'stone': 150, 'reward': {'coin': 150000}},
            {'level': 42, 'multiple': 20000, 'stone': 250, 'reward': {'coin': 200000}},
            {'level': 43, 'multiple': 25000, 'stone': 350, 'reward': {'coin': 250000}},
            {'level': 44, 'multiple': 30000, 'stone': 450, 'reward': {'coin': 300000}},
            {'level': 45, 'multiple': 35000, 'stone': 550, 'reward': {'coin': 350000}},
            {'level': 46, 'multiple': 40000, 'stone': 650, 'reward': {'coin': 400000}},
            {'level': 47, 'multiple': 45000, 'stone': 660, 'reward': {'coin': 450000}},
            {'level': 48, 'multiple': 50000, 'stone': 670, 'reward': {'coin': 500000}},
            {'level': 49, 'multiple': 60000, 'stone': 690, 'reward': {'coin': 600000}},
            {'level': 50, 'multiple': 70000, 'stone': 700, 'reward': {'coin': 700000}},
            {'level': 51, 'multiple': 80000, 'stone': 800, 'reward': {'coin': 800000}},
            {'level': 52, 'multiple': 90000, 'stone': 900, 'reward': {'coin': 900000}},
            {'level': 53, 'multiple': 100000, 'stone': 1000, 'reward': {'coin': 1000000}},
        ]

        return relax_barrel_unlock_config

    @classmethod
    def get_power_barrel(cls, gid):
        power_barrel_unlock_config = [
            {'level': 1, 'multiple': 1000, 'diamond': 100},
            {'level': 2, 'multiple': 5000, 'diamond': 150, 'reward': {'power': 0}},
            {'level': 3, 'multiple': 10000, 'diamond': 200, 'reward': {'power': 0}},

            {'level': 4, 'multiple': 15000, 'stone': 100, 'reward': {'power': 150000}},
            {'level': 5, 'multiple': 20000, 'stone': 100, 'reward': {'power': 200000}},
            {'level': 6, 'multiple': 25000, 'stone': 150, 'reward': {'power': 250000}},
            {'level': 7, 'multiple': 30000, 'stone': 150, 'reward': {'power': 300000}},
            {'level': 8, 'multiple': 35000, 'stone': 200, 'reward': {'power': 350000}},
            {'level': 9, 'multiple': 40000, 'stone': 200, 'reward': {'power': 400000}},
            {'level': 10, 'multiple': 45000, 'stone': 300, 'reward': {'power': 450000}},
            {'level': 11, 'multiple': 50000, 'stone': 400, 'reward': {'power': 500000}},
            {'level': 12, 'multiple': 60000, 'stone': 500, 'reward': {'power': 600000}},
            {'level': 13, 'multiple': 70000, 'stone': 600, 'reward': {'power': 700000}},
            {'level': 14, 'multiple': 80000, 'stone': 650, 'reward': {'power': 800000}},
            {'level': 15, 'multiple': 90000, 'stone': 700, 'reward': {'power': 900000}},
            {'level': 16, 'multiple': 100000, 'stone': 750, 'reward': {'power': 1000000}},
            {'level': 17, 'multiple': 150000, 'stone': 800, 'reward': {'power': 1500000}},
            {'level': 18, 'multiple': 200000, 'stone': 850, 'reward': {'power': 2000000}},
            {'level': 19, 'multiple': 250000, 'stone': 900, 'reward': {'power': 2500000}},
            {'level': 20, 'multiple': 300000, 'stone': 1000, 'reward': {'power': 3000000}},
            {'level': 21, 'multiple': 350000, 'stone': 1000, 'reward': {'power': 3500000}},
            {'level': 22, 'multiple': 400000, 'stone': 1000, 'reward': {'power': 4000000}},
            {'level': 23, 'multiple': 500000, 'stone': 1000, 'reward': {'power': 5000000}},
            {'level': 24, 'multiple': 600000, 'stone': 1000, 'reward': {'power': 6000000}},
            {'level': 25, 'multiple': 700000, 'stone': 1000, 'reward': {'power': 7000000}},
            {'level': 26, 'multiple': 800000, 'stone': 1000, 'reward': {'power': 8000000}},
            {'level': 27, 'multiple': 900000, 'stone': 1000, 'reward': {'power': 9000000}},
            {'level': 28, 'multiple': 1000000, 'stone': 1000, 'reward': {'power': 10000000}},

        ]

        return power_barrel_unlock_config

    @classmethod
    def trans_barrel_level(cls, gid, level, conf=None):
        if conf is None:
            conf = Context.get_relax_barrel(gid)
        elif conf == 1:
            conf = Context.get_power_barrel(gid)
        return conf[level - 1]['multiple']


Context = Context()
