#!/usr/bin/env python
#coding=utf-8

"""一个简单的epoll实现的网络协议，这个模块定义了一些基础方法
通过接收客户端的前10个字节，获取传输文件大小，然后进行处理
如果客户端发送 0000000002hi 服务端收到的就是hi 然后进程处理
后发送给客户端
"""

import os
import sys
import time
import errno
import socket
import select
import multiprocessing

# 调用父目录模块
workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.monconf import config 
from utils.utils import run_linenumber

all_conf = config('mon.conf')
debug = all_conf.getboolean('nbnet', 'debug')
# 判断是否开启debug
if debug:
    # 初始化日志
    from utils.monlog import Logger
    logs = Logger.getLogger(debug=True)
    
class STATE(object):
    """状态机状态"""
    def __init__(self):
        self.state = 'accept'
        # 需要读取的字节数
        self.need_read = 10
        self.need_write = 0
        # 已经收到的字节数
        self.have_read = 0
        self.have_write = 0
        # 读写缓存 
        self.buff_read = ''
        self.buff_write = ''
        # socket 对象
        self.sock_obj = None
        # 客户端连接IP 
        self.sock_addr = None
        # 以下使用check_fd时才有效
        # 读取开始时间 
        self.read_stime= None
        # 默认read等待最大超时时间
        self.read_itime= all_conf.getint('nbnet', 'readtime')

    def state_log(self, info):
        '''debug显示每个fd状态'''
        if debug:
            msg = (
                '\n fd:{fd} \n state:{state}'
                '\n need_read:{need_read} \n need_write:{need_write}'
                '\n have_read:{have_read}\n have_write:{have_write}'
                '\n buff_read:{buff_read} \n buff_write:{buff_write}'
                '\n sock_obj:{sock_obj} \n sock_addr:{sock_addr}'
            ) .format(
                fd = self.sock_obj.fileno(), state = self.state,
                need_read = self.need_read, need_write = self.need_write,
                have_read = self.have_read, have_write = self.have_write,
                buff_read = self.buff_read, buff_write = self.buff_write,
                sock_obj = self.sock_obj, sock_addr = self.sock_addr
            )
            logs.debug('[nbnet] ' + info + msg)


def bind_socket(addr, port):
    '''生成监听的socket'''
    # AF_INET 表示用IPV4地址族，
    # SOCK_STREAM 是说是要是用流式套接字也就是使用TCP
    # 0 是指不指定协议类型，系统自动根据情况指定
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    # setsockopt(level,optname,value)
    # level:(级别)： 指定选项代码的类型。
    # SOL_SOCKET: 基本套接口
    # IPPROTO_IP: IPv4套接口
    # IPPROTO_IPV6: IPv6套接口
    # IPPROTO_TCP: TCP套接口
    # optname：选项名, 不能同类型选项也不相同
    # value: 选项值 这里value设置为1，表示将SO_REUSEADDR标记为TRUE，操作系统会在服务器socket被关闭或服务器进程终止
    # 后马上释放该服务器的端口，否则择根据系统内核设定时间关闭连接
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 监听的地址和端口
    sock.bind((addr, port))
    # listen 指明在服务器实际处理连接的时候，允许有多少个未决（等待）的连接在队列中等待
    sock.listen(10)
    return sock

