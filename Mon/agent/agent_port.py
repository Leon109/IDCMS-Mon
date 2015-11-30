#!/usr/bin/env python
#coding=utf-8

import os
import sys
import json
import socket

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.syscmd import Command, get_iphostname
from utils.monconf import config 
from utils.utils import send_data

control_conf = config('mon.conf', 'control')
check_time = int(control_conf['check_time'])
check_count = int(control_conf['check_count'])
cmd_timeout = control_conf['cmd_timeout']

trans_list = ['localhost:9100']
sock_list = [None]

def agent_port(addr, port):
   sock=None
   while True:
       try:
           if sock == None:
               sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
               sock.settimeout(check_time * check_count)
               sock.connect((addr, port))
               sock.settimeout(None)
           count = sock.recv(10)
           if not count:
               raise  ValueError
           count = int(count)
           buf = sock.recv(count)
           if buf == "ping":
               sock.sendall("%010d%s"%(len("pong"), "pong"))
           else:
                host_cmd = json.loads(buf)
                send_buff = get_iphostname()
                cmd = host_cmd['cmd']
                timeout =  host_cmd.get("timeout", cmd_timeout)
                command = Command(cmd)
                recode, output, error = command.run(int(timeout))
                if not recode:
                    send_buff['result'] = output
                else:
                    send_buff['result'] = error
                send_buff['cmd_host'] = host_cmd['host']
                send_buff['cmd'] = cmd 
                send_buff = json.dumps(send_buff)
                send_data(trans_list, send_buff, sock_list)
       except (socket.error, ValueError), msg:
           sock.close()
           sock = None
if __name__ == "__main__":
    agent_port('127.0.0.1', 10000)
