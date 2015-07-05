#!/usr/bin/env python

'''Function Filter
检测客户端发送数据有误异常
'''

import os
import sys
import json

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.config import config
from simpleNet.nbNetFramework import bind_socket, nbNet

ff_conf = config('nbnet', 'ff')
host_alarm = config('alarm', 'host_alarm') 

alarmStatus = {}

def ff(data):
    '''根据host_alarm获取的值与获取的数据类型进行比较'''
    mon_data = json.loads(data)
    alarm_list = list(host_alarm)
    for key in alarm_list:
        mon_value = mon_data[key]
        alarm_value = host_alarm[key]
        eval_function = str(mon_value) + alarm_value
        ff_result = eval(eval_function)
        if ff_result:
            alarmStatus[key] = True
        else:
            if alarmStatus.pop(key, False):
                alarmStatus[key] = False
                print "Recover", eval_function
    

if __name__ == '__main__':
    addr = ff_conf['addr']
    port = int(ff_conf['port'])
   
    def logic(data):
        ff(data)
        return("OK")
    
    sock = bind_socket(addr, port)
    saverD = nbNet(sock, logic)
    saverD.run()
