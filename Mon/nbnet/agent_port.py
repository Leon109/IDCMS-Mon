import socket

def agnet_post(addr, port, logic):
   sock=None
   while True:
       try:
           # 判断soket是否存在，不存在则创建
           if sock == None:
               sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
               # 设置阻塞模式下的超时时间，如果超时了会发出一个socket超时异常
               # 注意设置超时链接后socket会变成非阻塞模式，.settimeout(None)变回阻塞模式
               sock.settimeout(5)
               sock.connect((host, port))
               sock_list[0].settimeout(None)
           # 接收数据前10个自己计算需要接受的数据大小
           count = sock.recv(10)
           # 如果接收失败发送异常(抛出一个异常进行重试)
           if not count:
               raise  ValueError
           # 统计需要接收数据大小
           count = int(count)
           # 接受数据
           buf = sock.recv(count)
           if buf == "ping":
               sock.sendall("%010d%s"%(len("pong"), "pong"))
           else:
               send
           raise socket.error
       # 发生socket，或者valueError（如接受的前10个字节不是数字）则关闭连接,然后继续重连
       except (socket.error, ValueError), msg:
           sock_list[0].close()
           sock_list[0] = None
           retry += 1
   return False
