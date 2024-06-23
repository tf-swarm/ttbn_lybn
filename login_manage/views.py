# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render_to_response, render, redirect,HttpResponse
from util.context import Context
from util.process import ProcessInfo
from django.http import HttpRequest,HttpResponse,JsonResponse,HttpResponseRedirect
from .models import *
from control_manage.models import Account
from django.views.decorators.csrf import csrf_exempt
from PIL import Image, ImageDraw, ImageFont
import json
import datetime
import time
from util.tool import Time
import random
from util.globals import Global, GlobalEnum
from hashlib import sha1
import random
# Create your views here.


def decorator(func):
    def wrapper(request, *args, **kwargs):
        phone = request.session.get('uid')
        access_token = request.COOKIES.get('user')
        if phone is None or access_token is None:
            return redirect('/login/')
        else:
            user_name = LoginInfo.objects.filter(phone=phone).first()
            if user_name:
                s1 = sha1()
                s1.update(str(user_name.nid))
                # 加密后的十六进制的值
                user_token = s1.hexdigest()
                if access_token == user_token:
                    return func(request, *args, **kwargs)
                else:
                    return redirect('/login/')
            else:
                return redirect('/login/')
    return wrapper


def main_login(request):
    if request.method == 'POST':
        # 获取表单用户密码
        dic = request.POST
        phone = dic.get('phone').encode('utf-8')
        verify = dic.get('verify', 0)

        # 获取的表单数据与数据库进行比较
        context = {'error_verify': 0, 'error_phone': 0}
        user_name = LoginInfo.objects.filter(phone=phone)

        if user_name:
            user_date = LoginInfo.objects.filter(phone=phone).values('login_limit')
            login_limit = int(user_date[0].get("login_limit"))
            if login_limit == 1:
                day_time = int(time.time()-10*60)
                auth_code = VerifyCode.objects.filter(phone=phone)
                if auth_code:
                    verify_time = VerifyCode.objects.get(phone=phone)
                    loc_time = Time.datetime_to_timestamp(verify_time.times)

                    if day_time > loc_time:
                        verify_time.verify = ProcessInfo.generate_verification_code()
                        verify_time.times = Time.timestamp_to_str(int(time.time()))
                        verify_time.save()

                    check_code = VerifyCode.objects.filter(phone=phone, verify=verify)
                    if check_code:
                        code_info = VerifyCode.objects.get(phone=phone)
                        verify_time.times = Time.timestamp_to_str(int(time.time()))
                        code_info.verify = ProcessInfo.generate_verification_code()
                        code_info.save()
                        s1 = sha1()
                        s1.update(str(user_name[0].nid))
                        user_info = s1.hexdigest()
                        request.session['uid'] = user_name[0].phone
                        response = redirect('/')
                        # response.set_signed_cookie('user', user_name[0].nid, salt='ximao2019',expires=60 * 60 * 24 * 1)  #1天 带签名的cookie(加盐)
                        response.set_cookie('user', user_info, expires=60 * 60 * 24 * 1)  # 1天
                        return response
                    else:
                        context['error_verify'] = 1
                        return render(request, 'login_manage/login.html', context)
                else:
                    context['error_verify'] = 1
                    return render(request, 'login_manage/login.html', context)
            else:
                context['error_phone'] = 1
                return render(request, 'login_manage/login.html', context)
        else:
            context['error_phone'] = 1
            return render(request, 'login_manage/login.html', context)
    else:
        return render(request, 'login_manage/login.html')


@decorator
def main_show(request):
    return render(request, 'login_manage/main.html')


@decorator
def main_top_show(request):
    return render(request, 'login_manage/top.html')


# 退出登陆
def login_out(request):
    response = HttpResponseRedirect('/login/')
    response.delete_cookie('user')
    request.session.flush()
    return response


@decorator
def main_left_show(request):
    phone = request.session.get('uid')
    user_date = LoginInfo.objects.filter(phone=phone).values('nid')
    nid = user_date[0].get("nid")
    user = Account.objects.filter(nid=nid, phone=phone).values("account_set", "control_list").first()
    if user:
        account_limit = str(user.get("account_set"))
        control_info = Context.json_loads(user.get("control_list"))
        control_list = [str(n) for n in control_info]
        channel_and_product(request)
    else:
        control_list, account_limit = [], "0"
    left_info = {"control": control_list, "account_limit": account_limit}
    return render(request, 'login_manage/left.html', left_info)


@decorator
def main_index_show(request):
    return render(request, 'login_manage/index.html')


@decorator
def main_right_show(request):
    return render(request, 'login_manage/right.html')


