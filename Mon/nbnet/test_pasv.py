#!/usr/bin/env python
#coding=utf-8

import socket, sys, os
import time

# 两个参数，一个是处理内容 一个是发送次数

HOST = '127.0.0.1'
PORT = 10000
#CNT = int(sys.argv[2])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

for x in range(10):
    count = sock.recv(10)
    print 123
    print count
    print 456
    # 统计需要接收数据大小
    count = int(count)
    # 接受数据
    buf = sock.recv(count)
    print buf
    if buf == "ping":
        sock.sendall("%010d%s"%(len("pong"), "pong"))

#cmd = sys.argv[1]
#data = "%010d%s"%(len(cmd), cmd)
#s.send(data * CNT)

#for i in xrange(CNT):
#    buf = s.recv(len(data))
#    print buf
