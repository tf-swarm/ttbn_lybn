# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class PeriodData(models.Model):
    """新玩家当天数据统计"""
    uid = models.CharField(max_length=12)
    json_data = models.CharField(max_length=16000)


class PresentData(models.Model):
    """用户赠送详情"""
    sole_id = models.CharField(max_length=16)
    day_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    uid = models.CharField(max_length=12)
    channel = models.CharField(max_length=10)
    json_data = models.CharField(max_length=1600)


class StrongBox(models.Model):
    """保险箱详情"""
    sole_id = models.CharField(max_length=16)
    day_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    box_status = models.CharField(max_length=6)
    uid = models.CharField(max_length=12)
    get_user = models.CharField(max_length=12)
    channel = models.CharField(max_length=10)
    json_data = models.CharField(max_length=1600)


class PowerRank(models.Model):
    """排行榜"""
    sole_id = models.CharField(max_length=16)
    day_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    point_status = models.CharField(max_length=6)
    send_status = models.CharField(max_length=6)
    uid = models.CharField(max_length=12)
    channel = models.CharField(max_length=10)
    json_data = models.CharField(max_length=1600)


class WhiteList(models.Model):
    """白名单"""
    user_status = models.IntegerField(null=True)
    user_list = models.CharField(max_length=600, null=True)
    user_length = models.IntegerField(null=True)