def channel_and_product(request):
    bool_type = True
    context = {}
    deal_channel = ["1001_1", "1001_2", "1001_3", "1001_4", "1001_5", "1003_1", "1004_1", "1005_1", "1006_0",
                    "1007_1", "1008_0", "1008_1", "1000_1", "1000_2", "1000_3", "888", "1000_0"]
    url = '/v2/shell/background/get_channel_list'
    context.update({"phone": request.session.get('uid')})
    ret = Context.Controller.request(url, context)
    channel_list = Context.json_loads(ret.content)
    if "ret" not in channel_list:
        print("-----------No_channel")
        bool_type = False
    else:
        channel_info = []
        deal_info = channel_list["ret"]
        ChannelList.objects.all().delete()
        for channel, name in deal_info.items():
            if channel in deal_channel:
                del deal_info[channel]
            else:
                continue
        new_data = ChannelList(
            channel_data=Context.json_dumps(deal_info)
        )
        channel_info.append(new_data)
        ChannelList.objects.bulk_create(channel_info)

    deal_product = ["103201", "103202", "103203", "103204", "103205", "103206"]
    url = '/v2/shell/get_product_list'
    context.update({"phone": request.session.get('uid')})
    ret = Context.Controller.request(url, context)
    product_list = Context.json_loads(ret.content)
    if "ret" not in product_list:
        print("-----------No_product")
        bool_type = False
    else:
        product_info = []
        ProductList.objects.all().delete()
        for key, value in product_list["ret"].items():
            keys = key.encode('utf-8')
            if keys not in deal_product:
                new_data = ProductList(
                    product_id=keys,
                    product_data=Context.json_dumps(value)
                )
                product_info.append(new_data)
            else:
                continue
        ProductList.objects.bulk_create(product_info)
    return bool_type


def verify_code(request):
    # 引入随机函数模块
    import random
    # 定义变量，用于画面的背景色、宽、高
    bgcolor = (random.randrange(20, 100), random.randrange(20, 100), 255)
    width = 100
    height = 25
    # 创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)  # "#F0F8FF"

    # 创建画笔对象
    draw = ImageDraw.Draw(im)
    # 调用画笔的point()函数绘制噪点
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    # 定义验证码的备选值
    str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]
    # 构造字体对象，ubuntu的字体路径为“/usr/share/fonts/truetype/freefont”
    font = ImageFont.truetype('FreeMono.ttf', 23)
    # 构造字体颜色
    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    # 绘制4个字
    draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
    draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
    draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
    draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
    # 释放画笔
    del draw
    # 存入session，用于做进一步验证
    request.session['verifycode'] = rand_str
    """
    python2的为
    # 内存文件操作
    import cStringIO
    buf = cStringIO.StringIO()
    """
    # 内存文件操作-->此方法为python3的
    import io
    buf = io.BytesIO()
    # 将图片保存在内存中，文件类型为png
    im.save(buf, 'png')
    # 将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'image/png')


def get_VerifyCode(request):
    dic = request.POST
    phone = dic.get('phone')
    """获取验证码"""

    url = '/v1/shell/gm/getMVerifyCode'

    context = {'mobile': phone}

    ret = Context.Controller.request(url, context)
    result = Context.json_loads(ret.content)
    print("-----code",result)
    code = result["code"]

    code_info = VerifyCode.objects.filter(phone__exact=phone)

    day_time = Time.timestamp_to_str(int(time.time()))
    if len(code_info) > 0:
        code_info.update(
            verify=code,
            times=day_time
        )
    else:
        VerifyCode.objects.create(
            phone=phone,
            verify=code,
            times=day_time
        )
    ok = 1
    return HttpResponse(json.dumps({'ok': ok}), content_type="application/json")


def check_phone(request):
    """验证账号"""
    dic = request.POST
    phone = dic.get('phone')
    user = LoginInfo.objects.filter(phone=phone)
    user_date = LoginInfo.objects.filter(phone=phone).values('login_limit')
    if user_date:
        login_limit = int(user_date[0].get("login_limit"))
        # 3.判断两个验证码是否相同
        if user and login_limit == 1:
            result = {'result': 1}
            return JsonResponse(result)
        else:
            result = {'result': 0}
            return JsonResponse(result)
    else:
        result = {'result': 0}
        return JsonResponse(result)

@csrf_exempt
def page_permission_denied(request):
    return render_to_response('login_manage/403.html')


# 404页面
@csrf_exempt
def page_not_found(request):
    return render_to_response('login_manage/404.html')


@csrf_exempt
def page_error(request):
    return render_to_response('login_manage/500.html')