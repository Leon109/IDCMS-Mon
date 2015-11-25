#!/usr/bin/env python
#coding=utf-8

import json

from nbnet_base import *

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.utils import run_linenumber

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
        # 通过父类获取socket链接
        accept_ret = self.accept(fd)
        # 如果获取到了socket对象，进行epoll注册，状态为只读，创建状态机
        # 并改变状态机状态为read
        if not accept_ret == "retry":
            conn = accept_ret[0]
            addr = accept_ret[1]
            # 初始化这个socket，设置为epool读模式,并定位到这个fd
            self.set_fd(conn, addr)
            self.epoll_sock.register(conn.fileno(), select.EPOLLIN)
            sock_state = self.conn_state[conn.fileno()]
            # 将ip和地址和addr绑定在一起，如果ip支持重复，则关掉这个fd
            if addr not in self.addr_fd:
                self.addr_fd[addr] = conn.fileno()
                # 更改这个fd为send模式
                sock_state.state = "send"
                # 服务端发送ping客户端回复pong保持链接
                sock_state.buff_send = "%010d%s" % (len("ping"), "ping")
                sock_state.need_send = len(sock_state.buff_send)
                self.epoll_sock.modify(conn.fileno(), select.EPOLLOUT)
                # 将ip和地址和addr绑定在一起，如果ip支持重复，则关掉这个fd
                sock_state.state_log(run_linenumber() + "accept2send: fd %s to send state" % conn.fileno())
            else:
                sock_state.state_log(run_linenumber() + "accept2send: fd %s ip addr repeat close" % conn.fileno())
                sock_state.state = "closing"
                self.state_machine(conn.fileno())
        # 如果获取到的是retry就什么都不操作，让epoll根据信号会再次执行状态机
        else:
            pass

    def read2process(self, fd):
        '''处理read状态，并传入proces进行执行'''
        # 获取read状态
        read_ret = self.read(fd)
        # 获取状态如果read执行完了则使用process进行处理
        # 如果其他状态不用处理,让epoll根据信号再次读取
        if read_ret == "read_finish":
            # 运行send
            self.process2send(fd)
        elif read_ret in ("read_content", "read_continue", "retry"):
            pass
        elif read_ret == "closing":
            self.conn_state[fd].state = 'closing'
            self.state_machine(fd)
        # 如果返回正确的状态则抛出异常
        else:
            raise Exception("impossible state returned by self.read")

    def process2send(self, fd):
        '''处理process状态，并直接使用send进行执行'''
        # 获取process状态
        process_ret = self.process(fd)
        # 如果process 处理完毕，改变为send状态
        if process_ret == "process_finish":
            # 更改这个fd状态
            sock_state = self.conn_state[fd]
            sock_state.state = "send"
            # 改变epoll状态为写状态，改变后epoll会收到写信号epoll检测到后，会自动执行
            # 状态机不用手动切换
            self.epoll_sock.modify(fd, select.EPOLLOUT)
            sock_state.state_log(run_linenumber() + "accept2process: fd %s to send state" % fd)
        else:
            raise Exception("impossible state returned by self.process")

    def send2read(self, fd):
        '''使用send发送process处理的数据
        处理完后返回read状态继续监听客户端发送'''
        # 获取 send 状态
        send_ret = self.send(fd)
        if send_ret in ("send_continue", "retry"):
            pass
        # 如果已经发送完成初始化状态机，调整为read状态,改变epoll为监听状态继续监听
        elif send_ret == "send_finish":
            sock_state = self.conn_state[fd]
            conn = sock_state.sock_obj
            addr = sock_state.sock_addr
            # 这里要更改，如果有读数据不能全部初始化，要只初始化发送的那部分
            self.set_fd(conn, addr)
            self.conn_state[fd].state = "read"
            self.epoll_sock.modify(fd, select.EPOLLIN)
            self.conn_state[fd].state_log(run_linenumber() + "accept2process: fd %s to read state" % fd)
        elif send_ret == "closing":
            self.conn_state[fd].state = 'closing'
            self.state_machine(fd)
        else:
            raise Exception("impossible state returned by self.send")

    def close(self, fd):
        '''重写关闭'''
        sock_state = self.conn_state[fd]
        sock_state.state_log(run_linenumber() + "close: close fd %s " % fd) 
        # 一定要先取消epoll注册，在关闭连接
        # 因为epoll运行过快，会发生socket关闭，epoll还没取消注册又收到信号的情况
        self.epoll_sock.unregister(fd)
        # 关闭sock
        sock = self.conn_state[fd].sock_obj
        sock.close()
        # 如果这个fd和某个ip绑定了则同时删除这个ip链接
        if fd == self.addr_fd.get(sock_state.sock_addr, None):
            self.addr_fd.pop(sock_state.sock_addr)
        # 从链接状态字典中删除这个fd
        self.conn_state.pop(fd)

    def logic(self, data, sock_state):
        # 将收到的命令发布出去
        if data == "pong":
            return "active"
        else:
            cmd_data = {}
            data = json.loads(data)
            print data
            if isinstance(data, dict) and "host" in data and "cmd" in data:
                if data['host']  not in self.addr_fd:
                    return "not_find_host"
                
                cmd_data['host'] = sock_state.sock_addr
                cmd_data['cmd'] = data['cmd']
                response = json.dumps(cmd_data)
                print  self.addr_fd
                print  data['host']
                cmd_sock_state = self.conn_state[self.addr_fd[data['host']]]
                new_buff_send = "%010d%s" % (len(response), response)
                cmd_sock_state.buff_send += new_buff_send
                cmd_sock_state.need_send += len(new_buff_send)
            else:
                return "error_data"
            if cmd_sock_state.state == "read":
                print "999"*10
                cmd_sock_state.state = "send"
                conn = cmd_sock_state.sock_obj
                print conn.fileno()
                self.epoll_sock.modify(conn.fileno(), select.EPOLLOUT)
            return "cmd_send_end"


if __name__ == "__main__":
    '''反转测试
    def logic(in_data):
        return in_data[::-1]
    '''
    '''多进程启动
    sock = bind_socket("0.0.0.0", 10000)
    fork_processes(4)
    reverseD = nbNet(sock, logic)
    reverseD.run()
    '''
    '''单进程启动'''
    sock = bind_socket("0.0.0.0", 10000)
    reverseD = nbNetPORT(sock)
    reverseD.run()
