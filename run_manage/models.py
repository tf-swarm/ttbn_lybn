# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class GameCollect(models.Model):
    """游戏数据汇总"""
    day_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    channel = models.CharField(max_length=12)
    json_data = models.CharField(max_length=16000)


class RunCollect(models.Model):
    """运营数据汇总"""
    day_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    channel = models.CharField(max_length=12)
    json_data = models.CharField(max_length=16000)


class Hardcore(models.Model):
    """硬核和CPS渠道"""
    day_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    channel = models.CharField(max_length=12)
    json_data = models.CharField(max_length=16000)


class Retention(models.Model):
    """留存汇总"""
    day_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    channel = models.CharField(max_length=12)
    json_data = models.CharField(max_length=16000)


class LtvCollect(models.Model):
    """LTV汇总"""
    day_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    channel = models.CharField(max_length=12)
    json_data = models.CharField(max_length=16000)


class OrderQuery(models.Model):
    """订单查询"""
    day_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    order_id = models.CharField(max_length=60)
    productId = models.CharField(max_length=90)
    user_id = models.CharField(max_length=12)
    pay_total = models.CharField(max_length=10, default="")
    pay_status = models.CharField(max_length=10)
    channel = models.CharField(max_length=12)
    json_data = models.CharField(max_length=1600)


class BroadcastData(models.Model):
    """广播总览"""
    broadcast_type = models.CharField(max_length=10)
    broadcast_id = models.BigIntegerField()
    day_time = models.BigIntegerField()
    json_data = models.CharField(max_length=9000)


class MailGeneral(models.Model):
    """邮件总览"""
    create_time = models.DateTimeField(auto_now_add=False, null=True)  # 日期
    mail_type = models.IntegerField()                                # 邮件类型
    nType = models.IntegerField()                                     # 全服 个人
    sender = models.CharField(max_length=20, null=True)                # 发件人
    recipients = models.CharField(max_length=20, null=True)            # 收件人
    subject = models.CharField(max_length=900)                         # 邮件标题
    reason = models.CharField(max_length=80)                          # 发放缘由
    reward = models.CharField(max_length=1000)                        # 奖品内容
    status = models.BigIntegerField()                                 # 审核状态
    verifier = models.CharField(max_length=20, null=True)              # 审核人
    verifier_time = models.DateTimeField(auto_now_add=False, null=True)  # 审核时间


class Notice(models.Model):
    """公告总览"""
    day_time = models.DateTimeField()
    insert_time = models.DateTimeField()
    channel = models.CharField(max_length=12, null=True)
    title = models.CharField(max_length=360, null=True)
    content = models.CharField(max_length=2600, null=True)


class EarlyWarning(models.Model):
    """预警设置"""
    user_status = models.IntegerField(null=True)
    user_list = models.CharField(max_length=600, null=True)
    user_length = models.IntegerField(null=True)


class MailRecord(models.Model):
    """邮件--操作记录"""
    insert_time = models.DateTimeField(auto_now_add=False)
    login_user = models.CharField(max_length=16, default="")
    record_data = models.CharField(max_length=1600, default="")


class BroadcastRecord(models.Model):
    """广播--操作记录"""
    insert_time = models.DateTimeField(auto_now_add=False)
    login_user = models.CharField(max_length=16, default="")
    record_data = models.CharField(max_length=1600, default="")


class EarlyRecord(models.Model):
    """预警异常--操作记录"""
    insert_time = models.DateTimeField(auto_now_add=False)
    login_user = models.CharField(max_length=16, default="")
    record_data = models.CharField(max_length=1600, default="")


class PowerPoolRecord(models.Model):
    """鸟蛋场房间池--操作记录"""
    insert_time = models.DateTimeField(auto_now_add=False)
    login_user = models.CharField(max_length=16, default="")
    record_data = models.CharField(max_length=1600, default="")

