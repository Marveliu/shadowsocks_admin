#!/usr/bin/python
# -*- coding: utf-8 -*-
# utf-8 中文编码

u""" 主节点后台进程

接受网站更新账号请求并批量发送到所有的节点

定时读取流量数据并合并到数据库





 """ 
from SimpleXMLRPCServer import SimpleXMLRPCServer
import xmlrpclib
import json
import os,sys
import hashlib
import thread  
import datetime,time

# DJANGO 配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MY_DJANGO_DIR = os.path.dirname(BASE_DIR)
sys.path.append(MY_DJANGO_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] ='master_node.settings'



import django
django.setup()

from django.conf import settings
from master_node.models import *

# 和ss节点通信加密用的 AES KEY 。
AES_KEY = settings.AES_KEY
# SS NODE 监听端口
SS_NODE_LISTENING_PORT= settings.SS_NODE_LISTENING_PORT
# 主服务器后台进程监听端口
MASTER_SERVER_LISTENING_PORT= settings.MASTER_SERVER_LISTENING_PORT
  
  
import mycrypto
  

def update_ss_config_as_node(host,ss_config,port = SS_NODE_LISTENING_PORT,key = AES_KEY):
    proxy = xmlrpclib.ServerProxy("http://%s:%s/"%(host,port))
    aes_data = xmlrpclib.Binary(mycrypto.encrypt_verify(AES_KEY,json.dumps({'ss_config':ss_config},encoding='utf8')))
    aes_res = proxy.update_ss_config(aes_data)
    res = json.loads( mycrypto.decrypt_verify(AES_KEY,aes_res.data) ,encoding='utf8')
    if res['status']=='ok':
        return True
    else:
        return False


def update_ss_config():
    u""" 更新 ss 配置
本程序会自己取所有用户ss配置，自己取ss节点列表，去批量更新。
"""
    # 获得所有有效用户
    Profiles = Profile.objects.filter(is_full=False,start_date__lte=datetime.now(),end_date__gte=datetime.now())
    ss_config={
         "port_password":{},
         "method":"aes-128-cfb",
         "timeout":600
        }
    for p in Profiles:
        ss_config['port_password']["%s"%p.sport]=p.spass
        
    # 空用户 ss 无法启动，所以这里增加了一个用户，密码是 md5(AES_KEY + x)
    if len(ss_config['port_password'])==0:
        ss_config['port_password']['8000']  = hashlib.md5(AES_KEY + 'dfsgertvgbhb7y4fzyfmjhseg')

    ss_config_json = json.dumps(ss_config,encoding='utf8')
    
    nodes = Node.objects.all()
    for n in nodes:
        print (u'开始更新节点 %s'%n.addr)
        try:
            print (update_ss_config_as_node(n.addr,ss_config_json))
        except Exception,inst:
            print(inst)

def async_update_ss_config(aes_data):
    data = mycrypto.decrypt_verify(AES_KEY,aes_data)
    if data:
        thread.start_new_thread(update_ss_config, ())
        return xmlrpclib.Binary(mycrypto.encrypt_verify(AES_KEY,json.dumps({'status':'ok'})))
    else:
        return xmlrpclib.Binary(json.dumps({'status':'aes_err'}))
    
def get_flow(host):
    proxy = xmlrpclib.ServerProxy("http://%s:%s/"%(host,SS_NODE_LISTENING_PORT))
    aes_data = xmlrpclib.Binary(mycrypto.encrypt_verify(AES_KEY,'1'))
    aes_res = proxy.get_flow(aes_data)
    res_json = mycrypto.decrypt_verify(AES_KEY,aes_res.data)
    return  json.loads( res_json ,encoding='utf8')

