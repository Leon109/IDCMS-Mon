#!/usr/bin/env python
# coding=utf-8

import os
import sys
import json

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.nbnetdb import db
from utils.config import config
from simpleNet.nbNetController import bind_socket, nbNetCtrl

# controller配置文件
#ctrl_conf = config('nbnet', 'controller')

def recv_data(data):
    print data
    #data = json.loads(data):
    if data == "ping":
        return "pong"
    #if data != "ping"

if __name__ == '__main__':
    # 监听地址和端口
    #addr = ctrl_conf['addr']
    #port = int(ctrl_conf['port'])
   
    # 处理程序
    #def logic(data):
    #    recv_data(data)
    #    return("OK")
    
    #sock = bind_socket(addr, port)
    #ctrlD = nbNet(sock, logic)
    
    sock = bind_socket("0.0.0.0", 9000)
    reverseD = nbNetCtrl(sock, recv_data)

    import threading
    class controlThread (threading.Thread):
        '''使用多线程，一个线程运行nbnetCtrl，另一个监控fd状态是否超时'''
        def __init__(self, name):
            threading.Thread.__init__(self)
            self.name = name
    
        def run(self):
            if self.name == 'ctl_start':
                self.ctl_start()
            elif self.name == 'check':
                self.check()

        def ctl_start(self):
            reverseD.run()
    
        def check(self):
            reverseD.check_fd()

    def startTh():
        ctl = controlThread('ctl_start')
        ctl.start()
        check_fd = controlThread('check')
        check_fd.start()
        ctl.join()
        check_fd.join()
    startTh()
