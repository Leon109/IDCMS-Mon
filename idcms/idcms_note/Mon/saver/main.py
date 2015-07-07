#!/usr/bin/env python
# coding=utf-8

import os
import sys
import json

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.nbnetdb import db
from utils.config import config
from simpleNet.nbNetFramework import bind_socket, nbNet

# saver配置文件
saver_conf = config('nbnet', 'saver')

# 要写入的表，这里进行了分表
monTables = [
    'stat_0',
    'stat_1',
    'stat_2',
    'stat_3',
]

def fnvhash(string):
    '''一个fnv哈希的实现'''
    # 初始hash值（一个质数）
    hash = 97
    for i in string:
        # 对输入的每个字符的ascii码进行异或预算并乘一个质数
        hash = hash ^ ord(i) * 13
    return hash

def insertMonData(data):
    '''数据写入数据库'''
    # 将发过来json数据转换成python格式
    data = json.loads(data)
    # 写入时间
    dTime = int(data['Time'])
    # 将主机的主机名使用fnv哈希，然后通过取余数，算出写入哪个分表中
    hostIndex = monTables[fnvhash(data['Host']) % len(monTables)]
    sql = ("INSERT INTO `%s` (`host`,`mem_free`,`mem_usage`,`mem_total`,`load_avg`,`time`)" 
    "VALUES('%s', '%d', '%d', '%d', '%s', '%d')" % (hostIndex, data['Host'], data['MemFree'], 
    data['MemUsage'], data['MemTotal'],data['LoadAvg'], dTime))
    result = db.execute(sql)
    

if __name__ == '__main__':
    # 监听地址和端口
    addr = saver_conf['addr']
    port = int(saver_conf['port'])
   
    # 处理程序
    def logic(data):
        insertMonData(data)
        return("OK")
    
    sock = bind_socket(addr, port)
    saverD = nbNet(sock, logic)
    saverD.run()
