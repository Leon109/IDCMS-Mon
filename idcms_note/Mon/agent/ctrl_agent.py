#!/usr/bin/env python
#coding=utf-8

import socket
import threading
from agent_utils import Command

def ctl_agent(addr, port, sock_l):
    recv_timeout = 60
    
    def send_data(sock, data):
        sock.sendall("%010d%s"%(len(data), data))

    while True:
        try:
            if socl_l[0] == None:
                sock_l[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock_l[0].settimeout(5)
                sock_l[0].connect((host, port))
                sock_l[0].settimeout(None)
            
            check_recv = threading.Timer(recv_timeout, send_data(sock_l[0], "ping"))   
            sock_l[0].settimeout(recv_timeout + 10)
            count = sock_l[0].recv(10)
            if not count:
                raise  ValueError
            count = int(count)
            recv_data = sock_l[0].recv(count)
            sock_l[0].settimeout(None)
            check_recv.cancel()

            if recv_data == "pong":
                pass
            else:
                cmd = recv_data["cmd"]
                recv_teimout = int(recv_data['timeout'])
                command = Command(cmd)
                recode, data, error = command.run(timeout)
                send_data(data)
        except (socket.error, ValueError), msg:
            sock_l[0].close()
            sock_l[0] == None
