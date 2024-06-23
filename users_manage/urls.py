#!/usr/bin/env python
# -*- coding=utf-8 -*-

from django.conf.urls import url
from django.conf import settings
from django.views import static
import views

urlpatterns = [
    url(r'^relax_overview/$', views.relax_overview),
    url(r'^power_overview/$', views.power_overview),
    url(r'^user_control/$', views.user_control_deal),
    url(r'^user_barrel/$', views.barrel_control),
    url(r'^derived_user/$', views.derived_user_info),
    url(r'^one_key_derived_user/$', views.one_key_derived_user),
    url(r'^user_period_data/$', views.user_period_data),
    url(r'^derived_period_user/$', views.derived_period_user),
    url(r'^derived_power_user/$', views.derived_power_user),
    url(r'^user_give/$', views.user_give_info),
    url(r'^championship/$', views.championship_info),
    url(r'^rob_rank/$', views.rob_rank),
    url(r'^strong_box/$', views.user_strong_box),
    url(r'^stop_service/$', views.stop_service),

    url(r'^query_unlock_info/$', views.query_unlock_info),
    url(r'^player_unlock/$', views.player_unlock),

    # url(r'^static/(?P<path>.*)$', static.serve,{'document_root': settings.STATIC_ROOT}, name='static')
]

# 配置异常页面
# handler403 = main_views.page_permission_denied
# handler404 = main_views.page_not_found
# handler500 = main_views.page_error