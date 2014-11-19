#!/usr/bin/python
# -*- coding: utf-8 -*-
# utf-8 中文编码
from django.db import models
from django.contrib import admin
from datetime import datetime,date,timedelta
import settings
import json,os,string,random
from SimpleXMLRPCServer import SimpleXMLRPCServer
import xmlrpclib
import json
import mycrypto


from django.contrib.auth.models import User

def GenPassword(length):
    chars=string.ascii_letters+string.digits
    return ''.join([random.choice(chars) for i in range(length)])#

class Profile(models.Model):
    u'''帐号附加信息'''

    user = models.ForeignKey(User,unique=True)  #User 外键且唯一
    sport = models.IntegerField()#ss端口
    spass = models.CharField(max_length=20, default='')#s密码
    smethod = models.CharField(max_length=20, default='aes-128-cfb') #加密方式
    used_flow = models.BigIntegerField(default=0)#当月已用流量
    all_flow = models.BigIntegerField(default=10*1024*1024*1024)#当月总流量
    start_date = models.DateTimeField(auto_now_add=True)#开始日期
    now_date = models.DateTimeField(auto_now_add=True)#当前统计月
    end_date = models.DateTimeField()#结束日期
    is_full = models.BooleanField(default=False)  #是否流量用尽
  
    def is_warning(self):
        u"""流量是否警告   注意没有管 is_full """        
        if  self.flow_proportion()>0.8 :
            return True
        return False
    def flow_proportion(self):
        return float(self.used_flow)/self.all_flow
    def flow_proportion_100(self):
        return float(self.used_flow)/self.all_flow * 100

    class Meta:
        verbose_name = u'账号'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.user.username
        



        
class ProfileAdmin(admin.ModelAdmin):
    list_display = (u'user',u'sport',u'spass',u'smethod',u'used_flow','all_flow',u'start_date',u'end_date','is_full')
    search_fields = (u'user',)
    ordering =(u'user',u'sport',u'used_flow',u'all_flow',u'start_date',u'end_date',u'is_full')
        
admin.site.register(Profile,ProfileAdmin)

def get_profile(user):
    #TODO: 这里没有考虑建立账号是未建立 Profile 的情况。 
    
    res = None
    try:
        res = Profile.objects.get(user=user)
    except:
        res = Profile(user=user,
                              sport=8000+user.id,
                              spass=GenPassword(10),
                              start_date=datetime.now(),
                              now_date=datetime.now(),
                              end_date=datetime.now())
        res.save()

    return res

def up_user(): 
    u"""更新了user后调用的方法。通知主服务器"""
    proxy = xmlrpclib.ServerProxy("http://127.0.0.1:%s/"%(settings.MASTER_SERVER_LISTENING_PORT))
    proxy.update_ss_config(mycrypto.encrypt_verify(settings.AES_KEY,1))
    
    

    
class Flow(models.Model):
    u'''流量统计表'''

    user = models.ForeignKey(User,unique=True)  #User 外键且唯一
    time= models.DateTimeField(auto_now_add=True)#统计时间
    original_in_flow = models.BigIntegerField(default=0)#原始入站流量
    original_out_flow = models.BigIntegerField(default=0)#原始入站流量
    in_flow = models.BigIntegerField(default=0)#本次入站流量
    out_flow = models.BigIntegerField(default=0)#本次入站流量本次
    all_in_flow = models.BigIntegerField(default=0)#单节点所有入站流量
    all_out_flow = models.BigIntegerField(default=0)#单节点所有入站流量本次
    port = models.IntegerField()#ss端口
    node_id = models.IntegerField()#节点id
    

    def __unicode__(self):
        return "%s %s" %(self.user.username ,self.time)
    
    class Meta:
        verbose_name = u'流量统计'
        verbose_name_plural = verbose_name

        
class FlowAdmin(admin.ModelAdmin):
    list_display = (u'user',u'time',u'original_in_flow',u'original_out_flow',u'in_flow','out_flow',u'port',u'node_id')
    search_fields = (u'user',)
    ordering =(u'user',u'time',u'original_in_flow',u'original_out_flow',u'in_flow',u'out_flow',u'port',u'node_id')
        
admin.site.register(Flow,FlowAdmin)



class Node(models.Model):
    u'''节点表'''
    name = models.CharField(max_length=20, default='') #节点名
    addr = models.CharField(max_length=100, default='127.0.0.1') #节点地址

    

    def __unicode__(self):
        return self.name 
    
    class Meta:
        verbose_name = u'节点'
        verbose_name_plural = verbose_name

        
class NodeAdmin(admin.ModelAdmin):
    list_display = (u'name',u'addr')
    search_fields = (u'name',)
    ordering =(u'name',u'addr')
        
admin.site.register(Node,NodeAdmin)







