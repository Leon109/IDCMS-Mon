#coding=utf-8

from inspect import currentframe, stack

def run_linenumber():
    '''使用currentframe模块获取函数运行在一行
    stack获取执行文件名'''
    cf = currentframe()
    caller_file = stack()[1][1]
    filename = caller_file
    return "%s line %s " % (caller_file, cf.f_back.f_lineno)
