#coding=utf-8

import os
import sys

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app.models import  Site

class CustomValidator():
    '''自定义检测
    如国检测正确返回 OK
    如国失败返回提示信息
    '''
    def __init__(self, item, value):
        self.item = item
        self.value = value
        self.sm =  {
            "site":self.validate_site,
        }

    def validate_return(self):
        if self.sm.get(self.item, None):
            return self.sm[self.item](self.value)
        else:
            return "OK"

    def validate_site(self, value):
        if Site.query.filter_by(site=value).first():
            return u'机房已经存在,修改失败'
        else:
            return "OK"
