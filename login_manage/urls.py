# -*- coding=utf-8 -*-

from django.conf.urls import url
from django.conf import settings
from django.views import static
import views as login

urlpatterns = [
    url(r'^$', login.main_show),
    url(r'^login/', login.main_login),
    url(r'^login_out/', login.login_out),
    url(r'^top/', login.main_top_show),
    url(r'^left/', login.main_left_show),
    url(r'^index/', login.main_index_show),
    url(r'^right/', login.main_right_show),
    url(r'^verify_code/$', login.verify_code),
    url(r'^get_verify/$', login.get_VerifyCode),
    url(r'^check_phone/$', login.check_phone),
    # url(r'^static/(?P<path>.*)$', static.serve,{'document_root': settings.STATIC_ROOT}, name='static')
]

# 配置异常页面
# handler403 = main_views.page_permission_denied
# handler404 = main_views.page_not_found
# handler500 = main_views.page_error