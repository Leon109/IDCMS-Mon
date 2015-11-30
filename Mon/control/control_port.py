#!/usr/bin/env python
#coding=utf-8

import os
import sys
import json

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from nbnet.nbnet_base import *
from utils.utils import run_linenumber
from utils.monconf import config 

control_conf = config('mon.conf', 'control')

addr = control_conf['addr']
port = int(control_conf['port'])
check_time = int(control_conf['check_time'])
check_count = int(control_conf['check_count'])

class AddrState(object):
    '''地址状态状态类'''
    def __init__(self):
        self.fd = None
        self.send_time = None
        self.fd_timeout = None
        self.buff_read = ''
        self.buff_send = ''
        self.count = 0

class nbNetPORT(nbNetBase):
    '''nbNet处理架构'''
    def __init__(self, sock, custom_logic=None):
        # 继承父类init
        super(nbNetPORT, self).__init__(sock, custom_logic)
        # 地址和fd对应表
        self.addr_fd = {}
        # 状态机切换规则
        self.sm = {
            "accept": self.accept2send,
            "read": self.read2process,
            "send": self.send2read,
            "closing": self.close,
        }

    def accept2send(self, fd):
        '''获取socket，并使socket转换为read状态
        注意 这里的fd 是监听的fd（第一个创建的fd）'''
        accept_ret = self.accept(fd)
        if not accept_ret == "retry":
            conn = accept_ret[0]
            addr = accept_ret[1]
            # 初始化这个socket,并定位到这个fd
            self.set_fd(conn, addr)
            sock_state = self.conn_state[conn.fileno()]
            # 将ip和地址和addr绑定在一起，如果ip支持重复，则关掉这个fd
            if addr not in self.addr_fd:
                tmp_addr_state = AddrState()
                tmp_addr_state.fd = conn.fileno()
                self.addr_fd[addr] = tmp_addr_state
                # 更改这个fd为send模式
                sock_state.state = "send"
                # 服务端发送ping客户端回复pong保持链接
                sock_state.buff_send = "%010d%s" % (len("ping"), "ping")
                sock_state.need_send = len(sock_state.buff_send)
                self.epoll_sock.register(conn.fileno(), select.EPOLLOUT)
                # 将ip和地址和addr绑定在一起，如果ip支持重复，则关掉这个fd
                sock_state.state_log(run_linenumber() + "accept2send: fd %s to send state" % conn.fileno())
            else:
                sock_state.state_log(run_linenumber() + "accept2send: fd %s ip addr repeat close" % conn.fileno())
                sock_state.state = "closing"
                self.state_machine(conn.fileno())
        else:
            pass

    def read2process(self, fd):
        '''处理read状态，并传入proces进行执行'''
        read_ret = self.read(fd)
        if read_ret == "read_finish":
            self.process2send(fd)
        elif read_ret in ("read_content", "read_continue", "retry"):
            pass
        elif read_ret == "closing":
            self.conn_state[fd].state = 'closing'
            self.state_machine(fd)
        else:
            raise Exception("impossible state returned by self.read")

    def process2send(self, fd):
        '''处理process状态，并直接使用send进行执行'''
        sock_state = self.conn_state[fd]
        process_ret = self.process(fd)
        # 如果通过了验证重置fd检查计数器和初始化这个fd 
        if process_ret == "process_verify":
            conn = sock_state.sock_obj
            addr = sock_state.sock_addr
            addr_state = self.addr_fd[addr]
            addr_state.count = 0
            if sock_state.need_read == 0:
                self.set_fd(conn, addr)
            else:
                self.set_send_fd(fd)
            self.conn_state[fd].state = "read"
            self.conn_state[fd].state_log(run_linenumber() + "accept2send: process_verify  fd %s to read state" % fd)

        elif process_ret == "process_finish":
            sock_state.state = "send"
            self.epoll_sock.modify(fd, select.EPOLLOUT)
            sock_state.state_log(run_linenumber() + "accept2process: process_finish fd %s to send state" % fd)
        else:
            raise Exception("impossible state returned by self.process")

    def send2read(self, fd):
        '''使用send发送process处理的数据
        处理完后返回read状态继续监听客户端发送'''
        send_ret = self.send(fd)
        if send_ret in ("send_continue", "retry"):
            pass
        elif send_ret == "send_finish":
            sock_state = self.conn_state[fd]
            # 防止这个fd改为send状态的时候，还没有读完
            if sock_state.need_read == 0:
                conn = sock_state.sock_obj
                addr = sock_state.sock_addr
                self.set_fd(conn, addr)
            else:
                self.set_send_fd(fd)
            self.conn_state[fd].state = "read"
            self.epoll_sock.modify(fd, select.EPOLLIN)
            self.conn_state[fd].state_log(run_linenumber() + "send2read: fd %s to read state" % fd)
        elif send_ret == "closing":
            self.conn_state[fd].state = 'closing'
            self.state_machine(fd)
        else:
            raise Exception("impossible state returned by self.send")

    def close(self, fd):
        '''重写关闭'''
        sock_state = self.conn_state[fd]
        sock_state.state_log(run_linenumber() + "close: close fd %s " % fd) 
        # 如果这个fd和某个ip绑定了则同时取消注册并删除这个ip链接
        addr_state  = self.addr_fd.get(sock_state.sock_addr, False)
        if addr_state and fd == addr_state.fd:
            self.epoll_sock.unregister(fd)
            self.addr_fd.pop(sock_state.sock_addr)
        sock = self.conn_state[fd].sock_obj
        sock.close()
        self.conn_state.pop(fd)

    def logic(self, data, sock_state):
        '''处理方式'''
        if data == "pong":
            return "active"
        elif data == "query":
            return json.dumps(self.addr_fd.keys())
        else:
            cmd_data = {}
            try:
                data = json.loads(data)
            except ValueError:
                return "error_data"
            if isinstance(data, dict) and "host" in data and "cmd" in data:
                if data['host']  not in self.addr_fd:
                    return "not_find_host"
                cmd_data['host'] = sock_state.sock_addr
                cmd_data['cmd'] = data['cmd']
                if data.get('timeout', None):
                    cmd_data['timeout'] = data['timeout']
                response = json.dumps(cmd_data)
                addr_state = self.addr_fd[data['host']]
                cmd_sock_state = self.conn_state[addr_state.fd]
                new_buff_send = "%010d%s" % (len(response), response)
                cmd_sock_state.buff_send += new_buff_send
                cmd_sock_state.need_send += len(new_buff_send)
            else:
                return "error_data"
            if cmd_sock_state.state == "read":
                cmd_sock_state.state = "send"
                conn = cmd_sock_state.sock_obj
                self.epoll_sock.modify(conn.fileno(), select.EPOLLOUT)
            return "cmd_send_end"

    def set_send_fd(self, fd):
        '''如果还没读完，但是改成发送状态了，需要初始化发送'''
        sock_state = self.conn_state[fd]
        sock_state.need_send = 0 
        sock_state.have_send = 0
        sock_state.buff_send = ''
        self.conn_state[sock.fileno()].state_log(run_linenumber() + "set_send_fd: init socket send fd %s" % fd)
        
    def check_fd(self):
        '''检查fd心跳链接
        如果地址缓存的状态，没有发生变化择发送心跳包，如果第二次还没有发生变化择
        关闭这个链接
        需要单独起一个线程进行监控
        '''
        while True:
            for addr in self.addr_fd.keys():
                addr_state = self.addr_fd[addr]
                sock_state = self.conn_state[addr_state.fd]
                
                # 判断读和写是否发生了变化
                if addr_state.buff_read != sock_state.buff_read:
                    addr_state.buff_read = sock_state.buff_read
                elif addr_state.buff_send != sock_state.buff_send:
                    addr_state.buff_send = sock_state.buff_send
                # 如果没发生变化择发送ping请求
                else:
                    if addr_state.count > check_count:
                        sock_state.state = "closing"
                        sock_state.state_log(run_linenumber() + "check_fd: fd %s no active closing" % addr_state.fd)
                        self.state_machine(addr_state.fd)
                        continue
                    heartbeat = "%010d%s" % (len('ping'), 'ping')
                    sock_state.buff_send += heartbeat
                    sock_state.need_send += len(heartbeat)
                    addr_state.count += 1
                    if sock_state.state == "read":
                        sock_state.state = "send"
                        self.epoll_sock.modify(addr_state.fd, select.EPOLLOUT)
            # 超时检查时间
            time.sleep(check_time)


if __name__ == "__main__":
    '''单进程启动'''
    sock = bind_socket(addr, port)
    control = nbNetPORT(sock)
    
    import threading
    class ControlThread (threading.Thread):
        '''使用多线程，一个线程运行control，另一个监控fd状态是否超时'''
        def __init__(self, name):
            threading.Thread.__init__(self)
            self.name = name
        
        def run(self):
            if self.name == 'control_run':
                self.control_run()
            elif self.name == 'check_run':
                self.check_run()

        def control_run(self):
            control.run()
    
        def check_run(self):
            control.check_fd()

    def control_start():
        ctl = ControlThread('control_run')
        ctl.start()
        check = ControlThread('check_run')
        check.start()
        ctl.join()
        check.join()
    control_start()
