#!/usr/bin/env python
#coding=utf-8

"""一个简单的epoll实现的网络协议
通过接收客户端的前10个字节，获取传输文件大小，然后进行处理
如国客户端发送 0000000002hi 服务端收到的就是hi 然后进程处理
后发送给客户端
"""

from nbNetBase import *

# 初始化debug日志(都是从netBase引入的)
if debug == "True":
    logs = DebugLog(__file__)

class nbNet(nbNetBase):
    '''nbNet处理架构'''
    def __init__(self, sock, logic):
        # 继承父类init
        super(nbNet, self).__init__(sock, logic)
        # 自定义处理方法
        self.sm = {
            "accept" : self.accept2read,
            "read"   : self.read2process,
            "write"  : self.write2read,
            "process": self.process,
            "closing": self.close,
        }

    def accept2read(self, fd):
        '''获取socket，并使socket转换为read状态'''
        # 通过父类获取socket链接
        conn_addr = self.accept(fd)
        # 如果获取到的是retry就什么都不操作，让epoll判断进行再次读取
        # 如国获取到了socket对象，进行epoll注册，创建状态机
        # 并改变状态机状态为read
        if not conn_addr == "retry":
            conn = conn_addr[0]
            addr = conn_addr[1]
            self.setFd(conn, addr)
            self.epoll_sock.register(conn.fileno(), select.EPOLLIN)
            logs.dblog("***chang socket fd(%s) state to read***" % conn.fileno())
            self.conn_state[conn.fileno()].state = "read"
        else:
            pass

    def read2process(self, fd):
        '''处理read状态，并传入proces进行执行'''
        # 获取read状态
        try:
            read_ret = self.read(fd)
        except Exception, msg:
            # 发生错误后切换到closing状态
            read_ret = "closing"
        # 获取状态如果是process状态嗲用process进行处理
        # closing状态关闭连接，如果其他状态不用处理,让epoll判担在次读取
        if read_ret == "process":
            self.process(fd)
        elif read_ret == "readcontent":
            pass
        elif read_ret == "readmore":
            pass
        elif read_ret == "retry":
            pass
        elif read_ret == "closing":
            self.conn_state[fd].state = 'closing'
            self.state_machine(fd)
        # 如果返回了其他问题，择抛出异常
        else:
            raise Exception("impossible state returned by self.read")

    def write2read(self, fd):
        '''使用write发送process处理的数据
        处理完后返回read状态继续监听客户端发送'''
        try:
            write_ret = self.write(fd)
        except socket.error, msg:
            write_ret = "closing"
        
        if write_ret == "writemore":
            pass
        # 如果已经发送完成调整为read状态,改变epoll为监听状态继续监听
        elif write_ret == "writecomplete":
            sock_state = self.conn_state[fd]
            conn = sock_state.sock_obj
            addr = sock_state.sock_addr
            self.setFd(conn, addr)
            logs.dblog("***chang socket fd(%s) state to read***" % fd)
            self.conn_state[fd].state = "read"
            # 在改为read状态后加入一个时间戳监控执行时间
            self.conn_state[fd].read_stime = time.time()
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
    sock = bind_socket("0.0.0.0", 9000)
    reverseD = nbNet(sock, logic)

    import threading
    class controlThread (threading.Thread):
        '''使用多线程，一个线程运行nbnet，另一个监控fd状态是否超时'''
        def __init__(self, name):
            threading.Thread.__init__(self)
            self.name = name
        
        def run(self):
            if self.name == 'ctl_start':
                self.ctl_start()
            elif self.name == 'check':
                self.check()

        def ctl_start(self):
            reverseD.run()
    
        def check(self):
            reverseD.check_fd()

    def startTh():
        ctl = controlThread('ctl_start')
        ctl.start()
        check_fd = controlThread('check')
        check_fd.start()
        ctl.join()
        check_fd.join()
    startTh()
