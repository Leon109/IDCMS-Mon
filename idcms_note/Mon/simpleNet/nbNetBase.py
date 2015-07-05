#!/usr/bin/env python

"""一个简单的epoll实现的网络协议，这个模块定义了一些基础方法
通过接收客户端的前10个字节，获取传输文件大小，然后进行处理
如国客户端发送 0000000002hi 服务端收到的就是hi 然后进程处理
后发送给客户端
"""
import os
import sys
import errno
import socket
import select
import multiprocessing
from inspect import currentframe

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.config import config
from utils.log import Logger

logconf = config('nbnet', 'log')
logger = Logger.getLogger()
debug = logconf['debug']


class DebugLog():
    '''debug日志模块会显示运行的文件和行数'''
    def __init__(self, file_path):
        self.file_path = file_path
    
    def get_linenumber(self):
        '''获取函数运行在一行'''
        cf = currentframe()
        return "run_line: file %s line %s " % (self.file_path, cf.f_back.f_back.f_lineno)

    def dblog(self, msg):
        '''根据debug开关纪录日志'''
        msg = self.get_linenumber() + msg 
        logger.debug(msg)

if debug == "True":
    logs = DebugLog(__file__)


class STATE(object):
    """状态机状态"""
    def __init__(self):
        self.state = 'accept'
        self.need_read = 10
        self.need_write = 0
        self.have_read = 0
        self.have_write = 0
        self.buff_read = ""
        self.buff_write = ""
        self.seck_obj = ""

    def state_log(self):
        '''dbug显示每个f状态'''
        if debug == "True":
            msg = (
                '\n current_fd:{fd} \n state:{state}'
                '\n need_read:{need_read} \n need_write:{need_write}'
                '\n have_read:{have_read}\n have_write:{have_write}'
                '\n buff_read:{buff_read} \n buff_write:{buff_write}'
            ) .format(
                fd = self.sock_obj.fileno(), state = self.state,
                need_read = self.need_read, need_write = self.need_write,
                have_read = self.have_read, have_write = self.have_write,
                buff_read = self.buff_read, buff_write = self.buff_write,
            )
            logs.dblog(msg)

def bind_socket(addr, port):
    '''生成监听的socket'''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((addr, port))
    sock.listen(10)
    return sock


