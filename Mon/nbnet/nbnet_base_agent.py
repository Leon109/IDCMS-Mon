#!/usr/bin/env python
#coding=utf-8

import os
import sys
import time
import json
import errno
import socket
import select
import multiprocessing

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.monconf import config 
from utils.utils import run_linenumber

all_conf = config('mon.conf')
debug = all_conf.getboolean('nbnet', 'debug')
if debug:
    from utils.monlog import Logger
    logs = Logger.getLogger(debug=True)
    
class STATE(object):
    """状态机状态"""
    def __init__(self):
        self.state = 'send'
        self.need_read = 10
        self.need_send = 0
        self.have_read = 0
        self.have_send = 0
        self.buff_read = ''
        self.buff_send = ''
        self.sock_obj = None
        self.sock_addr = None
        self.read_start_time= None
        self.read_wait_time= all_conf.getint('nbnet', 'wait_time')

    def state_log(self, info):
        '''debug显示每个socket fd 状态'''
        if debug:
            msg = (
                '\n state: %s \n need_read: %s \n need_send: %s \n have_read: %s' 
                '\n have_send: %s \n buff_read: %s \n buff_send: %s \n sock_obj: %s' 
                '\n sock_addr: %s \n sock_read_start_time: %s \n sock_read_wait_time: %s'
            ) % (
                self.state, self.need_read, self.need_send, self.have_read, 
                self.have_send, self.buff_read, self.buff_send, self.sock_obj,
                self.sock_addr, self.read_start_time, self.read_wait_time
            )
            logs.debug('[nbnet_agent] ' + info + msg)

class nbNetBaseAgent(object):
    def __init__(self, addr, port, logic):
        self.conn_state = {}
        self.addr = addr
        self.port = port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.bind((addr, port))
        sock.setblocking(0)
        self.set_fd(sock)
        self.epoll_sock = select.epoll()
        self.epoll_sock.register(sock.fileno(), select.EPOLLIN)
        self.logic = logic

    def set_fd(self, sock, addr=None):
        tmp_state = STATE()
        tmp_state.sock_obj = sock
        tmp_state.sock_addr = addr
        self.conn_state[sock.fileno()] = tmp_state
        self.conn_state[sock.fileno()].state_log(run_linenumber() + "set_fd: init socket fd %s" % sock.fileno())
    
    def state_machine(self, fd):
        sock_state = self.conn_state[fd]
        sock_state.state_log(run_linenumber() + "state_machine: runing fd %s state %s" % (fd, sock_state.state))
        self.sm[sock_state.state](fd)

    def monitor(self, fd):
        '''在什么也不需要操作的，进入监听模式
        防止在发送验证ping 和 pong 保持链接的的时候正在进行读和发送数据
        '''
        sock_state.state_log(run_linenumber() + "monitor: monitor start")
        sock_state = self.conn_state[fd]
        self.conn_state[fd].state = "read"
        self.state_machine(fd)

    def read(self, fd):
        sock_state = self.conn_state[fd]
        conn = sock_state.sock_obj
        sock_state.state_log(run_linenumber() + "read: start read")
        try:
            if sock_state.need_read <= 0:
                raise socket.error
            one_read = conn.recv(sock_state.need_read)
            if len(one_read) == 0:
                raise socket.error
            
            sock_state.buff_read += one_read
            sock_state.have_read += len(one_read)
            sock_state.need_read -= len(one_read)
            sock_state.state_log(run_linenumber() + 'read: read runing ......')

            if sock_state.have_read == 10:
                if not sock_state.buff_read.isdigit():
                    raise socket.error
                elif int(sock_state.buff_read) <= 0:
                     raise socket.error
                sock_state.need_read += int(sock_state.buff_read)
                sock_state.buff_read = ''
                sock_state.state_log(run_linenumber() + "read: head read finsh")
            elif sock_state.need_read == 0:
                sock_state.state_log(run_linenumber() + "read: read finish")
                self.process(fd)
            else:
                pass 
        except socket.error, msg:
            if msg.errno == 11:
                pass
            else:
                sock_state.state_log(run_linenumber() + "read: soket fd %s error %s" % (fd, msg))
                sock_state.state = 'closing'
                self.state_machine(fd)

    def process(self, fd):
        sock_state = self.conn_state[fd]
        sock_state.state_log(run_linenumber() + "process: process start")
        response = self.logic(sock_state.buff_read)
        sock_state.buff_send = "%010d%s" % (len(response), response)
        sock_state.need_send = len(sock_state.buff_send)
        sock_state.state_log(run_linenumber() + "process: process finish")
        sock_state.state = "send"
        self.epoll_sock.modify(fd, select.EPOLLOUT)
        sock_state.state_log(run_linenumber() + "accept2process: fd %s to send state" % fd) 

    def send(self, fd):
        sock_state = self.conn_state[fd]
        conn = sock_state.sock_obj
        # 如果发送的时候发现buff是空的发送ping（被动模式下使用）
        if not sock_state.buff_send:
            sock_state.buff_send = "%010d%s" % (len('ping'), "ping")
            sock_state.need_send = len(sock_state.buff_send)
            self.epoll_sock.modify(fd, select.EPOLLOUT)
        last_have_send = sock_state.have_send
        sock_state.state_log(run_linenumber() + "send: send start")
        try:
            have_send = conn.send(sock_state.buff_send[last_have_send:])
            sock_state.have_send += have_send
            sock_state.need_send -= have_send
            sock_state.state_log(run_linenumber() + "wirte: send runing ......")
            if sock_state.need_send == 0 and sock_state.have_send != 0:
                sock_state.state_log(run_linenumber() + "send: send end")
                conn = sock_state.sock_obj
                addr = sock_state.sock_addr
                self.set_fd(conn, addr)
                self.conn_state[fd].state = "monitor"
                self.epoll_sock.modify(fd, select.EPOLLIN)
            else:
                pass
        
        except socket.error, msg:
            if msg.errno == 11:
                pass
            else:
                sock_state.state_log(run_linenumber() + "send: soket fd %s error %s" % (fd, msg))
                sock_state.state = 'closing'
                self.state_machine(fd)

    def close(self, fd):
        sock_state = self.conn_state[fd]
        sock_state.state_log(run_linenumber() + "close: close fd %s " % fd)
        self.epoll_sock.unregister(fd)
        sock = self.conn_state[fd].sock_obj
        sock.close()
        self.conn_state.pop(fd)    

    def run(self):
        while True:
            epoll_list = self.epoll_sock.poll()
            for fd, events in epoll_list:
                sock_state = self.conn_state[fd]
                sock_state.state_log(run_linenumber() + "run: epoll find fd %s new events: %s" % (fd, events))
                sock_state = self.conn_state[fd]
                if select.EPOLLHUP & events:
                    sock_state.state = "closing"
                elif select.EPOLLERR & events:
                    sock_state.state = "closing"
                sock_state.state_log(run_linenumber() + "run: use state_machine runing fd %s" % fd)
                self.state_machine(fd)
    
    def check_fd(self):
        while True:
            for fd in self.conn_state.keys():
                sock_state = self.conn_state[fd]
                if sock_state.state == "read" and sock_state.read_stime \
                    and (time.time() - sock_state.read_stime) >= sock_state.read_itime:
                    sock_state.state = "closing"
                    self.state_machine(fd)
            time.sleep(60)
