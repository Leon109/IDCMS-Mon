#coding=utf-8

from ..models import User
from ..utils.permission import Permission

class CustomValidator():
    '''自定义检测
    如国检测正确返回 OK
    如国失败返回提示信息
    '''
    def __init__(self, item, value):
        self.item = item
        self.value = value
        self.sm =  {
            "username":self.validate_username,
            "role":self.validate_role
        }

    def validate_return(self):
        if self.sm.get(self.item, None):
            return self.sm[self.item](self.value)
        return "OK"

    def validate_username(self, value):
        if User.query.filter_by(username=value).first():
            return u'用户名已经存在'
        else:
            return "OK"

    def validate_role(self, value):
        role_range = dir(Permission)
        del role_range[-2:]
        if value in role_range:
            return "OK"
        else:
            return u"权限名称错误"

