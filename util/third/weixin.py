# -*- coding: utf-8 -*-
from util.context import Context
import urllib

Url_Login = "https://open.weixin.qq.com/connect/qrconnect?"
Url_Redirect = 'http://ttbngm.ximaowangluo.com:20001'
Url_Code = 'https://api.weixin.qq.com/sns/oauth2/access_token?'
Url_Refresh = "https://api.weixin.qq.com/sns/oauth2/refresh_token?"
Url_UserInfo = "https://api.weixin.qq.com/sns/userinfo?"

APP_ID = "wx9927f6083cf5595b"
APP_SECRET = "d4898c0df999b0b419375f9d76fb1a8e"


def get_WeChat_jump(request_url):
    open_url = "{}{}".format(Url_Redirect, request_url)
    print("------open_url-----", open_url)
    deal_url = urllib.quote(open_url)
    print("------deal_url-----", deal_url)
    redirect_url = "{}appid={}&redirect_uri={}&response_type=code&scope=snsapi_login&state=STATE".format(Url_Login, APP_ID, deal_url)
    return redirect_url


def get_WeChat_login_info(code):
    access_url = "{}appid={}&secret={}&code={}&grant_type=authorization_code".format(Url_Code, APP_ID, APP_SECRET, code)
    print("------access_url-----", access_url)
    result = Context.Controller.urllib2_get(access_url)
    print("------access_token-----", result)
    if result.has_key("access_token"):
        access_token = result["access_token"]
        openid = result["openid"]
    else:
        refresh_url = "{}appid={}&grant_type=refresh_token&refresh_token=REFRESH_TOKEN".format(Url_Refresh, APP_ID)
        refresh = Context.Controller.urllib2_get(refresh_url)
        access_token = refresh["access_token"]
        openid = refresh["openid"]
    # 微信用户信息
    user_url = "{}access_token={}&openid={}&lang=zh_CN".format(Url_UserInfo, access_token, openid)
    user_info = Context.Controller.urllib2_get(user_url)
    return user_info


