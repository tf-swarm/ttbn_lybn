#!/usr/bin/env python
# -*- coding=utf-8 -*-

from django.conf.urls import url
from django.conf import settings
from django.views import static
import views

urlpatterns = [
    url(r'^query_shop/$', views.limit_time_shop),
    url(r'^deal_limit_shop/$', views.deal_with_limit_shop),
    url(r'^deal_shop_picture/$', views.deal_shop_picture),
    url(r'^add_shop_good/$', views.add_shop_good),
    url(r'^shop_exchange_info/', views.shop_exchange_info),
    url(r'^exchange_record_xls/', views.exchange_record_xls),
    url(r'^alter_check_status/', views.alter_check_status),
    url(r'^deal_shipping/', views.shipping_info),
    url(r'^alter_shipping_status/', views.alter_shipping_status),
    url(r'^card_secret/', views.query_card_secret),
    url(r'^card_secret_xls/', views.card_secret_xls),
    url(r'^excel_handle/', views.excel_handle),
    url(r'^exchange_details/', views.shop_exchange_details),

    # url(r'^gift_total/', views.gift_total),
    # url(r'^exchange_total/', views.exchange_total),
    url(r'^shop_all_record/', views.All_record),

    # url(r'^static/(?P<path>.*)$', static.serve,{'document_root': settings.STATIC_ROOT}, name='static')
]
# 配置异常页面
# handler403 = exchange_views.page_permission_denied
# handler404 = exchange_views.page_not_found
# handler500 = exchange_views.page_error