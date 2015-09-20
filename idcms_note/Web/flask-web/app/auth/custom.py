#coding=utf-8

from app.models import User
from app.utils.permission import Permission

class CustomValidator():
    def __init__(self, item, value):
        self.item = item
        self.value = value
        self.sm =  {
            "username":self.validate_username,
            "alias": self.validate_alias,
            "role":self.validate_role
        }

    def validate_return(self):
        if self.sm.get(self.item, None):
            return self.sm[self.item](self.value)
        else:
            if len(self.value) > 12: 
                return u"更改失败 不能超过12个字符"
            if self.value:
                return "OK"
            return u"更改失败 这个项目不能为空"

    def validate_username(self, value):
        if len(self.value) > 12: 
            return u"更改失败 最大字符为12个字符"
        if not value:
            return u"更改失败 这个项目不能为空"
        if User.query.filter_by(username=value).first():
            return u'更改失败 用户 *** %s *** 已存在' % value
        else:
            return "OK"

    def validate_alias(self, value):
        if len(self.value) > 12: 
            return u"更改失败 最大字符为12个字符"
        if not value:
            return u"更改失败 这个项目不能为空"
        if User.query.filter_by(alias=value).first():
            return u'更改失败 别名 *** %s *** 已存在' % value
        else:
            return "OK"

    def validate_role(self, value):
        role_range = dir(Permission)
        del role_range[-2:]
        if value in role_range:
            return "OK"
        else:
            return u"更改失败 权限名称错误"
