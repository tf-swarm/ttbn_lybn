# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class RedPacketInfo(models.Model):
    """红包数据"""
    special_id = models.CharField(max_length=60, default='1547623377')
    stop_state = models.IntegerField()
    special_end_time = models.BigIntegerField()
    red_packet_type = models.BigIntegerField()
    day_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    day_stamp = models.BigIntegerField()
    json_data = models.CharField(max_length=16000)


class RedGetData(models.Model):
    """红包领取信息"""
    red_packet_id = models.CharField(max_length=60, default='1547623377')
    uid = models.BigIntegerField()
    nick = models.CharField(max_length=100)
    packet = models.BigIntegerField()
    time = models.DateTimeField(auto_now_add=False)


# class PayPictures(models.Model):
#     """充值积分周期榜--上传图片"""
#     pic_id = models.AutoField(primary_key=True, unique=True)
#     pic_path = models.ImageField(upload_to='activity/')
#     pic_name = models.CharField(max_length=40, unique=True)
#
#     def __str__(self):
#         return self.pic_path

# class PayRank(models.Model):
#     """充值积分周期榜"""
#     start_stamp = models.BigIntegerField()
#     end_stamp = models.BigIntegerField()
#     insert_stamp = models.BigIntegerField()
#     channel = models.CharField(max_length=360, null=True)


class PayRank(models.Model):
    """充值排行榜"""
    sole_id = models.CharField(max_length=16)
    day_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    uid = models.CharField(max_length=12)
    channel = models.CharField(max_length=10)
    json_data = models.CharField(max_length=1600)