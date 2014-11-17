#!/usr/bin/python
# -*- coding: utf-8 -*-
# utf-8 中文编码

u""" ss 节点管理

需实现的功能：

    1.接收主节点推送的账号更新，并处理
    2.读取流量并推送到服务器
    3.维护ss正常运行
    4.读取ss日志并推送到主服务器（用来统计账号在线信息）
    5.定时通知服务器本节点健康状态。
    
    实际只打算在本文件实现<1>功能。
 """

from SimpleXMLRPCServer import SimpleXMLRPCServer
import xmlrpclib
import json
import mycrypto
import os

BASE_DIR = os.path.dirname(__file__)

# 和主节点通信加密用的 AES KEY 。
AES_KEY = 'dsfsrt45gbi6h7beabsyrhyuj6gwaggi8eguf2setf4gf7wfwdfseg3bvtss'
# 监听端口
LISTENING_PORT= 1531
# ss 配置文件路径
SS_CONFIG_PATH = os.path.join(BASE_DIR,'config.json')


server = SimpleXMLRPCServer(('0.0.0.0', LISTENING_PORT))
print u"Listening on port %s..."%LISTENING_PORT
 

def update_ss_config(aes_data):
    u""" 更新 ss config 接口

    注意，数据要使用 AES 加密。
    解密后的格式为
    {
        'ok':hash 后的 AES_KEY +'test 串' ，用来确认安全 
        'ss_config':config.json 文件内容
    }
    
    返回值：同样加密了。
    
    在解密失败的情况下不会再返回加密信息了，直接返回原文。
"""
    text = mycrypto.decrypt_verify(AES_KEY,aes_data.data)
    if text == None:return xmlrpclib.Binary(json.dumps({'statos':'err_ase'},encoding='utf8'))
    r = json.loads(text,encoding='utf8')
    with open(SS_CONFIG_PATH,'wb') as file:
        file.write(r['ss_config'])
    os.system('killall -HUP shadowsocks-server')
    return xmlrpclib.Binary(mycrypto.encrypt_verify(AES_KEY,json.dumps({'statos':'ok'},encoding='utf8')))
 
server.register_function(update_ss_config, 'update_ss_config')
server.serve_forever()
