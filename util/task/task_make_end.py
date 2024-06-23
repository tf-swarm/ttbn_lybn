#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: likebeta <ixxoo.me@gmail.com>
# Create: 2016-07-13

from util.helper import File
from util.tool import Time
from util.context import Context


def action_make_end(params):
    params['update.time'] = Time.current_ts()
    from util.helper import ConfigHelper
    ConfigHelper.add_config('update.time', params['update.time'])
    ConfigHelper.add_global_config('params', params)
    ConfigHelper.save_config(params['output_dir'], 'redis.output')
    # Context.Log.printstack("-------tf2020--------", params)
    File.write_file(params['output_dir'], 'control.json', Context.json_dumps(params, indent=2))


game_make_end = action_make_end
shell_make_end = action_make_end
