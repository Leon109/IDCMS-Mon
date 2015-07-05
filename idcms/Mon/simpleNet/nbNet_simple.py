#!/usr/bin/env python

"""一个简单的epoll实现的网络协议（作为参考使用）
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

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.log import Logger

logger = Logger.getLogger()
debug = True

class _STATE(object):
    """
    链接状态
    """
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
        if debug:
            msg = (
                '\n current_fd:{fd} \n state:{state}'
                '\n need_read:{need_read} \n need_write:{need_write}'
                '\n have_read:{have_read}\n have_write:{have_write}'
                '\n buff_read:{buff_read} \n buff_write:{buff_write}'
            ) .format(
                fd = self.sock_obj.fileno(), state = self.state,
                need_read = self.need_read, need_write = self.need_write,
                have_read = self.need_read, have_write = self.need_write,
                buff_read = self.need_read, buff_write = self.need_write,
            )
            logger.debug(msg)

def bind_socket(addr, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(0)
    sock.bind((addr, port))
    sock.listen(10)
    return sock

class nbNet(object):
    """
    一个简单非阻塞网络框架
    """
    def __init__(self, sock, logic):
        self.conn_state = {}

        self.setFd(sock)
        self.epoll_sock = select.epoll()
        self.epoll_sock.register(sock.fileno(), select.EPOLLIN)

        self.logic = logic
        self.sm = {
            "accept": self.accept,
            "read": self.read,
            "write": self.write,
            "process": self.process,
            "closing": self.close,
        }

    def setFd(self, sock):
        '''为sock创建一个状态机
        '''
        tmp_state = _STATE()
        tmp_state.sock_obj = sock
        self.conn_state[sock.fileno()] = tmp_state

    def state_machine(self, fd):
        sock_state = self.conn_state[fd]
        self.sm[sock_state.state](fd)

    def accept(self, fd):
        '''接受新传入的fd，为新fd注册
        '''
        try:
            sock_state = self.conn_state[fd]
            sock = sock_state.sock_obj
            conn, addr = sock.accept()
            conn.setblocking(0)
            self.epoll_sock.register(conn.fileno(), select.EPOLLIN)
            self.setFd(conn)
            self.conn_state[conn.fileno()].state = "read"
        except socket.error as msg:
            if msg.args[0] in (errno.ECONNABORTED, errno.EAGAIN):
                return
            raise

    def read(self, fd):
        '''读取fd(appcet执行完后，切换到read状态)
        这里逻辑是这样的 先读10个字节头 根据10个字节头算出要接受数据的大小
        然后在次进行读，读完后交给process处理，读的时候不要使用self.state_machine(fd)强制
        虚幻调用了，容易触发python的最大递归次数，让epoll自己判断，就行读写
        '''
        sock_state = self.conn_state[fd]
        conn = sock_state.sock_obj
        try:
            if sock_state.need_read <= 0:
                raise socket.error

            one_read = conn.recv(sock_state.need_read)
            if len(one_read) == 0:
                raise socket.error

            sock_state.buff_read += one_read
            sock_state.have_read += len(one_read)
            sock_state.need_read -= len(one_read)

            if sock_state.have_read == 10:
                if not sock_state.buff_read.isdigit():
                    raise socket.error
                elif int(sock_state.buff_read) <= 0:
                     raise socket.error
                sock_state.need_read += int(sock_state.buff_read)
                sock_state.buff_read = ''

            elif sock_state.need_read == 0:
                sock_state.state = "process"
                self.state_machine(fd)

        except socket.error, msg:
            if msg.errno == 11:
                    return
            sock_state.state = "closing"
            self.state_machine(fd)

    def process(self, fd):
        '''read完成后进行 process 进行处理
        '''
        sock_state = self.conn_state[fd]
        response = self.logic(sock_state.buff_read)
        sock_state.buff_write = "%010d%s" % (len(response), response)
        sock_state.need_write = len(sock_state.buff_write)
        sock_state.state = "write"
        self.epoll_sock.modify(fd, select.EPOLLOUT)
        self.state_machine(fd)

    def write(self, fd):
        '''像客户端发送请求
        '''
        sock_state = self.conn_state[fd]
        conn = sock_state.sock_obj
        last_have_send = sock_state.have_write
        try:
            have_send = conn.send(sock_state.buff_write[last_have_send:])
            sock_state.have_write += have_send
            sock_state.need_write -= have_send
            if sock_state.need_write == 0 and sock_state.have_write != 0:
                self.setFd(conn)
                self.conn_state[fd].state = "read"
                self.epoll_sock.modify(fd, select.EPOLLIN)
        except socket.error, msg:
            if msg.errno == 11:
                return
            sock_state.state = "closing"
            self.state_machine(fd)

    def close(self, fd):
        '''关闭连接
        '''
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
                sock_state = self.conn_state[fd]
                if select.EPOLLHUP & events:
                    sock_state.state = "closing"
                elif select.EPOLLERR & events:
                    sock_state.state = "closing"
                self.state_machine(fd)


def fork_processes(num_processes, max_restarts=100):
    '''
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

if __name__ == "__main__":
    def logic(in_data):
        return in_data[::-1]
    '''多进程启动'''
    sock = bind_socket("0.0.0.0", 9000)
    fork_processes(0)
    reverseD = nbNet(sock, logic)
    reverseD.run()
    '''但进程启动
    sock = bind_socket("0.0.0.0", 9000)
    reverseD = nbNet(sock, logic)
    reverseD.run()
    '''
