# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.

from django.core.paginator import Paginator
from util.context import Context
import datetime
from django.shortcuts import render, redirect
from xlwt import *
from io import BytesIO
from util.tool import Time
from .models import *
import time
import json
from login_manage.models import LoginInfo
from login_manage.views import decorator
from django.http import JsonResponse
import socket


@decorator
def account_set(request):
    one_page = request.GET.get('page')
    url_date = "/control_manage/account_set/"
    res = LoginInfo.objects.values('account_name', 'phone', 'department', "limit_level", "login_limit", "nid")
    phone = request.session.get('uid')
    ret = LoginInfo.objects.filter(phone=phone).values('limit_level').first()
    order, account_list = 1, []
    for account in res:
        account.update({"order": order})
        account_list.append(account)
        order += 1
    paginator_page = Paginator(account_list, 30)
    if one_page:
        number, index = one_page, one_page
        page, plist = Context.paging(paginator_page, index)  # 翻页
        num_page = paginator_page.num_pages
        if one_page > num_page:
            number = num_page
    else:
        number = 1
        page, plist = Context.paging(paginator_page, 1)  # 翻页
    user_info = {"page": page, "number": number, "url_date": url_date, "limit_level": ret["limit_level"]}
    return render(request, 'control_manage/right_control.html', user_info)


@decorator
def edit_account_info(request):
    """弹窗显示数据"""
    dic = request.POST
    user_id = dic.get('user_id')
    phone = str(dic.get('phone'))

    control = {}
    res = LoginInfo.objects.filter(nid=user_id, phone=phone).values("account_name", "department").first()
    if res:
        department = res.get("department", "运营")
        user_name = res.get("account_name", "")
        control.update({"user_name": user_name, "department": department})
        user = Account.objects.filter(nid=user_id, phone=phone).values("control_list").first()
        if user:
            control_info = Context.json_loads(user.get("control_list"))
            control_list = [str(n) for n in control_info]
            control.update({"control_list": control_list})
            status, msg = True, ""
        else:
            status, msg = False, "查询数据异常!"
    else:
        status, msg = False, "查询数据异常!"

    control.update({"status": status, "msg": msg})
    print("--------------tf77", control)
    return JsonResponse(control)


@decorator
def alter_layout(request):
    """修改页面布局"""
    dic = request.POST
    user_id = int(dic.get('user_id'))
    user_name = dic.get('user_name')
    phone = str(dic.get('phone'))
    department = dic.get('department')
    control_list = list(eval(dic.get("control_list").encode("utf-8")))

    print("-----------alter_layout:", user_id, user_name, phone, department, control_list)
    LoginInfo.objects.filter(nid=user_id).update(account_name=user_name, department=department, phone=phone)
    Account.objects.filter(nid=user_id).update(control_list=Context.json_dumps(control_list), phone=phone)

    status, msg = True, "修改成功!"
    return JsonResponse({'status': status, "msg": msg})


@decorator
def alter_login_limit(request):
    """修改登录权限"""
    dic = request.POST
    phone = str(dic.get('phone'))
    user_id = dic.get('user_id')
    department = dic.get('department')

    result = LoginInfo.objects.filter(nid=user_id, phone=phone).values('login_limit').first()
    if result:
        status = True
        login_limit = int(result.get("login_limit"))
        if login_limit == 0:
            limit = 1
            msg = "账号开启成功！"
            LoginInfo.objects.filter(nid=user_id, phone=phone).update(login_limit=limit)
        else:
            limit = 0
            msg = "账号禁用成功！"
            LoginInfo.objects.filter(nid=user_id, phone=phone).update(login_limit=limit)
    else:
        status, msg = False, "权限异常!"
    return JsonResponse({"status": status, "msg": msg})


@decorator
def delete_account_data(request):
    """删除登录账号"""
    dic = request.POST
    phone = str(dic.get('phone'))
    user_id = dic.get('user_id')
    department = dic.get('department')

    LoginInfo.objects.filter(nid=user_id, phone=phone).delete()
    Account.objects.filter(nid=user_id, phone=phone).delete()
    status = True
    info = "删除账号成功！"
    return JsonResponse({"status": status, "msg": info})


@decorator
def add_login_info(request):
    """添加登录账号"""
    dic = request.POST
    phone = str(dic.get('phone'))
    user_name = dic.get('user_name')
    department = dic.get('department')
    control_list = list(eval(dic.get("control_list").encode("utf-8")))
    print("-------------------add_login_user", phone,user_name, department)
    if phone and user_name and department:
        create_login_account(user_name, phone, department)
        user_date = LoginInfo.objects.filter(account_name=user_name, phone=phone).values('nid')
        nid = user_date[0].get("nid")
        if nid:
            create_account(nid, phone, control_list)
            status = True
            msg = "添加账号成功!"
        else:
            status = False
            msg = "添加账号失败!"
    else:
        status = False
        msg = "请输入用户名或手机号!"
    return JsonResponse({"status": status, "msg": msg})


def create_login_account(account_name, phone, department):
    import socket
    password = str(Time.current_time('%Y-%m-%d %H:%M:%S'))
    # 得到本地ip
    localIP = socket.gethostbyname(socket.gethostname())
    LoginInfo.objects.create(
        username="admin",
        password=password,
        account_name=account_name,
        limit_level=1,
        login_limit=1,
        limit=1,
        phone=phone,
        department=department,
        ip_address=str(get_host_ip()),
        url="/control_manage/add_login_info/",
        create_time=Time.current_time('%Y-%m-%d %H:%M:%S'),
        login_time=Time.current_time('%Y-%m-%d %H:%M:%S'),
    )


def create_account(nid, phone, control_list):
    Account.objects.create(
        nid=nid,
        phone=phone,
        account_set=0,
        control_list=Context.json_dumps(control_list)
    )


def get_host_ip():
    """查询本机ip地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
