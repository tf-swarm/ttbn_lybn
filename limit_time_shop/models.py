# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import ugettext_lazy as _


ACTIVE_TYPE = (
    (1, _(u"已兑换")),
    (2, _(u"未兑换")),
)


class SetCardsClose(models.Model):
    """卡密设置"""
    card_id = models.AutoField(primary_key=True, editable=False)                             # ID
    upload_time = models.DateTimeField(auto_now_add=False, null=True)                        # 上传时间
    card_number = models.CharField(max_length=90, null=True)                                 # 卡号
    card_secret = models.CharField(max_length=260, null=True)                                # 卡密
    card_type = models.CharField(max_length=100, null=True)                                  # 卡类型
    card_price = models.CharField(max_length=100, null=True)                                 # 卡金额
    good_id = models.CharField(max_length=30, default="")                                    # 订单ID
    player_id = models.CharField(max_length=100, null=True)                                  # 玩家ID
    player_nick = models.CharField(max_length=150, null=True)                                # 玩家昵称
    player_phone = models.CharField(max_length=60, null=True)                                # 玩家手机号
    change_time = models.DateTimeField(auto_now_add=False, null=True)                        # 兑换时间
    change_state = models.IntegerField(choices=ACTIVE_TYPE, null=True, default=2)            # 兑换状态


class LimitInfo(models.Model):
    """限时商城--更新数据"""
    good_id = models.CharField(max_length=30)
    channel = models.CharField(max_length=16)
    good_type = models.IntegerField()
    update_time = models.DateTimeField(auto_now_add=True)
    json_data = models.CharField(max_length=1600)


class ExchangeInfo(models.Model):
    """兑换记录"""
    uid = models.CharField(max_length=60)
    nick = models.CharField(max_length=160)
    order_id = models.CharField(max_length=30)
    day_time = models.DateTimeField()
    day_stamp = models.BigIntegerField()
    insert_time = models.DateTimeField()
    channel = models.CharField(max_length=60)
    good_type = models.IntegerField()
    status = models.IntegerField()
    json_data = models.CharField(max_length=1600)


class LimitRecord(models.Model):
    """限时商城--操作记录"""
    insert_time = models.DateTimeField(auto_now_add=False)
    login_user = models.CharField(max_length=16, default="")
    record_data = models.CharField(max_length=1600, default="")


class ExchangeRecord(models.Model):
    """兑换操作记录"""
    insert_time = models.DateTimeField(auto_now_add=False)
    login_user = models.CharField(max_length=16, default="")
    record_data = models.CharField(max_length=1600, default="")


class ChannelCost(models.Model):
    """渠道的成本"""
    query_day = models.CharField(max_length=30)
    json_data = models.CharField(max_length=1600)


class GoodCost(models.Model):
    """记录限时商城全部商品成本"""
    channelID = models.CharField(max_length=36)
    goodID = models.CharField(max_length=36)
    cost = models.CharField(max_length=36)


class LimitPictures(models.Model):
    """限时商城--上传图片"""
    pic_id = models.CharField(max_length=10)
    channel = models.CharField(max_length=12)
    pic_path = models.ImageField(upload_to='limit_time_shop/')
    pic_name = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.pic_path


class LimitGoodId(models.Model):
    """限时商城--添加商品"""
    good_id = models.AutoField(primary_key=True)
    prop_id = models.IntegerField()