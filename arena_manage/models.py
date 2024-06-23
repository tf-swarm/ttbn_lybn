# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class CelerityGeneral(models.Model):
    """快速赛--总览"""
    day_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    games_type = models.CharField(max_length=20)
    json_data = models.CharField(max_length=1600)


class CelerityDetails(models.Model):
    """快速赛--详情"""
    user_uid = models.CharField(max_length=200)
    day_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    games_type = models.CharField(max_length=20)
    json_data = models.CharField(max_length=1600)
