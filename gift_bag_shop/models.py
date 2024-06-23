# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.

ACTIVE_TYPE = (
    (1, _(u"上架")),
    (2, _(u"下架")),
)


class GiftInfo(models.Model):
    """礼包商城"""
    gift_id = models.CharField(max_length=16, null=True)
    skip = models.CharField(max_length=10, null=True)
    gift_name = models.CharField(max_length=160, null=True)
    version_id = models.CharField(max_length=16, null=True)                               # 版本号
    index = models.CharField(max_length=6, default=1000)                                      # 排序
    hot = models.CharField(max_length=6, null=True)                                        # 热度
    start_time = models.DateTimeField(auto_now_add=False, null=True)                       # 开启时间
    end_time = models.DateTimeField(auto_now_add=False, null=True)                         # 结束时间
    icon_type = models.CharField(max_length=6, null=True)                                  # icon类型
    price = models.BigIntegerField()                                                       # 价格
    worth = models.BigIntegerField()                                                       # 价值
    open_type = models.CharField(max_length=6, null=True)                                  # 开放类型
    limit_num = models.BigIntegerField()                                                   # 限制数量
    vip_type = models.CharField(max_length=6, null=True)                                   # vip类型
    vip_level = models.CharField(max_length=260, null=True)                                # vip 等级
    detail_1 = models.CharField(max_length=160, null=True)
    detail_2 = models.CharField(max_length=160, null=True)
    detail_3 = models.CharField(max_length=160, null=True)
    online_state = models.IntegerField(choices=ACTIVE_TYPE, null=True, default=2)          # 上架状态
    reward = models.CharField(max_length=1600, null=True)
    add_time = models.IntegerField(null=True)
    add_reward = models.CharField(max_length=1600, null=True)
    channel_list = models.CharField(max_length=660, null=True)

