#!/usr/bin/env python
#coding=utf-8

'''nbnet在客户端链接后，主动发送数据给客户端，客户端等待链接'''

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
        self.state = 'accept'
        self.need_read = 10
        self.need_send = 0
        self.have_read = 0
        self.have_send = 0
        self.buff_read = ''
        self.buff_send = ''
        # PORT模式主动发送过来的数据
        self.port_send = ''
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
            logs.debug('[nbnet] ' + info + msg)


def bind_socket(addr, port):
    '''生成监听的socket'''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((addr, port))
    sock.listen(10)
    return sock

class nbNetBase_PORT(object):
    '''无阻塞网络框架
    基础方法
    '''
    def __init__(self, sock, logic):
        '''初始化对象'''
        self.conn_state = {}
        # 生成一个fd和ip对应的字典
        self.fd_addr = {}
        self.set_fd(sock)
        self.epoll_sock = select.epoll()
        self.epoll_sock.register(sock.fileno(), select.EPOLLIN)
        self.logic = logic

    def set_fd(self, sock, addr=None):
        '''状态机初始化'''
        tmp_state = STATE()
        tmp_state.sock_obj = sock
        tmp_state.sock_addr = addr
        # 只接受每个ip 一个客户端端链接
        if addr:
            if add not in self.fd_addr.keys():
                sock.close
                return False
        self.fd_addr[sock.fileno()] = addr
        # conn_states是这字典使用soket连接符(这个fileno获取socket连接符，是个整数)做key链接状态机
        self.conn_state[sock.fileno()] = tmp_state
        self.conn_state[sock.fileno()].state_log(run_linenumber() + "set_fd: init socket fd %s" % sock.fileno())
        return True
    
    def state_machine(self, fd):
        '''跟据状态切换状态执行方法'''
        sock_state = self.conn_state[fd]
        sock_state.state_log(run_linenumber() + "state_machine: runing fd %s state %s" % (fd, sock_state.state))
        self.sm[sock_state.state](fd)

    def accept(self, fd):
        '''accept使用epoll等待客户端连接
        收到连接后返回一个新的客户端 非阻塞socket, 和IP地址
        '''
        try:
            sock_state = self.conn_state[fd]
            sock = sock_state.sock_obj
            conn, addr = sock.accept()
            conn.setblocking(0)
            sock_state.state_log(run_linenumber() + "accept: fd %s find new socket client fd %s IP %s" % \
                                (fd, conn.fileno(), addr[0]))
            return conn, addr[0]
        except socket.error as msg:
            if msg.errno in (11, 103):
                return "retry"
    
    def read(self, fd):
        '''读取数据，读取要先将这个fd epoll注册，并变成为读状态
        epoll发现有读取信号会自动执行这个方法

        这里逻辑是这样的(协议设计) 先读10个字节头 根据10个字节头算出要接受数据的大小
        然后在次进行读取，直到读取完成
        
        '''
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
                return "read_content"
            elif sock_state.need_read == 0:
                sock_state.state_log(run_linenumber() + "read: read finish")
                return "read_finish"
            else:
                return "read_continue"
        
        except socket.error, msg:
            if msg.errno == 11:
                return "retry"
            sock_state.state_log(run_linenumber() + "read: soket fd %s error %s" % (fd, msg))
            return "closing"

    def process(self, fd):
        '''程序处方法使用传入的logic方法进行处理'''
        sock_state = self.conn_state[fd]
        sock_state.state_log(run_linenumber() + "process: process start")
        response = self.logic(sock_state.buff_read)
        sock_state.buff_send = "%010d%s" % (len(response), response)
        sock_state.need_send = len(sock_state.buff_send)
        sock_state.state_log(run_linenumber() + "process: process finish")
        return "process_finish"

    def send(self, fd):
        '''send处理，注意在send处理前，要先将处理的fd改成写模式'''
        sock_state = self.conn_state[fd]
        conn = sock_state.sock_obj
        last_have_send = sock_state.have_send
        sock_state.state_log(run_linenumber() + "send: send start")
        try:
            have_send = conn.send(sock_state.buff_send[last_have_send:])
            sock_state.have_send += have_send
            sock_state.need_send -= have_send
            sock_state.state_log(run_linenumber() + "wirte: send runing ......")
            if sock_state.need_send == 0 and sock_state.have_send != 0:
                sock_state.state_log(run_linenumber() + "send: send end")
                return "send_finish"
            else:
                return "send_continue"
        
        except socket.error, msg:
            if msg.errno == 11:
                return "retry"
            sock_state.state_log(run_linenumber() + "send: soket fd %s error %s" % (fd, msg))
            return "closing"

    def close(self, fd):
        '''关闭连接'''
        sock_state = self.conn_state[fd]
        sock_state.state_log(run_linenumber() + "close: close fd %s " % fd)
        self.epoll_sock.unregister(fd)
        sock = self.conn_state[fd].sock_obj
        sock.close()
        self.conn_state.pop(fd)    

    def run(self):
        '''运行程序
        监听epoll是否有新连接过来
        '''
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
        '''检查fd超时
        如果read 指定时间呢没有读取到数据择关闭连接
        需要单独起一个线程进行监控
        '''
        while True:
            for fd in self.conn_state.keys():
                sock_state = self.conn_state[fd]
                # fd是read状态并且 read_time 是真的
                # 判断该fd的epoll收到数据的等待时间是否超过间隔时间
                if sock_state.state == "read" and sock_state.read_stime \
                    and (time.time() - sock_state.read_stime) >= sock_state.read_itime:
                    # 超过定时器时间关闭该fd
                    sock_state.state = "closing"
                    self.state_machine(fd)
            # 超时检查时间
            time.sleep(60)

