#coding=utf-8

import os
import logging
import logging.handlers

from monconf import config

log_conf = config('mon.conf', 'log')

class Logger(object):
    '''log日志模块初始化封装'''
    # 日志级别
    levels = {
        "n" : logging.NOTSET,
        "d" : logging.DEBUG,
        "i" : logging.INFO,
        "w" : logging.WARN,
        "e" : logging.ERROR,
        "c" : logging.CRITICAL
    } 
    
    # 日志名称
    log_name = "mon.log"
    # 指定最低日志级别，低于该级别将被忽略
    log_level = "d"

    # 日志保存的文件名和路径默认保存在上层文件的log文件夹内
    work_path = os.path.dirname(os.path.realpath(__file__))
    log_path = "%s/%s" % (work_path, '../log')
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    log_file = "%s/%s" % (log_path, log_name)
    
    # 日志文件子节大小
    log_max_byte = log_conf['maxbyte']
    # 日志文件保存份数
    log_backup_count = log_conf['count']
    # 日志格式
    log_formatter = '[ %(levelname)s ] %(asctime)s %(message)s'
    log_formatter_datefmt ='%Y-%m-%d %H:%M:%S'

    @staticmethod
    def getLogger(debug=False):
        '''日志使用的静态方法
        两种模式
        如果debug关闭，日志之纪录到日志文件中去
        如果debug开启，在记录到文件中的同时会打印到终端上
        '''
        Logger.logger = logging.Logger(Logger.log_name) 
        
        if debug:
            debug_handler = logging.StreamHandler()
            debug_fmt = logging.Formatter(
                    Logger.log_formatter, 
                    datefmt=Logger.log_formatter_datefmt
                    )   
            debug_handler.setFormatter(debug_fmt)   
            Logger.logger.addHandler(debug_handler)
       
        file_handler = logging.handlers.RotatingFileHandler(
                filename = Logger.log_file,
                maxBytes = Logger.log_max_byte,
                backupCount = Logger.log_backup_count
                )
        file_fmt = logging.Formatter(
                Logger.log_formatter, 
                datefmt=Logger.log_formatter_datefmt
                )
        file_handler.setFormatter(file_fmt)
        Logger.logger.addHandler(file_handler)
        
        Logger.logger.setLevel(Logger.levels.get(Logger.log_level))
        return Logger.logger

if __name__ == "__main__":
    # 使用方法
    # 直接使用日志模块
    logger = Logger.getLogger()
    logger.debug("debug")
    logger.info("info")
    logger.warn("warn")
    logger.error("error")
    logger.critical("critical")
    logs.debug("haha  bong")
