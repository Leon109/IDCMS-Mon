#coding=utf-8
from datetime import timedelta

'''Flask配置文件'''

class Config(object):
    # CSRF是否开启
    WTF_CSRF_ENABLED = True
    # 自动提交
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # flask-login 记住登录时间
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    # cookie 密钥
    SECRET_KEY = 'hard to guess string'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:""@127.0.0.1/nbnet"

config = { 
    'default': DevelopmentConfig
}
