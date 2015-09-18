#coding=utf-8

from flask import Blueprint
task = Blueprint('task', __name__)

from . import views
from ..utils.permission import Permission

# 通过这个上下文处理装饰器把这个方法注入下，在模版中就可以直接使用了
@task.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
