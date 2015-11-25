#!/usr/bin/python

import os
import sys
import time

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../")

from utils.utils import send_data

sock_list = [None]
trans_list = ['localhost:9100']

while True:
    send_data(trans_list, "gogogo", sock_list)
    time.sleep(5)
