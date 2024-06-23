#!/usr/bin/env python
# -*- coding=utf-8 -*-

from django.conf.urls import url
from django.conf import settings
from django.views import static
import views

urlpatterns = [
    url(r'^redeem_overview/$', views.redeem_overview),
    url(r'^deal_redeem/$', views.deal_redeem),
    url(r'^derived_overview/$', views.derived_redeem_info),
    url(r'^redeem_query/$', views.redeem_query),
    url(r'^derived_query/$', views.derived_query_info),

    url(r'^all_record/$', views.all_record),
    #url(r'^record/$', views.operation_record),
    # url(r'^static/(?P<path>.*)$', static.serve,{'document_root': settings.STATIC_ROOT}, name='static')
]
# 配置异常页面
# handler403 = views.page_permission_denied
# handler404 = views.page_not_found
# handler500 = views.page_error