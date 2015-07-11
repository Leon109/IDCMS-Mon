#!/usr/bin/env python
#coding=utf-8

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

# 调用日志模块
logger = Logger.getLogger()
# debug开关
debug = True

class _STATE(object):
    """
    链接状态
    """
    def __init__(self):
        self.state = 'accept'
        # 需要读取的字节数
        self.need_read = 10
        self.need_write = 0
        # 已经收到的字节数
        self.have_read = 0
        self.have_write = 0
        # 读写缓存 
        self.buff_read = ""
        self.buff_write = ""
        # socket 对象
        self.seck_obj = ""

    # 对状态机进行debug调用方法
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

# 生成一个要监听的socket
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
        # 链接状态字典,每个链接根据socket连接符建立一个字典，字典中链接状态机
        self.conn_state = {}

        # 使用setFD将根据每个socket链接符存入状态机中
        self.setFd(sock)
        # 新建epoll事件对象，后续要监控的事件添加到其中
        self.epoll_sock = select.epoll()
        # 第一个参数向epoll句柄中注册监听socket的可读事件（这个fd用于监听）
        # 第二个实用的是一个epoll的事件掩码 EPOLLIN 默认是只读
        # 具体可以参考https://docs.python.org/2.7/library/select.html?highlight=epoll#select.poll.register
        self.epoll_sock.register(sock.fileno(), select.EPOLLIN)

        # 处理绑定方法
        self.logic = logic
        # 通过不同状态调用不通的方法
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
        # 使用soket连接符(这个fileno获取socket连接符，是个整数)做key链接状态机
        self.conn_state[sock.fileno()] = tmp_state
        # 调用debug方法的时候日志记录当前的状态
        # logger.info('def setFD')
        # self.conn_state[sock.fileno()].state_log()

    def state_machine(self, fd):
        # 取出fd
        sock_state = self.conn_state[fd]
        # 根据fd不同状态执行不同方法
        self.sm[sock_state.state](fd)

    def accept(self, fd):
        '''接受新传入的fd，为新fd注册
        '''
        try:
            # 取出fd（这里是监听的的那个fd）
            sock_state = self.conn_state[fd]
            # 取出sock（取出监听的soket）
            sock = sock_state.sock_obj
            # 使用accept方法为新进请求连接的连接，返回一个元组conn是一个新的socket连接，addr是连接的客户端地址
            conn, addr = sock.accept()
            # 设置socket为非阻塞
            conn.setblocking(0)
            # 向epoll中注册链接到socket新的fd
            self.epoll_sock.register(conn.fileno(), select.EPOLLIN)
            # 将这个获取到的conn链接存入状态机sock
            self.setFd(conn)
            # 更改这个fd的状态为read epoll自动处理，根据状态执行不通的方法
            self.conn_state[conn.fileno()].state = "read"
        except socket.error as msg:
            # ECONNABORTED防止TCP链接三次握手后再次放松RST
            # EAGIIN 防止缓冲区满了等错误，这两个错误发生后
            # 再次运行accept
            if msg.args[0] in (errno.ECONNABORTED, errno.EAGAIN):
                return
            raise

    def read(self, fd):
        '''读取fd(appcet执行完后，切换到read状态)
        这里逻辑是这样的 先读10个字节头 根据10个字节头算出要接受数据的大小
        然后在次进行读，读完后交给process处理，读的时候不要使用self.state_machine(fd)强制
        虚幻调用了，容易触发python的最大递归次数，让epoll自己判断，就行读写
        '''
        # 根据传入的fd取出socket
        sock_state = self.conn_state[fd]
        conn = sock_state.sock_obj
        try:
            # 判断需要读的字节数是不是小于等于0,比如客户端发送了10个0过来(状态机里面的need_read)
            if sock_state.need_read <= 0:
                # 如果小于等于0 关闭链接将状态机切换到 closing 并执行状态机
                # 或者直接抛出异常让异常处理关闭连接
                raise socket.error

            # 进行读取(使用recv)
            one_read = conn.recv(sock_state.need_read)
            # 读取后有三种情况
            # 1 判断如果读取后字节数是0则返回空（这种情况，如数据在接受的时候可以
            # 什么数据也没有发过来（如tcp校验失败）这样直接返回，epoll会重新处理
            # 2 wirte结束后如果客户端没有发送数据，或者因为非阻塞发生异常
            # [Errno 11] Resource temporarily unavailable，异常处理会返回read状态
            # 3 客户端关闭，tcp也会发送一个空FIN文件过来（如果这种情况下不关闭会有问题
            # 应为客户端关闭了，epoll没有关闭信号，如果没有关闭连接进行处理，epoll会认为
            # 这个事件没有处理，一直需要读这里就会一直读死循环，造成cpu 100%)
            # 所以这里应该关闭连接，不应该使用return
            if len(one_read) == 0:
                # return
                raise socket.error

            # 将收到的数据存入buff
            sock_state.buff_read += one_read
            # 修改已经接受的字节数
            sock_state.have_read += len(one_read)
            # 修改还需要读取的字结数
            sock_state.need_read -= len(one_read)

            # 先处理前10个协议头(这里下面不用做处理的原因是如果epoll
            # 发现有了新数据会自动调用read，如果第一次读了5个自己卡住了，
            # 下次会继续所以只要判断前10个字节协议头就好)
            if sock_state.have_read == 10:
                # 判断读取前十个字节是否是数字
                # 如果不是数字抛出socket.error异常，产生这个异常后后面的异常处理就会关闭连接
                if not sock_state.buff_read.isdigit():
                    raise socket.error
                # 假如读取的数小于0抛出socket.error异常，产生这个异常后后面的异常处理就会关闭连接
                elif int(sock_state.buff_read) <= 0:
                     raise socket.error
                # 计算下次需要读取的大小
                sock_state.need_read += int(sock_state.buff_read)
                # 清空缓存
                sock_state.buff_read = ''
                # 根据取道的字节数再次进行读取
                # 注意这里不要掉用self.state_machine(fd) 不要自己手动调用，让epoll自动调用
                # 如果直接调用会形成  write 》read 》read 》process 》 write 这样都使用state_machine形成递归情况，
                # python 对递归有次数由限制，所以次read状态时让epoll自动进检查,epoll发现有数据后会再次调用read所以
                # 这里就不需要强制使用self.state_machine(fd)了
                # 而且比如用户发送的10个字节头，但是后面没有数据停顿了还没有发过来，还会发生socket erron =11 这种错误

            # 如果need_read 等于0 说明已经读取完毕，可以执行process进行处理了   
            elif sock_state.need_read == 0:
                sock_state.state = "process"
                self.state_machine(fd)

        # 发生错误如soket断开链接等，或者valueerror（发上输入错误，这个比如输的前10个自己中包含了了字母）执行closing字段       
        except socket.error, msg:
            # 这里发生错误如客户端断开连接等要将状态及状态调整为cloing，关闭连接
            # 要单独处理socket 11 错误时由于比如用户发送的10个字节头，但是后面没有数据停顿了还没有发过来，就会发生这种错误
            # 还有就是非阻塞socket时，若读不到数据就会报这个错误，所以不需要特别处理，返回空值让上层代码继续epoll或者循环读取。
            # 这里因为write完后会返回读的状态，再次读取值会是空置也会发生这个错误。
            if msg.errno == 11:
                    return
            sock_state.state = "closing"
            self.state_machine(fd)

    def process(self, fd):
        '''read完成后进行 process 进行处理
        '''
        # 读取socket
        sock_state = self.conn_state[fd]
        # 获取输入
        response = self.logic(sock_state.buff_read)
        # 将获取的输入的字符串获取到后进行拼接写入buff_write
        sock_state.buff_write = "%010d%s" % (len(response), response)
        # 统计发送字节数
        sock_state.need_write = len(sock_state.buff_write)
        # 改变状态机状态
        sock_state.state = "write"
        # 改变epoll状态为写状态
        self.epoll_sock.modify(fd, select.EPOLLOUT)
        # 执行write状态
        self.state_machine(fd)

    def write(self, fd):
        '''像客户端发送请求
        '''
        # 取出socket
        sock_state = self.conn_state[fd]
        conn = sock_state.sock_obj
        # 定义发送从第几个字节开始
        last_have_send = sock_state.have_write
        try:
            # 取出发送数据 conn.send 会返回发送的字节数 
            have_send = conn.send(sock_state.buff_write[last_have_send:])
            # 统计已经发送的字节
            sock_state.have_write += have_send
            # 计算出还需要发送的字节
            sock_state.need_write -= have_send
            # 判断如果所有数据已经发送完了， 并且已经有发送的字节数
            if sock_state.need_write == 0 and sock_state.have_write != 0:
                # 改变状态机状态继续进行读,这个用户可能还会发送数据
                self.setFd(conn)
                self.conn_state[fd].state = "read"
                self.epoll_sock.modify(fd, select.EPOLLIN)
        except socket.error, msg:
            # 在send发送数据时如果socket缓冲区满了epoll会进入阻塞模式等待再次发送
            # 所以产生这个错的的时候[Errno 11] Resource temporarily unavailable
            # 不需要处理，让epoll自动处理就好,直接返回让epoll在继续写
            if msg.errno == 11:
                return
            sock_state.state = "closing"
            self.state_machine(fd)

    def close(self, fd):
        '''关闭连接
        '''
        self.epoll_sock.unregister(fd)
        # 关闭sock
        sock = self.conn_state[fd].sock_obj
        sock.close()
        # 取消epoll注册
        self.epoll_sock.unregister(fd)
        # 从链接字典中删除这个fd
        self.conn_state.pop(fd)

    def run(self):
        '''运行程序
          监听epoll是否有新链接过来
        '''
        while True:
            # epoll对象哪些套接字在最近一次查询后又有新的需要注册的事件到来，然后根据状态及状态进行执行
            # 如果没有对象过来，epoll就会组赛道这里
            epoll_list = self.epoll_sock.poll()
            for fd, events in epoll_list:
                sock_state = self.conn_state[fd]
                # 确认 epoll状态如果有io事件 epoll hang住则关闭连接
                if select.EPOLLHUP & events:
                    sock_state.state = "closing"
                # 如果IO时间epoll发生错误也关闭连接
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
    # 字典以pid为key 进程数位值
    children = {}
    
    # 创建子进程
    def start_child(i):
        pid = os.fork()
        if pid == 0:
            #在子进程里运行的东西
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
            # 等待子进程结束os.wait()回收
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
        # 进程结束后从字典中删除,并返回事第几个进程
        id = children.pop(pid)
        # 可以根据不同状态计入日志
        # 如果进程由于信号而退出，则返回True，否则返回False
        if os.WIFSIGNALED(status):
            pass
        # 如果WIFEXITED(status)返回True，则返回一个整数，该整数是exit()调用的参数。否则返回值是未定义的
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
