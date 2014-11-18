#!/usr/bin/python
# -*- coding: utf-8 -*-
# utf-8 中文编码
import os

def add_iptables():
    for i in range(8000,8010):
        #os.system("iptables -I INPUT -d 107.170.230.206 -p tcp --dport 8388")
        print ("add %s"%i)
        os.system("iptables -I INPUT  -p tcp --dport %s" %i)
        os.system("iptables -I OUTPUT -p tcp --sport %s"%i)
    pass


if __name__ == '__main__':
    add_iptables()