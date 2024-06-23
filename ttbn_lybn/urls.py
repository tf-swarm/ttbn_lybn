"""ttbn_lybn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include

urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^', include('login_manage.urls', namespace='login_manage')),
    url('^control_manage/', include('control_manage.urls', namespace='control_manage')),
    url('^currency_total/', include('currency_total.urls', namespace='currency_total')),
    url('^users_manage/', include('users_manage.urls', namespace='users_manage')),
    url('^limit_time_shop/', include('limit_time_shop.urls', namespace='limit_time_shop')),
    url('^run_manage/', include('run_manage.urls', namespace='run_manage')),
    url('^gift_bag_shop/', include('gift_bag_shop.urls', namespace='gift_bag_shop')),
    url(r'^activity_manage/', include('activity_manage.urls', namespace='activity_manage')),
    url(r'^arena_manage/', include('arena_manage.urls', namespace='arena_manage')),
    url(r'^redeem_code/', include('redeem_code.urls', namespace='redeem_code')),
    # url(r'^mini_game/', include('mini_game.urls', namespace='mini_game')),
]
