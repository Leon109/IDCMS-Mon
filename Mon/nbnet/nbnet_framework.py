#!/usr/bin/env python
#coding=utf-8

from nbnet_base import *

# 调用父目录模块
workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.utils import run_linenumber

# 重新定义日志模块应为__file__模块发生了变化

class nbNet(nbNetBase):
    '''nbNet处理架构'''
    def __init__(self, sock, logic):
        # 继承父类init
        super(nbNet, self).__init__(sock, logic)
        # 状态机切换规则
        self.sm = {
            "accept" : self.accept2read,
            "read"   : self.read2process,
            "process": self.process2write,
            "write"  : self.write2read,
            "closing": self.close,
        }

    def accept2read(self, fd):
        '''获取socket，并使socket转换为read状态
        注意 这里的fd 是监听的fd（第一个创建的fd）'''
        # 通过父类获取socket链接
        accept_ret = self.accept(fd)
        # 如果获取到了socket对象，进行epoll注册，状态为只读，创建状态机
        # 并改变状态机状态为read
        if not accept_ret == "retry":
            conn = accept_ret[0]
            addr = accept_ret[1]
            # 初始化这个socket，设置为epool读模式
            self.set_fd(conn, addr)
            self.epoll_sock.register(conn.fileno(), select.EPOLLIN)
            # 更改这个fd为rede模式
            sock_state = self.conn_state[conn.fileno()]
            sock_state.state = "read"
            sock_state.state_log(run_linenumber() + "accept2read: fd %s to read state" % conn.fileno())
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
            self.process2write(fd)
        elif read_ret in ("read_content", "read_continue", "retry"):
            pass
        elif read_ret == "closing":
            self.conn_state[fd].state = 'closing'
            self.state_machine(fd)
        # 如果返回正确的状态则抛出异常
        else:
            raise Exception("impossible state returned by self.read")

    def process2write(self, fd):
        '''处理process状态，并传入wirte进行执行'''
        # 获取process状态
        process_ret = self.process(fd)
        # 如果process 处理完毕，改变为write状态
        if process_ret == "process_finish": 
            # 改变fd状态机状态
            sock_state = self.conn_state[fd]
            sock_state.state = "write"
            # 改变epoll状态为写状态，改变后epoll会收到写信号epoll检测到后，会自动执行
            # 状态机不用手动切换
            self.epoll_sock.modify(fd, select.EPOLLOUT)
        else:
            raise Exception("impossible state returned by self.process")

    def write2read(self, fd):
        '''使用write发送process处理的数据
        处理完后返回read状态继续监听客户端发送'''
        # 获取 write 状态
        write_ret = self.write(fd)
        if write_ret in ("write_continue", "retry"):
            pass
        # 如果已经发送完成初始化状态机，调整为read状态,改变epoll为监听状态继续监听
        elif write_ret == "write_finish":
            sock_state = self.conn_state[fd]
            conn = sock_state.sock_obj
            addr = sock_state.sock_addr
            self.set_fd(conn, addr)
            self.conn_state[fd].state = "read"
            self.epoll_sock.modify(fd, select.EPOLLIN)
        elif write_ret == "closing":
            self.conn_state[fd].state = 'closing'
            self.state_machine(fd)
        else:
            raise Exception("impossible state returned by self.write")


if __name__ == "__main__":
    '''反转测试'''
    def logic(in_data):
        return in_data[::-1]
    '''多进程启动
    sock = bind_socket("0.0.0.0", 9000)
    fork_processes(0)
    reverseD = nbNet(sock, logic)
    reverseD.run()
    '''
    
    '''单进程启动'''
    sock = bind_socket("0.0.0.0", 10000)
    reverseD = nbNet(sock, logic)
    reverseD.run()
