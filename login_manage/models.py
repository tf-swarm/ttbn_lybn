# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


class LoginInfo(models.Model):
    nid = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    account_name = models.CharField(max_length=50, default='')
    limit_level = models.IntegerField(default=0)
    login_limit = models.IntegerField()
    limit = models.IntegerField(default=1)
    phone = models.CharField(max_length=50, default='')
    department = models.CharField(max_length=100, default='')
    ip_address = models.CharField(max_length=50, default='')
    url = models.CharField(max_length=50, default='')
    create_time = models.DateTimeField(default=timezone.now)
    login_time = models.DateTimeField(default=timezone.now)


class VerifyCode(models.Model):
    phone = models.CharField(max_length=50)
    verify = models.CharField(max_length=6)
    times = models.DateTimeField(auto_now_add=True)


class ChannelList(models.Model):
    channel_data = models.CharField(max_length=2600, default='')


class ProductList(models.Model):
    product_id = models.CharField(max_length=16, default='')
    product_data = models.CharField(max_length=900, default='')