#!/usr/bin/env python
# -*- coding=utf-8 -*-

from django.conf.urls import url
from django.conf import settings
from django.views import static
import views

urlpatterns = [
    url(r'^game_data_collect/$', views.game_data_collect),
    url(r'^run_data_collect/$', views.run_data_collect),
    url(r'^retention_rate/$', views.retention_rate),
    url(r'^ltv_collect/$', views.ltv_collect),
    url(r'^hardcore_channels/$', views.hardcore_channels),
    url(r'^order_query/$', views.order_query),
    url(r'^deal_xls/$', views.deal_xls),
    url(r'^query_mail_info/$', views.query_mail_info),
    url(r'^insert_mail_info/$', views.insert_mail_info),
    url(r'^alter_mail_status/$', views.alter_mail_status),
    url(r'^send_broadcast/$', views.send_broadcast),
    url(r'^query_broadcast/$', views.query_broadcast),
    url(r'^deal_proclamation/$', views.proclamation_general),
    url(r'^recharge_add_gift/$', views.recharge_add_gift),
    url(r'^coin_energy_config/$', views.coin_energy_config),
    url(r'^room_control_config/$', views.room_control_config),
    url(r'^early_warning/$', views.early_warning_signal),
    url(r'^deal_game_info/$', views.deal_game_info),

    url(r'^all_record/$', views.look_record),

    # url(r'^static/(?P<path>.*)$', static.serve,{'document_root': settings.STATIC_ROOT}, name='static')
]

# 配置异常页面
# handler403 = main_views.page_permission_denied
# handler404 = main_views.page_not_found
# handler500 = main_views.page_error