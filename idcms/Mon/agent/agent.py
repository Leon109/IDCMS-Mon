#!/usr/bin/env python

import os
import sys
import time
import json
import signal
from  multiprocessing import Pipe
from agent_utils import Command, get_iphostname

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.config import config
from simpleNet.nbNetUtils import sendData_mh

get_data, put_data = Pipe(duplex=False)
agent_conf = config('agent', 'global')
sleep_time = int(agent_conf['sleep'])


def send_data():
    '''接受管道传过来的数据
    发送给传输层
    '''
    trans_l = agent_conf['trans_l'].split(';')
    agent_sock_l = [None]
    while True:
        data = get_data.recv()
        sendData_mh(trans_l, json.dumps(data), agent_sock_l)

def init_runlist():
    '''生成任务列表'''
    items = config('agent')
    items.remove('global')
    script_dir = 'scripts/'
    run_list = []
    for item in items:
        item_conf = config('agent', item)
        if not item_conf['timeout']:
            item_conf['timeout'] = agent_conf['timeout']
        item_conf['last_time'] = None
        item_conf['script_ptah'] = script_dir + item_conf['name']
        script_path = item_conf['script_ptah']
        if not os.path.exists(script_path):
            raise  Exception('script %s not find' % script_path)
            sys.exit(1)
        run_list.append(item_conf)
    
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
                    continue
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
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

if  __name__ == "__main__":
    pid = os.fork()
    if pid == 0:
        send_data()
    runlist = init_runlist()
    send_data = get_iphostname()
    lisent_sigchld()
    run_task()
