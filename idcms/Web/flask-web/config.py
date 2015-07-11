#coding=utf-8
from datetime import timedelta

'''Flask配置文件'''

class Config(object):
    WTF_CSRF_ENABLED = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    SECRET_KEY = 'hard to guess string'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:""@127.0.0.1/nbnet"

config = { 
    'default': DevelopmentConfig
}
