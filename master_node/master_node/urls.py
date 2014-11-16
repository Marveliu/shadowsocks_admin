#!/usr/bin/python
# -*- coding: utf-8 -*-
# utf-8 中文编码

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = patterns('master_node.views',
    # Examples:
    # url(r'^$', 'master_node.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
	# 首页
	url(r'^$',  'index',name='index'),
	
	# 重置密码页
	(r'^accounts/register/$',  'register',),
	(r'^accounts/login/$',  login,),
	(r'^accounts/profile/$',  'profile',),
    (r'^accounts/logout/$', 'logout'),


    url(r'^admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
