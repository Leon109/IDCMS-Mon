#!/usr/bin/env python
#coding=utf-8

import socket
import threading
from agent_utils import Command
import time

def ctl_agent(addr, port, sock_l):
    '''客户端接受服务端发过来的链接
    通过 threading.Timer做计时器定时探测服务端是否活跃
    通过 socket settimeout，做超时判断，注意改回settimeout(None)
    改为 settimeout后 socket会变成非阻塞模式
    socket 异常关闭后通过 time.sleep 定时重新连接服务端
    '''
    recv_timeout = 5
    
    def send_data(sock, data):
        try:
            sock.sendall("%010d%s"%(len(data), data))
        except socket.error, msg:
            pass

    while True:
        try:
            if sock_l[0] == None:
                sock_l[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock_l[0].settimeout(5)
                sock_l[0].connect((addr, port))
                sock_l[0].settimeout(None)
            check_recv = threading.Timer(recv_timeout, send_data,args=[sock_l[0], "ping"])
            check_recv.start()
            sock_l[0].settimeout(recv_timeout + 10)
            count = sock_l[0].recv(10)
            if not count:
                raise  ValueError
            count = int(count)
            recv_data = sock_l[0].recv(count)
            sock_l[0].settimeout(None)
            check_recv.cancel()

            if recv_data == "pong":
                print recv_data
                pass
            else:
                cmd = recv_data["cmd"]
                recv_teimout = int(recv_data['timeout'])
                command = Command(cmd)
                recode, data, error = command.run(timeout)
                send_data(data)
        except (socket.error, ValueError), msg:
            sock_l[0].close()
            sock_l[0] = None
            time.sleep(2)

if  __name__ == "__main__":
    sock_l = [None]
    addr = '127.0.0.1'
    port = 9000
    ctl_agent( addr, port, sock_l)
