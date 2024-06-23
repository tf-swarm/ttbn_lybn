# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Account(models.Model):
    nid = models.IntegerField()
    phone = models.CharField(max_length=20, default='')
    control_list = models.CharField(max_length=960, default='')
    account_set = models.IntegerField(default=0)  # 账号管理
    # account_log = models.IntegerField(default=0)  # 管理日志
