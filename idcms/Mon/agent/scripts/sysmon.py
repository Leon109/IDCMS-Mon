#!/usr/bin/env python
'''
获取系统的监控信息
发送给传输层
'''
from __future__ import print_function
import os
import time
import socket
import inspect


class mon():
    '''系统监控'''
    def __init__(self):
        self.data = {}

    def getLoadAvg(self):
        with open('/proc/loadavg') as load_open:
            load_average = load_open.read().split()[0]
            return   float(load_average)
    
    def getMemTotal(self):
        with open('/proc/meminfo') as mem_open:
            memtotal = int(mem_open.readline().split()[1]) / 1024
            return memtotal
    
    def getMemUsage(self, noBufferCache=True):
        if noBufferCache:
            with open('/proc/meminfo') as mem_open:
                memtotal = int(mem_open.readline().split()[1])
                memfree = int(mem_open.readline().split()[1])
                memavailable = int(mem_open.readline().split()[1])
                membuffer = int(mem_open.readline().split()[1])
                memcache = int(mem_open.readline().split()[1])
                return (memtotal-memfree-membuffer-memcache)/1024
        else:
            with open('/proc/meminfo') as mem_open:
                used = int(mem_open.readline().split()[1]) - int(mem_open.readline().split()[1])
                return used / 1024
    
    def getMemFree(self, noBufferCache=True):
        if noBufferCache:
            with open('/proc/meminfo') as mem_open:
                memtotal = int(mem_open.readline().split()[1])
                memfree = int(mem_open.readline().split()[1])
                memavailable = int(mem_open.readline().split()[1])
                membuffer = int(mem_open.readline().split()[1])
                memcache = int(mem_open.readline().split()[1]) 
                return (memfree+membuffer+memcache)/1024
        else:
            with open('/proc/meminfo') as mem_open:
                mem_open.readline()
                memfree = int(mem_open.readline().split()[1])
                return a / 1024
    
    def getlinknumber(self):
        link = os.popen('ss -ntp | wc -l','r')
        return link.read().strip('\n')

    def getTime(self):
        return int(time.time())
    
    def runAllGet(self):
        for fun in inspect.getmembers(self, predicate=inspect.ismethod):
            if fun[0][:3] == 'get':
                self.data[fun[0][3:]] = fun[1]()
        return self.data

if __name__ == "__main__":
    print (mon().runAllGet(), end='')
