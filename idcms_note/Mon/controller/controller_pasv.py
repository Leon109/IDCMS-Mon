#!/usr/bin/env python
# coding=utf-8

import os
import sys
import json

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.config import config
from utils.crypt import encrypt,decrypt
from utils.sys_cmd import Command, get_iphostname
from simpleNet.nbNetFramework import bind_socket, nbNet

ctrl_conf = config('nbnet', 'controller')

# 监听地址和端口
addr = ctrl_conf['addr']
port = int(ctrl_conf['port'])
def_timeout = ctrl_conf['timeout']

#处理程序
def logic(data):
    dec_data = decrypt(data)
    data = json.loads(dec_data)
    if "cmd" in data:
        send_data = get_iphostname()
        cmd = data['cmd']
        timeout =  data.get("timeout", def_timeout)
        command = Command(cmd)
        recode, output, error = command.run(int(timeout))
        if not recode:
            print recode
            # 如国命令执行成功
            send_data['result'] = output
        else:
            print recode
            # 如国命令执行失败
            send_data['result'] = error
        send_data['cmd'] = cmd
        enc_data = json.dumps(send_data)
        return encrypt(enc_data)
    else:
        return encrypt("input error")
    
sock = bind_socket(addr, port)
saverD = nbNet(sock, logic)
saverD.run()
