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
    
    log_name = log_conf['logname']
    log_level = "d"
    
    work_path = os.path.dirname(os.path.realpath(__file__))
    log_path = "%s/%s" % (work_path, '../log')
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    log_file = "%s/%s.log" % (log_path, log_name)
    
    log_print = log_conf['print']
    log_max_byte = log_conf['maxbyte']
    log_backup_count = log_conf['count']
    log_formatter = '[ %(levelname)s ] %(asctime)s %(message)s'
    log_formatter_datefmt ='%Y-%m-%d %H:%M:%S'

    @staticmethod
    def getLogger():
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
    logger = Logger.getLogger()
    logger.debug("debug")
    logger.info("info")
    logger.warn("warn")
    logger.error("error")
    logger.critical("critical")
    msg ="print test"
    log_level = "debug"
    def dbglog(msg):
        getattr(logger, log_level)(msg)
    dbglog(msg)
