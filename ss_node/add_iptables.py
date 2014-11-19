#!/usr/bin/python
# -*- coding: utf-8 -*-
# utf-8 中文编码
u""" 为流量统计功能增加 iptables 规则

实测发现在搬瓦工 VPS 上面添加150多个端口的规则时出现 "iptables: Memory allocation problem." 错误.
DO VPS上面添加了500个端口的规则没有任何问题。确认了，是搬瓦工做的限制，下面是详细文档。
egrep "failcnt|numiptent" /proc/user_beancounters
http://wiki.openvz.org/Proc/user_beancounters
http://wiki.openvz.org/Numiptent#numiptent

记录个命令
iptables-save  > /etc/iptables-save
iptables-restore < /etc/iptables-save

"""
import os

# 清空 iptables 规则
#os.system('iptables -F')

def add_iptables():
    for i in range(8000,8500):
        #os.system("iptables -I INPUT -d 107.170.230.206 -p tcp --dport 8388")
        print ("add %s"%i)
        os.system("iptables -I INPUT  -p tcp --dport %s" %i)
        os.system("iptables -I OUTPUT -p tcp --sport %s"%i)
    pass


if __name__ == '__main__':
    add_iptables()