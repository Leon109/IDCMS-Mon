#!/usr/bin/env python
#coding=utf-8

import socket

# 使用socket像多台主机发送数据
def sendData_mh(host_l, data, sock_l, single_host_retry=3):
    """
    # host 使用一个列表，以主机名或者IP开头后面跟端口
    # 这是假如同时有多个host(多个host写入一个数据库)，只要向一个host发送成功就可以关闭连接
    host_l = ["localhost:50001","127.0.0.1:50001"]
    data 数据
    sock_l = [some_socket] 
    sock_l sock使用列表方式传入，这样的好处是可以判断socket是否为空
    而且加入sock使用列表传入经过函数处理后列表也会发生变化，不会是原来的状态
    python 字符串，数字和元组时不可变变量，字典和列表是可变变量,通过这一状态
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
    # 循环像所有主机发送数据只要一个正确接收返回True
    for host_port in host_l:
        # 计算出主机和端口
        host,port =host_port.split(':')
        # 端口要使用int类型
        port = int(port)
        # 发送重试计数器
        retry = 0
        while retry < single_host_retry:
            try:
                # 去除socket判断soket是否存在，不存在这创建
                if sock_l[0] == None:
                    sock_l[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # 设置阻塞模式下的超时时间，如果超时了会发出一个socket超时异常单位是秒
                    # 注意设置超时链接后socket会变成非阻塞模式，.settimeout(None)变回阻塞模式
                    sock_l[0].settimeout(5)
                    sock_l[0].connect((host, port))
                    sock_l[0].settimeout(None)
                # 发送数据
                sock_l[0].sendall("%010d%s"%(len(data), data))
                # 接收数据前10个自己计算需要接受的数据大小
                count = sock_l[0].recv(10)
                # 如果接收失败发送异常(抛出一个异常进行重试)
                if not count:
                    raise  ValueError
                # 统计需要接收数据大小
                count = int(count)
                # 接受数据
                buf = sock_l[0].recv(count)
                # 如果数据最后两个字符是 OK 说明已经接收成功,重置计数器,并return 结果结束程序退出程序
                if buf == "OK":
                    return True 
                # 如果返回的不是OK,抛出一个socket错误进行重试
                raise socket.error
            # 发生socket，或者valueError（如接受的前10个字节不是数字）则关闭连接,然后继续重连
            except (socket.error, ValueError), msg:
                sock_l[0].close()
                sock_l[0] = None
                retry += 1
        return False


