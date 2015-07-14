#!/usr/bin/env python
# coding=utf-8

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

# ff配置文件
ff_conf = config('nbnet', 'ff')
host_alarm = config('alarm', 'host_alarm') 

# alarm 状态记录字典
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
            # 如果结果成立发送报警
            alarmStatus[key] = True
        else:
            # 如果结果不成立，先判断原来的状态是报警状态改为恢复状态
            # 这里给个默认值因为如果第一次判断没有触发报警，不然会出现异常
            if alarmStatus.pop(key, False):
                alarmStatus[key] = False
                print "Recover", eval_function
    

if __name__ == '__main__':
    # 监听地址和端口
    addr = ff_conf['addr']
    port = int(ff_conf['port'])
   
    # 处理程序
    def logic(data):
        ff(data)
        return("OK")
    
    sock = bind_socket(addr, port)
    saverD = nbNet(sock, logic)
    saverD.run()
