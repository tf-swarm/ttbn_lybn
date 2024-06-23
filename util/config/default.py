#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: likebeta <ixxoo.me@gmail.com>
# Create: 2015-05-06

from util.helper import *
from util.context import Context

# add_global_config('cdkey.access_key', 'aXh4b28ubWVAZ21hag==WwuY29tC')
# add_global_config('shell.special_access_key', 'yQGmK6rjcVdRxYeBzUah==fokMWw')
# add_global_config('shell.access_key', 'aXh4b28ubWVAZ21haWwuY29tCg==')
# add_global_config('game.access_key', '3ZrPg1lXsnbNWIORTh6==xzyiVU7')
# add_global_config('ip.limit.user', 100)
#
# add_game_config(2, 'appKey', 'qifan_self_game_2_eWlzaWxvbmcK')
# add_game_config(10002, 'appKey', 'qifan_self_game_10002_ZVdsemFXeHZibWNLCg')
# add_game_config(10003, 'appKey', 'qifan_self_game_10003_KQ89hPpqYtlU8wPZ')
# add_game_config(10004, 'appKey', 'qifan_self_game_10004_koPHeTDgVvK3xPrRBK')
# add_game_config(10005, 'appKey', 'qifan_self_game_10005_1qNxXiCObRJIawAkGk')
#
# add_global_config('game.desc', [
#     {'id': 2, 'name': u'天天捕鸟'},
#     {'id': 10002, 'name': u'龙虎斗'},
#     {'id': 10003, 'name': u'百人牛牛'},
#     {'id': 10004, 'name': u'水浒传'},
#     {'id': 10005, 'name': u'斗地主'},
# ])


game_key = 'game_redis:{}:{}'.format("system", "config")
res = Context.RedisMatch.hash_mget(game_key, ["file_list"])
print("----------res", res)
if res[0]:
    file_list = Context.json_loads(res[0])
else:
    file_list = []

for s in file_list:
    package_name = str(s)
    print("----------package_name", package_name)
    exec 'from util.game.bird import {}'.format(package_name)

from util.game.bird import *

