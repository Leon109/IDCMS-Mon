#!/usr/bin/env python

import os
import sys

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.config import config
from simpleNet.nbNetFramework import bind_socket, nbNet
from simpleNet.nbNetUtils import sendData_mh

trans_conf = config('nbnet', 'trans')
ff_l = trans_conf['ff_l'].split(';')
saver_l = trans_conf['saver_l'].split(';')
ff_sock_l = [None]
saver_sock_l = [None]

def sendsaver(saver_l, data, sock_l):
    return sendData_mh(saver_l, data, sock_l)

def sendff(ff_l, data, sock_l):
    return sendData_mh(ff_l, data, sock_l)

if __name__ == '__main__':
    addr = trans_conf['addr']
    port = int(trans_conf['port'])
    
    def logic(data):
        print data
        return("OK")
    
    sock = bind_socket(addr, port)
    transD = nbNet(sock, logic)
    transD.run()
