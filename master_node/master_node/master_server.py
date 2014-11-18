#!/usr/bin/python
# -*- coding: utf-8 -*-
# utf-8 中文编码

u""" 主节点后台进程

接受网站更新账号请求并批量发送到所有的节点



 """ 
from SimpleXMLRPCServer import SimpleXMLRPCServer
import xmlrpclib
import json
import mycrypto
import os,sys
import hashlib
import thread  

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
LISTENING_PORT= settings.LISTENING_PORT
  
  
  

def update_ss_config_as_node(host,ss_config,port = SS_NODE_LISTENING_PORT,key = AES_KEY):
    proxy = xmlrpclib.ServerProxy("http://%s:%s/"%(host,port))
    aes_data = xmlrpclib.Binary(mycrypto.encrypt_verify(AES_KEY,json.dumps({'ss_config':ss_config},encoding='utf8')))
    aes_res = proxy.update_ss_config(aes_data)
    res = json.loads( mycrypto.decrypt_verify(AES_KEY,aes_res.data) ,encoding='utf8')
    if res['statos']=='ok':
        return True
    else:
        return False


def update_ss_config():
    u""" 更新 ss 配置
本程序会自己取所有用户ss配置，自己取ss节点列表，去批量更新。
"""
    # 获得所有用户
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
        update_ss_config_as_node(n.addr,ss_config_json)

def async_update_ss_config(aes_data):
    data = mycrypto.decrypt_verify(AES_KEY,aes_data)
    if data:
        thread.start_new_thread(update_ss_config, ())
        return xmlrpclib.Binary(mycrypto.encrypt_verify(AES_KEY,json.dumps({'status':'ok'})))
    else:
        return xmlrpclib.Binary(json.dumps({'status':'aes_err'}))
    

server = SimpleXMLRPCServer(('127.0.0.1', LISTENING_PORT))
print u"Listening on port %s..."%LISTENING_PORT

server.register_function(async_update_ss_config, 'update_ss_config')
server.serve_forever()
