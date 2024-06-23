# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class ChannelTotal(models.Model):
    """渠道数据统计"""
    day_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    channel = models.CharField(max_length=12)
    json_data = models.CharField(max_length=16000)


class PayTotal(models.Model):
    """付费数据统计"""
    day_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    channel = models.CharField(max_length=12)
    good_id = models.CharField(max_length=16)
    json_data = models.CharField(max_length=16000)


class TimesTotal(models.Model):
    """时段数据统计"""
    day_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    channel = models.CharField(max_length=12)
    online = models.CharField(max_length=600)
    online_pay = models.CharField(max_length=600)
    online_vip = models.CharField(max_length=600)


class PropsTotal(models.Model):
    """礼盒数据统计"""
    day_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    channel = models.CharField(max_length=12)
    json_data = models.CharField(max_length=16000)