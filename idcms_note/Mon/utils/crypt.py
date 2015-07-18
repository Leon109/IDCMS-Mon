#!/usr/bin/env python
#coding=utf-8
'''
一个简单的对称加密
支持16位字符串特殊符号key给字符串加密
'''
from Crypto import Random
from Crypto.Cipher import AES 
import base64

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
unpad = lambda s : s[0:-ord(s[-1])]
# Key是一个加密密钥，加密和揭秘断同时使用这个密钥进行加密解密
KEY = ":::@#$sfe1111111"

def encrypt(raw):
    raw = pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    return base64.b64encode( iv + cipher.encrypt(raw) ) 

def decrypt(enc):
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(KEY, AES.MODE_CBC, iv )
    return unpad(cipher.decrypt(enc[16:]))

if __name__ == "__main__":
    data = "sdf"
    e =  encrypt(data)
    print decrypt(e)