class nbNetBase(object):
    '''无阻塞网络框架
    一些基础方法，方便复用
    '''
    def __init__(self, sock, logic):
        '''初始化对象'''
        self.conn_state = {}
        logs.dblog("init: init listen socket ")
        self.setFd(sock)
        self.epoll_sock = select.epoll()
        self.epoll_sock.register(sock.fileno(), select.EPOLLIN)
        self.logic = logic

    def setFd(self, sock):
        '''创建状态机初始化状态
        STATE() 是初始状态,具体参考STATE类
        conn_state 是一个自定义的字典，用于存取每个fd的状态
        '''
        logs.dblog("setFD: crete init state")
        tmp_state = STATE()
        tmp_state.sock_obj = sock
        self.conn_state[sock.fileno()] = tmp_state
        self.conn_state[sock.fileno()].state_log()

    def state_machine(self, fd):
        '''跟据状态机切换状态执行不用方法
        sm 是一个python下的switch使用字典（需要自定义）
        如{'x':func0, "y":func1},使用不同的key执行不同的函数
        '''
        logs.dblog("state_machine: run state")
        sock_state = self.conn_state[fd]
        sock_state.state_log()
        self.sm[sock_state.state](fd)


    def accept(self, fd):
        '''accpet使用epoll等待检测客户端连接
        返回一个新的socket非阻塞对象
        '''
        logs.dblog("accept: accept client")
        try:
            sock_state = self.conn_state[fd]
            sock = sock_state.sock_obj
            conn, addr = sock.accept()
            conn.setblocking(0)
            logs.dblog("accept: find new socket client fd(%s)" % conn.fileno())
            return conn
        except socket.error as msg:
            if msg.errno in (11, 103):
                return "retry"
    
    def read(self, fd):
        '''读取数据(appcet执行完后，切换到read状态)
        这里逻辑是这样的 先读10个字节头 根据10个字节头算出要接受数据的大小
        然后在次进行读，一直到读完后返回状态 process
        '''
        logs.dblog("read: start read data")
        sock_state = self.conn_state[fd]
        conn = sock_state.sock_obj
        try:
            if sock_state.need_read <= 0:
                raise socket.error

            one_read = conn.recv(sock_state.need_read)
            if len(one_read) == 0:
                raise socket.error
            
            logs.dblog("read: read state")
            sock_state.buff_read += one_read
            sock_state.have_read += len(one_read)
            sock_state.need_read -= len(one_read)
            sock_state.state_log()

            if sock_state.have_read == 10:
                logs.dblog("read: protocol read end")
                if not sock_state.buff_read.isdigit():
                    raise socket.error
                elif int(sock_state.buff_read) <= 0:
                     raise socket.error
                sock_state.need_read += int(sock_state.buff_read)
                sock_state.buff_read = ''
                sock_state.state_log()
                return "readcontent"

            elif sock_state.need_read == 0:
                logs.dblog("read: read end")
                return "process"
            else:
                return "readmore"
        
        except socket.error, msg:
            if msg.errno == 11:
                return "retry"
            logs.dblog("***read: soket fd(%s) error(%s) "
                "change state to closing***" % (fd, msg))
            return "closing"

    def process(self, fd):
        '''程序处方法使用传入的logic方法进行处理'''
        logs.dblog("proces: proces start")
        sock_state = self.conn_state[fd]
        response = self.logic(sock_state.buff_read)
        sock_state.buff_write = "%010d%s" % (len(response), response)
        sock_state.need_write = len(sock_state.buff_write)
        sock_state.state = "write"
        self.epoll_sock.modify(fd, select.EPOLLOUT)
        logs.dblog("***process: process end fd state change to write***")
        sock_state.state_log()

    def write(self, fd):
        '''wirte用与在"process"处理完数据后向客户端返回数据'''
        logs.dblog("write: start write data")
        sock_state = self.conn_state[fd]
        conn = sock_state.sock_obj
        last_have_send = sock_state.have_write
        try:
            logs.dblog("write: write state")
            have_send = conn.send(sock_state.buff_write[last_have_send:])
            sock_state.have_write += have_send
            sock_state.need_write -= have_send
            sock_state.state_log()
            if sock_state.need_write == 0 and sock_state.have_write != 0:
                logs.dblog("wirte: write end")
                return "writecomplete"
            else:
                return "readmore"
        
        except socket.error, msg:
            if msg.errno == 11:
                return "retry"
            logs.dblog("***wirte: soket fd(%s) error(%s) change state to closing***" % (fd, msg))
            return "closing"

    def close(self, fd):
        '''关闭连接
        '''
        logs.dblog("close: close fd(%s)" % fd)
        self.epoll_sock.unregister(fd)
        sock = self.conn_state[fd].sock_obj
        sock.close()
        self.epoll_sock.unregister(fd)
        self.conn_state.pop(fd)

    def run(self):
        '''运行程序
          监听epoll是否有新链接过来
        '''
        while True:
            epoll_list = self.epoll_sock.poll()
            for fd, events in epoll_list:
                logs.dblog("epoll: epoll find fd(%s) have signal" % fd)
                sock_state = self.conn_state[fd]
                if select.EPOLLHUP & events:
                    sock_state.state = "closing"
                elif select.EPOLLERR & events:
                    sock_state.state = "closing"
                logs.dblog("epoll: use state_machine process fd(%s)" % fd)
                self.state_machine(fd)

def fork_processes(num_processes, max_restarts=100):
    '''多进程启动
    两个参数
    1 开启进程数，如果小于等于0 则按cpu核心数开启
    2 子进程最大重启次数
    '''
    if num_processes is None or num_processes <= 0:
        num_processes = multiprocessing.cpu_count()
    children = {}
    
    def start_child(i):
        pid = os.fork()
        if pid == 0:
            return i
        else:
            children[pid] = i 
            return None
    
    for i in range(num_processes):
        id = start_child(i)
        if id is not None:
            return id
    num_restarts = 0 
    
    while children:
        try:
            pid, status = os.wait()
        except OSError as e:
            if e.errno == errno.EINTR:
                continue
            raise
        if pid not in children:
            continue
        id = children.pop(pid)
        if os.WIFSIGNALED(status):
            pass
        elif os.WEXITSTATUS(status) != 0:
            pass
        else:
            continue
        num_restarts += 1
        if num_restarts > max_restarts:
            raise RuntimeError("Too many child restarts, giving up")
        new_id = start_child(id)
        if new_id is not None:
            return new_id
    sys.exit(0)


