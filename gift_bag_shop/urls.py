#!/usr/bin/env python
# -*- coding=utf-8 -*-

from django.conf.urls import url
from django.conf import settings
from django.views import static
import views

urlpatterns = [
    url(r'^gift_shop/$', views.gift_shop),

    # url(r'^static/(?P<path>.*)$', static.serve,{'document_root': settings.STATIC_ROOT}, name='static')
]
# 配置异常页面
# handler403 = exchange_views.page_permission_denied
# handler404 = exchange_views.page_not_found
# handler500 = exchange_views.page_error