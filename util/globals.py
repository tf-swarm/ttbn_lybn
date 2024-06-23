#!/usr/bin/env python
# -*- coding=utf-8 -*-

import os

from enum import Enum
class GlobalEnum(Enum):
    UID = 'uid'           # 用户UID


class Global(object):

    def get_context_path(self):
        return os.getcwd()

    def get_path(self):
        return os.path.dirname(self.get_context_path())

    def get_log_path(self):
        return os.path.dirname(self.get_path()) + '/log'


Global = Global()