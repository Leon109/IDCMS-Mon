#!/usr/bin/env python

import socket

def sendData(host, port, data, sock_l, single_host_retry=3):
    '''
    host  连接接受数据的主机
    port  接受数据的端口
    data  数据
    sock_l sock使用列表方式传入，这样的好处是可以判断socket是否为空
    而且加入sock使用列表传入经过函数处理后列表也会发生变化，不会是原来的状态
    python 对简单的数据类型是用的引用，对高级的数据类型使的复制
    In [5]: a = 1
    In [6]: def s(l):
    ...:     l +=1
    ...:     
    In [7]: s(a)
    In [8]: a
    Out[8]: 1
    In [9]: def x(l):
    ...:     l[0] +=1
    ...:     
    In [10]: z = [a]
    In [11]: x(z)
    In [12]: z
    Out[12]: [2]
    single_host_retry 发送数据重试次数
    '''
    retry = 0 
    while retry < single_host_retry:
        try:
            if sock_l[0] == None:
                sock_l[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
                sock_l[0].settimeout(5)
                sock_l[0].connect((host, port))
                sock_l[0].settimeout(None)
            sock_l[0].sendall("%010d%s"%(len(data), data)) 
            count = sock_l[0].recv(10)
            if not count:
                raise Exception("socket,recv error", "recv no data")
            count = int(count)
            buf = sock_l[0].recv(count)
            if buf == "OK":
                return True 
            raise socket.error
        except:
            sock_l[0].close()
            sock_l[0] = None
            retry += 1

def sendData_mh(host_l, data, sock_l, single_host_retry=3):
    """
    host_l = ["localhost:50001","127.0.0.1:50001"]
    data 数据
    sock_l = [some_socket] 
    sock_l sock使用列表方式传入，这样的好处是可以判断socket是否为空
    而且加入sock使用列表传入经过函数处理后列表也会发生变化，不会是原来的状态
    python 对简单的数据类型是用的引用，对高级的数据类型使的复制,通过这一状态
    这样就能保证我门下次传入的socket还是跟上次一样的同一socket(以便保持常链接)
    (我们传入一个sock_l=[None],这个函数处理创建的socket就会在sock_l里面保留下来)
    In [5]: a = 1
    In [6]: def s(l):
    ...:     l +=1
    ...:     
    In [7]: s(a)
    In [8]: a
    Out[8]: 1
    In [9]: def x(l):
    ...:     l[0] +=1
    ...:     
    In [10]: z = [a]
    In [11]: x(z)
    In [12]: z
    Out[12]: [2]
    single_host_retry  发送数据重试次数
    sendData_mh(host_l,"this is data to send")
    """
    for host_port in host_l:
        host,port =host_port.split(':')
        port = int(port)
        retry = 0
        while retry < single_host_retry:
            try:
                if sock_l[0] == None:
                    sock_l[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock_l[0].settimeout(5)
                    sock_l[0].connect((host, port))
                    sock_l[0].settimeout(None)
                sock_l[0].sendall("%010d%s"%(len(data), data))
                count = sock_l[0].recv(10)
                if not count:
                    raise  ValueError
                count = int(count)
                buf = sock_l[0].recv(count)
                if buf == "OK":
                    return True 
                raise socket.error
            except (socket.error, ValueError), msg:
                sock_l[0].close()
                sock_l[0] = None
                retry += 1
        return False