def up_flow():
    u""" 更新流量信息 


            # 这里没有处理第一次统计之前的流量，也就是第一次统计之后的流量才被计算
            # 同样没有处理 ss 节点重启后第一次流量统计之前的流量。
            # 主要为了防止之后增加端口更换功能造成用户流量被误统计。

获得流量数据
获得账号信息
根据账号绑定流量信息  # 有些流量信息是无效的，是空用户
查询上一次的流量信息及刷出这次的流量
保存本次流量纪录
更新账号流量信息"""
    now = datetime.now()
    node_flow = []
    nodes = Node.objects.all()
    for n in nodes:
        print (u'%s 开始获得节点 %s 的流量信息'%(now,n.addr))
        try:
            f = get_flow(n.addr)
            f['node_id']=n.id
            f['node_name']=n.name
            f['node_addr']=n.addr
            node_flow.append(f)
            print f
        except Exception,inst:
            print(inst)
    # 获得所有有效用户
    Profiles = Profile.objects.filter(is_full=False,start_date__lte=datetime.now(),end_date__gte=datetime.now())
    for p in Profiles:
        for n in node_flow:
            if not n['flow_in'].has_key(unicode(p.sport)):
                print u'[错误][流量统计] 节点 %s(%s) iptables 未统计用户id:%s 端口 %s 的进站流量！' %(n['node_name'],n['node_addr'],p.user_id,p.sport)
                continue
            if not n['flow_out'].has_key(unicode(p.sport)):
                print u'[错误][流量统计] 节点 %s(%s) iptables 未统计用户id:%s 端口 %s 的出站流量！' %(n['node_name'],n['node_addr'],p.user_id,p.sport)
                continue

            # 本次统计到的原始流量(节点端口开放至今的流量)
            original_in_flow = n['flow_in'][unicode(p.sport)]
            original_out_flow = n['flow_out'][unicode(p.sport)]

            #当前用户本节点所有已用流量
            all_flow_in = 0
            all_flow_out = 0

            # 当前用户本节点本次统计增加
            flow_in = 0
            flow_out = 0

            flow_old_log_list = Flow.objects.filter(user_id=p.user_id,node_id=n['node_id']).order_by('-time')[:1]
            flow_old_log = None
            if len(flow_old_log_list) >0:
                flow_old_log=flow_old_log_list[0]
            if flow_old_log:
                all_flow_in = flow_old_log.all_in_flow
                all_flow_out = flow_old_log.all_out_flow
                if flow_old_log.port==p.sport :
                # 这里限制仔细点，宁愿漏掉一次统计也别多统计
                    if original_in_flow > flow_old_log.original_in_flow  and original_out_flow > flow_old_log.original_out_flow:
                        flow_in = original_in_flow - flow_old_log.original_in_flow
                        flow_out = original_out_flow - flow_old_log.original_out_flow
                        all_flow_in +=flow_in
                        all_flow_out +=flow_out

            flow_new_log = Flow(user_id=p.user_id,port=p.sport,node_id=n['node_id'],time=now,
                                original_in_flow=original_in_flow,original_out_flow=original_out_flow,
                                in_flow = flow_in,out_flow=flow_out,
                                all_in_flow = all_flow_in,all_out_flow=all_flow_out)

            p.used_flow =p.used_flow + (  flow_in + flow_out )
            flow_new_log.save()
        if (p.used_flow>p.all_flow):
            p.is_full = True
        p.save()

    
def while_up_flow():
    minute = -1
    FLOW_INTERVAL = settings.FLOW_INTERVAL

    while(1):
        now = datetime.now()
        if now.minute % FLOW_INTERVAL == 0 and now.minute != minute:
            print(u'%s 开始统计流量' % now)
            minute = now.minute
            up_flow()
#            try:
 #               up_flow()
#            except Exception,inst:
#                print(inst)
        else:
            time.sleep(10)


thread.start_new_thread(while_up_flow, ())

server = SimpleXMLRPCServer(('127.0.0.1', MASTER_SERVER_LISTENING_PORT))
print u"Listening on port %s..."%MASTER_SERVER_LISTENING_PORT

server.register_function(async_update_ss_config, 'update_ss_config')
server.serve_forever()
