#!/usr/bin/env python
#coding=utf-8
import os
import sys
import socket
import json

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.crypt import encrypt,decrypt
# 三个参数，一个是处理内容，一个是发送次数，三十超时时间

HOST = '211.100.52.158'
PORT = 10000
CNT = int(sys.argv[2])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

data = {}
data['host'] = sys.argv[1]
data['cmd'] = sys.argv[2]
data['timeout'] = sys.argv[3]

count = sock.recv(10)
# 统计需要接收数据大小
count = int(count)
buf = sock.recv(count)
if buf == "ping":
    sends = json.dumps(data)
    sock.sendall("%010d%s"%(len(sends), sends))

    count = sock.recv(10)
    count = int(count)
    buf = sock.recv(count)
    print buf
    sock.close()
