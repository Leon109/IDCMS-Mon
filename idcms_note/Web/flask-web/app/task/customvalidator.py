#coding=utf-8

from ..models import User
from ..utils.permission import Permission

class CustomValidator():
    '''自定义检测
    如果检测正确返回 OK
    如果失败返回提示信息
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
        else:
            if len(self.value) > 64: 
                return u"更改失败 不能超过64个字符"
            if self.value:
                return "OK"
            return u"更改失败 这个项目不能为空"

    def validate_username(self, value):
        if len(self.value) > 64: 
            return u"更改失败 最大字符为64个字符"
        if not value:
            return u"更改失败 这个项目不能为空"
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
