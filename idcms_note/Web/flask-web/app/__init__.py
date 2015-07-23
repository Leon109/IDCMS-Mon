#coding=utf-8

from flask import Flask
from config import config
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
# 设为'strong' 时，Flask-Login 会记录客户端IP
# 地址和浏览器的用户代理信息，如果发现异动就登出用户
login_manager.session_protection = 'strong'
# 登陆页
login_manager.login_view = 'auth.login'
# 访问页面登录提示
login_manager.login_message = None #u'请先登录'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    login_manager.init_app(app)

    from .auth import auth
    app.register_blueprint(auth, url_prefix='/auth')
    from .cmdb import cmdb
    app.register_blueprint(cmdb)
    
    return app
