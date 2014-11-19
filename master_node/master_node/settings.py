#!/usr/bin/python
# -*- coding: utf-8 -*-
# utf-8 中文编码

"""
Django settings for master_node project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""



# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os,sys


# 和ss节点通信加密用的 AES KEY 。
AES_KEY = ''
# SS NODE 监听端口
SS_NODE_LISTENING_PORT= 1531
# 主服务器后台进程监听端口
MASTER_SERVER_LISTENING_PORT= 1530

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = []

# Django 数据库配置
DATABASES = None

# 流量统计间隔(单位分钟)
FLOW_INTERVAL = 5

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# My Shadowsocks 项目目录
MY_SHADOWSOCKS_DIR = os.path.join(BASE_DIR,'../')

sys.path.append(MY_SHADOWSOCKS_DIR)

try:
    import config
    AES_KEY = config.AES_KEY
    SS_NODE_LISTENING_PORT = config.SS_NODE_LISTENING_PORT
    MASTER_SERVER_LISTENING_PORT = config.MASTER_SERVER_LISTENING_PORT
    SECRET_KEY = config.SECRET_KEY
    DEBUG=config.DEBUG
    TEMPLATE_DEBUG = config.DEBUG
    ALLOWED_HOSTS = config.ALLOWED_HOSTS
    DATABASES = config.DATABASES
    FLOW_INTERVAL = config.FLOW_INTERVAL
except ImportError,inst :
    print (u'未找到配置文件，或配置文件错误，请检查。')
    raise inst






AUTH_PROFILE_MODULE = 'master_node.Profile'     #app名称.类名

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/




# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	'master_node',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'master_node.urls'

WSGI_APPLICATION = 'master_node.wsgi.application'


TEMPLATE_DIRS = (
    os.path.abspath(os.path.join(os.path.dirname(__file__),"templates/")),
)
# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'zh-cn'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

DATE_FORMAT = ur'Y-m-d'
DATETIME_FORMAT = ur'Y-m-d G:i'
TIME_FORMAT = ur'G:i'
YEAR_MONTH_FORMAT = ur'Yn'
MONTH_DAY_FORMAT = ur'm-d'
