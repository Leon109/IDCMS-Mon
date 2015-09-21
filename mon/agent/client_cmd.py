#!/usr/bin/env python
#coding=utf-8
import socket, sys, os
import time
import json

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.crypt import encrypt,decrypt
# 三个参数，一个是处理内容，一个是发送次数，三十超时时间

HOST = '127.0.0.1'
PORT = 9200
CNT = int(sys.argv[2])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

data = {}
data['cmd'] = sys.argv[1]
data['timeout'] = sys.argv[3]

data = json.dumps(data)
enc_data = encrypt(data)
send_data = "%010d%s"%(len(enc_data), enc_data)

for i in xrange(CNT):
    s.send(send_data)

for i in xrange(CNT):
    but_int = s.recv(10)
    data_size=int(but_int)
    buf = decrypt(s.recv(data_size))
    ret = json.loads(buf)
    print ret['result']
