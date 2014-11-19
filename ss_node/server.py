#!/usr/bin/python
# -*- coding: utf-8 -*-
# utf-8 中文编码

u""" ss 节点管理

需实现的功能：

    1.接收主节点推送的账号更新，并处理
    2.读取流量
    3.读取ss日志并推送到主服务器（用来统计账号在线信息）
    4.定时通知服务器本节点健康状态。
    
注意：统计流量功能需要 root 权限。
 """

from SimpleXMLRPCServer import SimpleXMLRPCServer
import xmlrpclib
import json
import os,sys
import time, sys,iptc



# My Shadowsocks 项目目录
MY_SHADOWSOCKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(MY_SHADOWSOCKS_DIR)

# 和主节点通信加密用的 AES KEY 。
AES_KEY = ''
# SS NODE 监听端口
SS_NODE_LISTENING_PORT= 1531
# ss 配置文件路径
SS_CONFIG_PATH = ''

import mycrypto

try:
    import config
    AES_KEY = config.AES_KEY
    SS_NODE_LISTENING_PORT = config.SS_NODE_LISTENING_PORT
    SS_CONFIG_PATH=config.SS_CONFIG_PATH

except ImportError,inst :
    print (u'未找到配置文件，或配置文件错误，请检查。')
    raise inst









server = SimpleXMLRPCServer(('0.0.0.0', SS_NODE_LISTENING_PORT))
print (u"Listening on port %s..."%SS_NODE_LISTENING_PORT)
 

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
    return xmlrpclib.Binary(mycrypto.encrypt_verify(AES_KEY,json.dumps({'status':'ok'},encoding='utf8')))
 
def get_flow(aes_data):
    u'''''' 
    text = mycrypto.decrypt_verify(AES_KEY,aes_data.data)
    if text == None:return xmlrpclib.Binary(json.dumps({'statos':'err_ase'},encoding='utf8'))

    res={
            'flow_in':{},  # {u'8001':3916788L}
            'flow_out':{},
            'status':'ok'
        }


    table = iptc.Table(iptc.Table.FILTER)

    chain_in = iptc.Chain(table, 'INPUT')
    chain_out = iptc.Chain(table, 'OUTPUT')

    table.refresh()

    for rule in chain_out.rules:
        try:
            if len(rule.matches)==1:
                sport = int(rule.matches[0].sport)
                res['flow_out'][sport] = rule.get_counters()[1]
        except Exception,inst:
            print (u'[警告]未知的 iptables 规则，如果是其他软件添加的可以忽略。')
            print(inst)
    for rule in chain_in.rules:
        try:
            if len(rule.matches)==1:
                dport = int(rule.matches[0].dport)
                res['flow_in'][dport] = rule.get_counters()[1]
        except Exception,inst:
            print (u'[警告]未知的 iptables 规则，如果是其他软件添加的可以忽略。')
            print(inst)


    return xmlrpclib.Binary(mycrypto.encrypt_verify(AES_KEY,json.dumps(res,encoding='utf8')))




server.register_function(update_ss_config, 'update_ss_config')
server.register_function(get_flow, 'get_flow')
server.serve_forever()
