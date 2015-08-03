#coding=utf-8

from flask import Blueprint
auth = Blueprint('auth', __name__)

from . import views
from ..utils.permission import Permission

# 通过这个上下文处理装饰器把这个方法注入下，在模版中就可以直接使用了
@auth.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

@auth.app_context_processor
def injcet_work():
    titles = {'path':'/auth/setting', 'title':u'IDCMS-设置'}
    # 列表显示 第一个是列，第二个是显示名称，第三个是对象的input name
    thead = [[0, u'用户名','username'], [1,u'密码', 'password'], [2,u'权限', 'role']]
    return dict(titles=titles, thead=thead)
