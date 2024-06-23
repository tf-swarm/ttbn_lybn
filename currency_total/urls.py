#!/usr/bin/env python
# -*- coding=utf-8 -*-

from django.conf.urls import url
from django.conf import settings
from django.views import static
import views

urlpatterns = [
    url(r'^channel_total/$', views.channel_total),
    url(r'^pay_total/$', views.pay_total),
    url(r'^times_total/$', views.times_total),
    url(r'^gift_box_total/$', views.gift_box_total),
    url(r'^derived_pay_total/$', views.derived_pay_total),
    url(r'^derived_times_total/$', views.derived_times_total),
    # url(r'^static/(?P<path>.*)$', static.serve,{'document_root': settings.STATIC_ROOT}, name='static')
]

# 配置异常页面
# handler403 = main_views.page_permission_denied
# handler404 = main_views.page_not_found
# handler500 = main_views.page_error