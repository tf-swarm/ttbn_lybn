# -*- coding: utf-8 -*-
"""
Django settings for ttbn_lybn project.

Generated by 'django-admin startproject' using Django 2.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import time

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6y_qo+gqq4d^lu6mx^i*035@m%(@!3%i4*+x8+ocap0rhm1(rr'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['ttbngm.ximaowangluo.com', '0.0.0.0:10001']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',

    'login_manage',
    'control_manage',
    'currency_total',
    'users_manage',
    'limit_time_shop',
    'limit_time_shop.templatetags',
    'gift_bag_shop',
    'run_manage',
    'activity_manage',
    'arena_manage',
    'mini_game',
    'redeem_code',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'login_manage.middleware.ApiLoggingMiddleware',
]

ROOT_URLCONF = 'ttbn_lybn.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ttbn_lybn.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'XiMao2019', 
        'USER': 'root',
        'PASSWORD': 'mysql2019',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'static/media')

cur_path = os.path.dirname(os.path.realpath(__file__))  # log_path是存放日志的路径
log_path = os.path.join(os.path.dirname(cur_path), 'logs')
if not os.path.exists(log_path): os.mkdir(log_path)  # 如果不存在这个logs文件夹，就自动创建一个

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        # 日志格式
        'standard': {
            'format': '[%(asctime)s] [%(filename)s:%(lineno)d] [%(module)s:%(funcName)s] '
                      '[%(levelname)s]- %(message)s'},
        'simple': {  # 简单格式
            'format': '%(levelname)s %(message)s'
        },
    },
    # 过滤
    'filters': {
        # 'require_debug_false': {
        #     '()': 'django.utils.log.RequireDebugFalse'
        # }
    },
    # 定义具体处理日志的方式
    'handlers': {
        # 控制台输出
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        # 默认记录所有日志
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_path, 'all-{}.log'.format(time.strftime('%Y-%m-%d'))),
            'maxBytes': 1024 * 1024 * 30,  # 文件大小
            'formatter': 'standard',  # 输出格式
            'encoding': 'utf-8',  # 设置默认编码，否则打印出来汉字乱码
            # 保存 60 天
            'backupCount': 60,
        },
        # 输出info日志
        'info': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_path, 'info-{}.log'.format(time.strftime('%Y-%m-%d'))),
            'maxBytes': 1024 * 1024 * 30,
            'backupCount': 60,
            'formatter': 'standard',
            'encoding': 'utf-8',  # 设置默认编码
        },
        # 输出错误日志
        # 'error': {
        #     'level': 'ERROR',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': os.path.join(log_path, 'error-{}.log'.format(time.strftime('%Y-%m-%d'))),
        #     'maxBytes': 1024 * 1024 * 30,   # 日志文件的最大值,设置30M
        #     'backupCount': 6,  # 备份数
        #     'formatter': 'standard',  # 输出格式
        #     'encoding': 'utf-8',  # 设置默认编码
        # },
    },
    # 配置用哪几种 handlers 来处理日志
    'loggers': {
        # 类型 为 django 处理所有类型的日志， 默认调用
        'django': {
            'handlers': ['default', 'console'],
            'level': 'INFO',
            'propagate': False
        },
        # log 调用时需要当作参数传入
        'log': {
            'handlers': ['info', 'console', 'default'],  # 'error',
            'level': 'INFO',
            'propagate': True
        },
    }
}
# STATIC_ROOT = 'static'

# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# CRONJOBS = [
# 每5分钟执行一次
#     ('*/5 * * * *', 'appname.cron.test','>>/home/test.log')
# ]

# 定时任务
CRONJOBS = [
    ('01 3 * * *', 'run_manage.timers.crontab.t_order_query', '>>/home/order_query_task.log'),
    ('10 3 * * *', 'currency_total.timers.crontab.Calc_Coupon_Rate', '>>/home/Calc_Coupon_Rate.log'),
    ('45 3 * * *', 'run_manage.timers.crontab.t_query_game_data', '>>/home/query_game_data.log'),
    ('55 3 * * *', 'run_manage.timers.crontab.t_query_run_data', '>>/home/query_run_data.log'),
    ('59 3 * * *', 'run_manage.timers.crontab.deal_retention_ltv', '>>/home/deal_retention_ltv.log'),
    ('*/10 * * * *', 'run_manage.timers.crontab.half_hour_request_data', '>>/home/half_hour_request.log'),
]
