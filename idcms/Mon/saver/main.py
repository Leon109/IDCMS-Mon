#!/usr/bin/env python

import os
import sys
import json

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.nbnetdb import db
from utils.config import config
from simpleNet.nbNetFramework import bind_socket, nbNet

saver_conf = config('nbnet', 'saver')

monTables = [
    'stat_0',
    'stat_1',
    'stat_2',
    'stat_3',
]

def fnvhash(string):
    '''一个fnv哈希的实现'''
    hash = 97
    for i in string:
        hash = hash ^ ord(i) * 13
    return hash

def insertMonData(data):
    '''数据写入数据库'''
    data = json.loads(data)
    dTime = int(data['Time'])
    hostIndex = monTables[fnvhash(data['Host']) % len(monTables)]
    sql = ("INSERT INTO `%s` (`host`,`mem_free`,`mem_usage`,`mem_total`,`load_avg`,`time`)" 
    "VALUES('%s', '%d', '%d', '%d', '%s', '%d')" % (hostIndex, data['Host'], data['MemFree'], 
    data['MemUsage'], data['MemTotal'],data['LoadAvg'], dTime))
    result = db.execute(sql)
    

if __name__ == '__main__':
    addr = saver_conf['addr']
    port = int(saver_conf['port'])
   
    def logic(data):
        insertMonData(data)
        return("OK")
    
    sock = bind_socket(addr, port)
    saverD = nbNet(sock, logic)
    saverD.run()
