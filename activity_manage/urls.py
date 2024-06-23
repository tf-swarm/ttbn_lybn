#!/usr/bin/env python
# -*- coding=utf-8 -*-

from django.conf.urls import url
from django.conf import settings
from django.views import static
import views
from .models import *
urlpatterns = [
    url(r'^red_packet/$', views.red_packet_query),
    url(r'^deal_red_packet/$', views.deal_red_packet),
    url(r'^pay_double/$', views.player_pay_double),
    url(r'^novice_gift/$', views.the_novice_gift),
    url(r'^accumulate_top_up/$', views.accumulate_top_up),
    url(r'^vip_login_give/$', views.vip_login_give),
    url(r'^saving_pot/$', views.saving_pot),
    url(r'^happy_shake_alter/$', views.happy_shake_alter),
    url(r'^happy_shake_query/$', views.happy_shake_query),
    url(r'^activity_gift_bag/$', views.activity_gift_bag),

    url(r'^activity_wheel/$', views.activity_wheel_config),
    url(r'^activity_task/$', views.activity_task_config),
    url(r'^activity_rank/$', views.activity_rank_config),
    url(r'^activity_login/$', views.activity_login_config),
    url(r'^activity_share/$', views.activity_share_config),
    url(r'^activity_discount/$', views.activity_discount_config),
    url(r'^activity_give/$', views.activity_give_config),
    url(r'^make_proud_alter/$', views.may_day_make_proud),
    url(r'^make_proud_query/$', views.make_proud_query),
    url(r'^smash_egg_alter/$', views.smash_egg_alter),
    url(r'^smash_egg_query/$', views.smash_egg_query),
    url(r'^month_card_alter/$', views.month_card_alter),
    url(r'^dragon_boat_alter/$', views.dragon_boat_alter),
    url(r"^dragon_boat_query/$", views.dragon_boat_query),
    url(r"^for_free_give_money/$", views.for_free_give_money),
    url(r"^seven_day_reward/$", views.seven_day_reward),
    url(r"^monopoly/$", views.monopoly_game),

    url(r'^new_user_vip_gift/(\d{1})$', views.new_user_and_vip_gift),
    url(r'^login_luxury_gifts/(\d{1})$', views.luxury_gifts),

    url(r"^bag_lucky_draw/$", views.bag_lucky_draw),
    url(r"^login_lucky_draw/$", views.login_lucky_draw),
    url(r"^special_gift_bag/$", views.special_gift_bag),
    url(r'^recharge_integral/$', views.recharge_integral),
    url(r'^deal_integral_rank/$', views.pay_integral_rank),
    url(r'^all_record/$', views.look_record),
    url(r'^export_xls/$', views.export_all_xls),
    url(r'^red_packet_xls/(\d{1})$', views.red_packet_xls),
    # url(r'^day_week_assignment/$', views.day_week_assignment_alter),


    # url(r'^static/(?P<path>.*)$', static.serve,{'document_root': settings.STATIC_ROOT}, name='static')
]

# 配置异常页面
# handler403 = main_views.page_permission_denied
# handler404 = main_views.page_not_found
# handler500 = main_views.page_error