#coding=utf-8

from flask import Blueprint
auth = Blueprint('auth', __name__)

from . import views, errors
from ..utils.permission import Permission

# 通过这个上下文处理装饰器把这个方法注入下，在模版中就可以直接使用了
@auth.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

@auth.app_context_processor
def injcet_work():
    titles = {'path':'/auth/setting', 'title':u'IDCMS-设置'}
    del_page = '/auth/setting/delete'
    change_page= '/auth/setting/change'
    return dict(titles=titles, del_page=del_page, change_page=change_page)
