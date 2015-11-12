#!/usr/bin/env python
#coding=utf-8

import os
import sys
import time
import json
import signal
from  multiprocessing import Pipe

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.config import config
from utils.syscmd import Command, get_iphostname
from simpleNet.nbNetUtils import sendData_mh

# 使用multiprocessing封装好的Pipe包
get_data, put_data = Pipe(duplex=False)
# 全局配置文件
agent_conf = config('agent', 'global')
sleep_time = int(agent_conf['sleep'])


def send_data():
    '''接受管道传过来的数据
    发送给传输层
    '''
    # 传输服务器里列表端口
    trans_l = agent_conf['trans_l'].split(';')
    # agent socket使用列表，具体参考sendData_mh
    agent_sock_l = [None]
    while True:
        # 从管道获取数据
        data = get_data.recv()
        # 发送给传输层
        sendData_mh(trans_l, json.dumps(data), agent_sock_l)

def init_runlist():
    '''生成任务列表'''
    # 获取所有配置项目
    items = config('agent')
    items.remove('global')
    # 运行脚本目录
    script_dir = 'scripts/'
    # 运行状态
    run_list = []
    # 初始化执行列表
    for item in items:
        item_conf = config('agent', item)
        if not item_conf['timeout']:
            item_conf['timeout'] = agent_conf['timeout']
        # 加入如开始时间
        item_conf['last_time'] = None
        # 脚本目录
        item_conf['script_ptah'] = script_dir + item_conf['name']
        script_path = item_conf['script_ptah']
        # 检查脚本是否存在
        if not os.path.exists(script_path):
            raise  Exception('script %s not find' % script_path)
            sys.exit(1)
        run_list.append(item_conf)
    
    # 初始任务化时间状态
    for task in run_list:
        if not task['last_time']:
            task['last_time'] = time.time()
        cmd = task['script_ptah'] 
        task['timeout'] = int(task['timeout']) 
        task['interval']= int(task['interval'])
    return run_list

def run_task():
    '''为每个脚本执行一个进程
    执行完毕后并关闭
    '''
    while True:
        for task in runlist:
            start_time =  time.time()
            name = task['name']
            cmd = task['script_ptah']
            timeout = task['timeout']
            interval = task['interval']
            last_time = task['last_time']
            if (start_time -last_time) >= interval:
                task['last_time'] = time.time()
                pid = os.fork()
                if pid > 0:
                    # 父进程继续循环执行任务列表
                    continue
                # 子进程执行命令,使用了subprocess，这个模块也使用了信号处理，
                # 如过父进程使用了信号监听,父进程会受到信号需要注意
                command = Command(cmd)
                recode, data, error = command.run(timeout)
                send_data['data'] = data
                send_data['name'] = name
                put_data.send(send_data)
                sys.exit(0)
        time.sleep(sleep_time)

def lisent_sigchld():
    '''监听子进程关闭信号
    通关指定函数关闭进程
    '''
    # SIG_IGN ：忽略的处理方式，将关闭信号交给INIT处理防止僵尸进程
    # 子进程状态信息会被丢弃，也就是自动回收了，使用了这个就不能使用wait和waitpid了
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

if  __name__ == "__main__":
    # fork一个进程处理接受发送数据
    pid = os.fork()
    if pid == 0:
        send_data()
    # 获取任务列表执行任务
    runlist = init_runlist()
    # 定义发送数据先获取主机ip和主机名
    send_data = get_iphostname()
    # 监听只子进程关闭信号
    lisent_sigchld()
    # 运行获取程序
    run_task()
