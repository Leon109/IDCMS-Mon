#!/usr/bin/env python
# coding=utf-8

import os
import sys

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.monconf import config
#from utils.senddata import sendData_mh
from nbnet.nbnet_framework import bind_socket, nbNet

# 导入配置文件
trans_conf = config('mon.conf', 'trans')
# 监控服务器列表
ff_l = trans_conf['ff_l'].split(';')
# 服务器主机列表
saver_l = trans_conf['saver_l'].split(';')
# ff 和 saver的soket，使用列表，具体参考sendData_mh
# ff socket
ff_sock_l = [None]
# saver socket
saver_sock_l = [None]

# 发送给服务端data是发送的数据
def sendsaver(saver_l, data, sock_l):
    return sendData_mh(saver_l, data, sock_l)

#发送给监控端
def sendff(ff_l, data, sock_l):
    return sendData_mh(ff_l, data, sock_l)

if __name__ == '__main__':
    # 监听地址和端口
    addr = trans_conf['addr']
    port = int(trans_conf['port'])
    
    # 处理程序
    def logic(data):
        print data
        #ff_ret = sendff(ff_l, data, ff_sock_l)
        #saver_ret = sendsaver(saver_l, data, saver_sock_l)
        # 一般情况只判断监控收到就可以了
        #if ff_ret:
        return("OK")
        #else:
        #    return("ER")
    
    # 启动服务
    sock = bind_socket(addr, port)
    transD = nbNet(sock, logic)
    transD.run()
