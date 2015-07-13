#!/usr/bin/env python
#coding=utf-8
import socket, sys, os
import time
# 两个参数，一个是处理内容，一个是发送次数

HOST = '127.0.0.1'
PORT = 9000
CNT = int(sys.argv[2])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

cmd = sys.argv[1]
data = "%010d%s"%(len(cmd), cmd)
#s.send(data * CNT)
for i in xrange(CNT):
    s.send(data)
    time.sleep(50)

for i in xrange(CNT):
    buf = s.recv(len(data))
    print buf
