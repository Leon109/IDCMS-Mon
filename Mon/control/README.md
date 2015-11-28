# 控制端和执行系统命令

1 PASV模式下直接发送命令到客户端

2 PORT模式下，所有客户端使用agent（agent下的agent_port.py）链接到控制端，执行命令也发送到

控制端，由控制端在转发到客户端

3 PASV下命令格式

｛'cmd': 执行命令 'timeout': 命令执行超时时间｝

  PORT下命令个是

｛'host': 接受命令主机ip cmd': 执行命令 'timeout': 命令执行超时时间｝
 
 "query" 获取所有连接的主机 

4 返回

timeout : 超时

error_data : 发送数据格式错误

not_find_host: 没有找到主机

cmd_send_end : 成功发送命令
