#!/usr/bin/env python
# coding=utf-8

import os
import sys
import json

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.nbnetdb import db
from utils.config import config
from simpleNet.nbNetController import bind_socket, nbNet

# controller配置文件
ctrl_conf = config('nbnet', 'controller')

def recv_data(data):
    data = json.loads(data):
        if data == "ping":
            return "pong"

if __name__ == '__main__':
    # 监听地址和端口
    addr = ctrl_conf['addr']
    port = int(ctrl_conf['port'])
   
    # 处理程序
    def logic(data):
        recv_data(data)
        return("OK")
    
    sock = bind_socket(addr, port)
    ctrlD = nbNet(sock, logic)