class nbNetBase(object):
    '''无阻塞网络框架
    基础方法
    '''
    def __init__(self, sock, logic):
        '''初始化对象'''
        # 链接状态字典,每个链接根据socket连接符建立一个字典，字典中链接状态机
        self.conn_state = {}
        # 使用setFD将监听socket链接符存入状态机中,这个socket使用阻塞模式
        self.set_fd(sock)
        # 新建epoll事件对象，后续要监控的事件添加到其中
        self.epoll_sock = select.epoll()
        # 第一个参数向epoll句柄中注册监听socket的可读事件（这个fd用于监听）
        # 第二个使用的是一个epoll的事件掩码 EPOLLIN 是只读和默认epoll模式是水平触发模式
        self.epoll_sock.register(sock.fileno(), select.EPOLLIN)
        # 绑定处理方法
        self.logic = logic

    def set_fd(self, sock, addr=None):
        '''状态机初始化
        STATE() 是初始状态,具体参考STATE类
        conn_state 是一个自定义的字典，用于存取每个fd的状态
        '''
        # 创建初始化状态
        tmp_state = STATE()
        tmp_state.sock_obj = sock
        tmp_state.sock_addr = addr
        # conn_states是这字典使用soket连接符(这个fileno获取socket连接符，是个整数)做key链接状态机
        self.conn_state[sock.fileno()] = tmp_state
        # 将初始化状态记录到日志中
        self.conn_state[sock.fileno()].state_log(run_linenumber() + "set_fd: init socket fd %s" % sock.fileno())

    def state_machine(self, fd):
        '''跟据状态切换状态执行方法
        sm 是一个python下的switch 使用字典（需要自定义）
        如{'x':func0, "y":func1},使用不同的key执行不同的函数
        '''
        # 取出fd状态字典
        sock_state = self.conn_state[fd]
        # 记录执行前状态
        sock_state.state_log(run_linenumber() + "state_machine: runing fd %s state %s" % (fd, sock_state.state))
        # 根据fd不同状态执行不同方法
        self.sm[sock_state.state](fd)

    def accept(self, fd):
        '''accpet使用epoll等待客户端连接
        收到连接后返回一个新的客户端 非阻塞socket, 和IP地址
        '''
        try:
            # 取出fd（这里是监听的那个fd）
            sock_state = self.conn_state[fd]
            # 取出sock（取出监听的soket）
            sock = sock_state.sock_obj
            # 使用accept方法为新进请求连接的连接，返回一个元组conn是一个新的socket连接，
            # addr是连接的客户端地址和端口
            conn, addr = sock.accept()
            # 将spcket设置为非阻塞
            conn.setblocking(0)
            # 返回新链接进来的socket对象,和连接IP地址
            sock_state.state_log(run_linenumber() + "accept: find new socket client fd %s IP %s" % (conn.fileno(), addr[0]))
            return conn, addr[0]
        except socket.error as msg:
            # EAGIIN 防止缓冲区满了等错误，这两个错误发生后(erron代码是11)
            # ECONNABORTED防止TCP链接三次握手后再次发送RST(erron代码是103)
            # 再次运行accept 返回 重试 状态retry
            if msg.errno in (11, 103):
                return "retry"
    
    def read(self, fd):
        '''读取数据，读取要先将这个fd epoll注册，并变成为读状态
        epoll发现有读取信号会自动执行这个方法

        这里逻辑是这样的(协议设计) 先读10个字节头 根据10个字节头算出要接受数据的大小
        然后在次进行读取，直到读取完成
        
        '''
        # 根据传入的fd取出socket
        sock_state = self.conn_state[fd]
        conn = sock_state.sock_obj
        sock_state.state_log(run_linenumber() + "read: start read")
        try:
            # 判断需要读的字节数是不是小于等于0,比如客户端发送了10个0过来(状态机里面的need_read)
            if sock_state.need_read <= 0:
                # 如果小于等于0 关闭链接将状态机切换到 closing 并执行状态机
                # 或者直接抛出异常让异常处理关闭连接
                raise socket.error

            # 进行读取(使用recv),因为非阻塞socket会发生socket 11错误（如缓冲区读满）下面异常会处理
            one_read = conn.recv(sock_state.need_read)
            # 如果读取的结果为0有两种情况
            # 1 如epoll判断有数据需要接受但数据也没有发过来（如tcp校验失败)
            # 2 客户端关闭，tcp也会发送一个空FIN文件过来（如果这种情况下不关闭会有问题
            # 应为客户端关闭了，epoll没有关闭信号，如果没有关闭连接进行处理，epoll会认为
            # 这个事件没有处理，一直需要读这里就会一直读死循环，造成cpu 100%)
            if len(one_read) == 0:
                raise socket.error
            
            # 将收到的数据存入buff
            sock_state.buff_read += one_read
            # 修改已经接收的字节数
            sock_state.have_read += len(one_read)
            # 修改还需要读取的字结数
            sock_state.need_read -= len(one_read)
            # 读取状态记录到日志
            sock_state.state_log(run_linenumber() + 'read: read change')

            # 先处理前10个协议头
            if sock_state.have_read == 10:
                # 判断读取前十个字节是否是数字
                # 如果不是数字抛出socket.error异常，产生这个异常后后面的异常处理就会关闭连接
                if not sock_state.buff_read.isdigit():
                    raise socket.error
                # 假如读取的数小于0抛出socket.error异常，产生这个异常后后面的异常处理会关闭连接
                elif int(sock_state.buff_read) <= 0:
                     raise socket.error
                # 计算下次需要读取的大小
                sock_state.need_read += int(sock_state.buff_read)
                # 清空缓存
                sock_state.buff_read = ''
                # 协议头读取完后的状态记录到日志
                sock_state.state_log(run_linenumber() + "read: head read finsh")
                # 读取完毕后，返回读取内容状态
                return "read_content"
            # 如果need_read 等于0 说明已经读取完毕，可以进行下一步处理了
            elif sock_state.need_read == 0:
                # 读取完毕
                sock_state.state_log(run_linenumber() + "read: read finish")
                return "read_finish"
            else:
                # 如果都不符合说明没有读取完成继续读取
                return "read_continue"
        
        except socket.error, msg:
            # 这里发生错误如客户端断开连接等要将状态及状态调整为closing，关闭连接
            # 要单独处理socket 11 错误时由于比如用户发送的10个字节头，但是后面没
            # 有数据停顿了还没有发过来，就会发生这种错误, 还有非阻塞socket时，若读
            # 不到数据就会报这个错误，所以不需要特别处理, 继续进行重试
            if msg.errno == 11:
                return "retry"
            # 其他错误则返回关闭状态
            sock_state.state_log(run_linenumber() + "read: soket fd %s error %s" % (fd, msg))
            return "closing"

    def process(self, fd):
        '''程序处方法使用传入的logic方法进行处理'''
        # 读取socket
        sock_state = self.conn_state[fd]
        sock_state.state_log(run_linenumber() + "process: process start")
        # 获取处理完毕后的结果
        response = self.logic(sock_state.buff_read)
        # 将获取的输入的字符串获取到后进行拼接写入buff_write
        sock_state.buff_write = "%010d%s" % (len(response), response)
        # 统计发送字节数
        sock_state.need_write = len(sock_state.buff_write)
        # 返回处理完毕
        sock_state.state_log(run_linenumber() + "process: process finish")
        return "process_finish"

    def write(self, fd):
        '''wirte处理，注意在write处理前，要先将处理的fd改成写模式'''
        # 取出socket
        sock_state = self.conn_state[fd]
        conn = sock_state.sock_obj
        # 定义发送从第几个字节开始
        last_have_send = sock_state.have_write
        sock_state.state_log(run_linenumber() + "write: wire start")
        try:
            # 取出发送数据 conn.send 会返回发送的字节数
            have_send = conn.send(sock_state.buff_write[last_have_send:])
            # 统计已经发送的字节
            sock_state.have_write += have_send
            # 计算出还需要发送的字节
            sock_state.need_write -= have_send
            # 日志记录发送状态
            sock_state.state_log(run_linenumber() + "wirte: socket send state change")
            # 如果所有数据已经发送完了，并且已经没有发送的字节数, 说明已经发送完毕
            if sock_state.need_write == 0 and sock_state.have_write != 0:
                sock_state.state_log(run_linenumber() + "wirte: write end")
                return "write_finish"
            else:
                #如果不是，说明还没有发送完成继续发送
                return "write_continue"
        
        except socket.error, msg:
            # 在send发送数据时如果socket缓冲区满了epoll会进入阻塞模式等待再次发送
            # 所以产生这个错的的时候[Errno 11] Resource temporarily unavailable
            # 不需要处理,继续重试发送就好
            if msg.errno == 11:
                return "retry"
            sock_state.state_log(run_linenumber() + "write: soket fd %s error %s" % (fd, msg))
            return "closing"

    def close(self, fd):
        '''关闭连接'''
        sock_state = self.conn_state[fd]
        sock_state.state_log(run_linenumber() + "close: close fd %s " % fd)
        # 一定要先取消epoll注册，在关闭连接
        # 因为epoll运行过快，会发生socket关闭，epoll还没取消注册又收到信号的情况
        self.epoll_sock.unregister(fd)
        # 关闭sock
        sock = self.conn_state[fd].sock_obj
        sock.close()
        # 从链接状态字典中删除这个fd
        self.conn_state.pop(fd)

    def run(self):
        '''运行程序
        监听epoll是否有新连接过来
        '''
        while True:
            # epoll自动检测哪些套接字在最近一次查询后又有新的需要注册的事件到来，然后根据状态及状态进行执行
            # 如果没有对象过来，epoll就会阻塞在这里
            epoll_list = self.epoll_sock.poll()
            for fd, events in epoll_list:
                #events可以是以下几个宏的集合":"后面表示用数字表示,我们取到的events值就是数子
                #EPOLLIN ：1 表示对应的文件描述符可以读（包括对端SOCKET正常关闭）；
                #EPOLLPRI：2 表示对应的文件描述符有紧急的数据可读；
                #EPOLLOUT：4 表示对应的文件描述符可以写；
                #EPOLLERR：8 表示对应的文件描述符发生错误；
                #EPOLLHUP：16 表示对应的文件描述符被挂断；
                #EPOLLONESHOT：1073741824 只监听一次事件，当监听完这次事件之后，如果还需要继续监听这个socket的话，需要再次把这个socket加入到EPOLL队列里
                #EPOLLET：2147483648  将EPOLL设为边缘触发(Edge Triggered)模式，这是相对于水平触发(Level Triggered)来说的
                sock_state = self.conn_state[fd]
                sock_state.state_log(run_linenumber() + "run: epoll find fd %s new events: %s" % (fd, events))
                sock_state = self.conn_state[fd]
                # 如果有io事件epoll hang住则关闭连接
                if select.EPOLLHUP & events:
                    sock_state.state = "closing"
                # 如果IO时间epoll发生错误也关闭连接
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
    #   计算CPU核心数
    if num_processes is None or num_processes <= 0:
        num_processes = multiprocessing.cpu_count()
    # 字典以pid为key 进程数位值
    children = {}
    
    # 创建子进程
    def start_child(i):
        # i是运行的进程数
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
        # 如果WIFEXITED(status)返回True，WEXITSTATUS(status)则返回一个整数，该整数是exit()调用的参数。否则返回值是未定义的
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
