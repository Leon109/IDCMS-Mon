#coding=utf-8

from flask import Flask
from config import config
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = u'请先登录'

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
