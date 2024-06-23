#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: likebeta <ixxoo.me@gmail.com>
# Create: 2015-05-11

from util.context import Context
from util.helper import File


def action_push_config(params):
    """推送配置"""
    data = File.read_file(params['redis.output'])
    j = Context.json_loads(data)

    for item in j:
        config, key, value = item[1], item[2], item[3]
        Context.RedisConfig.hash_set(config, key, value)


def game_push_config(params):
    action_push_config(params)


shell_push_config = action_push_config

