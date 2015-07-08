#coding=utf-8
'''Flask配置文件'''

class Config(object):
    WTF_CSRF_ENABLED = True
    SECRET_KEY = 'hard to guess string'

class DevelopmentConfig(Config):
    DEBUG = True

config = { 
    'default': DevelopmentConfig
}