def fork_processes(num_processes, max_restarts=100):
    '''多进程启动
    两个参数
    1 开启进程数，如果小于等于0 则按cpu核心数开启
    2 子进程最大重启次数
    '''
    # 计算CPU核心数
    if num_processes is None or num_processes <= 0:
        num_processes = multiprocessing.cpu_count()
    # 字典以pid为key 进程数位值
    children = {}
    
    # 创建子进程
    def start_child(i):
        # i 是运行的进程数
        pid = os.fork()
        if pid == 0:
            return i
        else:
            #父进程将子进程pid存入字典
            children[pid] = i 
            return None
    
    # 根据进程数量启动进程并返回进程pid
    for i in range(num_processes):
        id = start_child(i)
        # 父进程运行到这里因为返回的是个空的所以会继续运行下面的代码
        # 子进程运行到这里因为程序已经运行完所以会结束运行
        if id is not None:
            return id
    # 父进程会继续运行下面
    # 子进程重启计数开始
    num_restarts = 0 
    
    while children:
        try:
            # 等待子进程结束os.wait()回收，进程回阻塞在这里
            pid, status = os.wait()
        except OSError as e:
            #如果系统EINTR错误(信号中断)跳出继续进行循环
            if e.errno == errno.EINTR:
                continue
            #其他OS错误则抛出
            raise
        #如果子进程pid不再启动的进程里面跳出继续进循环
        if pid not in children:
            continue
        # 进程结束后从字典中删除,并返回是第几个进程
        id = children.pop(pid)
        # 可以根据不同状态计入日志
        # 如果进程由于信号而退出，则返回True，否则返回False
        if os.WIFSIGNALED(status):
            pass
        # 如果WIFEXITED(status)返回True(子进程正常退出返回一个非零值)
        # 当WIFEXITED返回非零值时，我们可以用这个方法来提取子进程的返回值，如果子进程调用exit(5)退出，WEXITSTATUS(status)就会返回5
        elif os.WEXITSTATUS(status) != 0:
            pass
        # 其他错误跳出这次循环继续程序
        else:
            continue
        # 子进程最多的重启次数，如果子进程重启次数超过最大的设置则抛出异常
        num_restarts += 1
        if num_restarts > max_restarts:
            raise RuntimeError("Too many child restarts, giving up")
        # 正常情况下这个id已经退出了,我们在fork出一个新的进程
        new_id = start_child(id)
        # 如果fork 成功了直接return退出这个子进程
        if new_id is not None:
            return new_id
    # 如果没有正常启动进程，子进程字典为空则退出进程
    sys.exit(0)
