# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models


class General(models.Model):
    """兑换码总览"""
    day_time = models.DateTimeField()
    cdkey_name = models.CharField(max_length=90)
    channel = models.CharField(max_length=16)
    version = models.CharField(max_length=40)
    pool = models.CharField(max_length=20)
    count = models.BigIntegerField()
    used = models.BigIntegerField()
    unused = models.BigIntegerField()
    reward = models.CharField(max_length=6000)
    create_time = models.DateTimeField(auto_now_add=False)
    lose_time = models.DateTimeField(auto_now_add=False)
    amount = models.BigIntegerField()  # 投放额度


class Query(models.Model):
    """兑换码查询"""
    cdkey_id = models.CharField(max_length=90)
    cdkey_name = models.CharField(max_length=90)
    people = models.CharField(max_length=60)
    used = models.BigIntegerField()
    uid = models.BigIntegerField()
    channel = models.CharField(max_length=60)
    reward = models.CharField(max_length=6000)
    create_time = models.DateTimeField(auto_now_add=False)
    lose_time = models.DateTimeField(auto_now_add=False)
    employ_time = models.DateTimeField(auto_now_add=False)


class Record(models.Model):
    """操作记录"""
    insert_time = models.DateTimeField(auto_now_add=False)
    login_user = models.CharField(max_length=16, default="")
    record_data = models.CharField(max_length=1600, default="")

