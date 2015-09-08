#coding=utf-8

import functools
from flask import abort
from ..models import User
from flask.ext.login import current_user

class Permission:
    '''定义用户权限
    0 作为保留
    '''
    # 查询权限
    QUERY = 29
    # 高级查询
    ADVANCED_QUERY = 39
    # 修改权限
    ALTER = 69
    # 管理员权限
    ADMIN = 99

def permission_validation(level, level1=99):
    '''权限验证装饰器
       level 是级别，int类型小于这个级别的将抛出403错误
       要求：
       这个装饰器一定要flask-login 的验证用户登录后在添加
       举例
       @permission_validation(Permission.ADMIN)
       # 这个加载试图函数中，用户权限就会返回403
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取到用户数据库 id 并查询用户
            u_id = current_user.id
            user = User.query.filter_by(id=u_id).first()
            role_id = getattr(Permission, user.role)
            # 通过用户对应数字判断用户权限
            if role_id >= level or role_id == level1 :
                return func(*args, **kwargs)
            abort(403)
        return wrapper
    return decorator
