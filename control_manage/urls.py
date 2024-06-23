#!/usr/bin/env python
# -*- coding=utf-8 -*-

from django.conf.urls import url
from django.conf import settings
from django.views import static
import views

urlpatterns = [
    url(r'^account_set/$', views.account_set),
    url(r'^edit_account/$', views.edit_account_info),
    url(r'^alter_layout/$', views.alter_layout),
    url(r'^alter_login/$', views.alter_login_limit),
    url(r'^delete_data/$', views.delete_account_data),
    url(r'^add_login_info/$', views.add_login_info),
    # url(r'^static/(?P<path>.*)$', static.serve,{'document_root': settings.STATIC_ROOT}, name='static')
]

# 配置异常页面
# handler403 = main_views.page_permission_denied
# handler404 = main_views.page_not_found
# handler500 = main_views.page_error