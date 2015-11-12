#coding=utf-8
import os
import logging
import logging.handlers
from config import config

log_conf = config('nbnet', 'log')


class Logger(object):
    logger = None
    levels = {
        "n" : logging.NOTSET,
        "d" : logging.DEBUG,
        "i" : logging.INFO,
        "w" : logging.WARN,
        "e" : logging.ERROR,
        "c" : logging.CRITICAL
    } 
    
    # 日志对象名称和级别
    log_name = log_conf['logname']
    log_level = "d"
    
    # 日志保存的文件名和路径
    work_path = os.path.dirname(os.path.realpath(__file__))
    log_path = "%s/%s" % (work_path, '../log')
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    log_file = "%s/%s.log" % (log_path, log_name)
    
    # 默认只输出到文件中，True的会打印出出来
    log_print = log_conf['print']
    # 日志文件最大大小(100M)
    log_max_byte = log_conf['maxbyte']
    # 日志文件保存份数
    log_backup_count = log_conf['count']
    # 日志格式
    log_formatter = '[ %(levelname)s ] %(asctime)s %(message)s'
    log_formatter_datefmt ='%Y-%m-%d %H:%M:%S'

    @staticmethod
    def getLogger():
        # 判断log对象是否已经生成,如果模块中反复引用则直接返回该对象
        # 比如a模块使用了log对象，b模块导入a后也再次引用了则改对象，
        # 这样这个方法就会被使用两次
        if Logger.logger is not None:
            return Logger.logger
        Logger.logger = logging.Logger(Logger.log_name) 
       
        if Logger.log_print == "True":
            print_handler = logging.StreamHandler()
            print_fmt = logging.Formatter(
                    Logger.log_formatter, 
                    datefmt=Logger.log_formatter_datefmt
                    )   
            print_handler.setFormatter(print_fmt)   
            Logger.logger.addHandler(print_handler)
       
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
    logger = Logger.getLogger()
    # 方法1
    logger.debug("debug")
    logger.info("info")
    logger.warn("warn")
    logger.error("error")
    logger.critical("critical")
    # 方法2
    msg ="print test"
    log_level = "debug"
    def dbglog(msg):
        getattr(logger, log_level)(msg)
    dbglog(msg)
