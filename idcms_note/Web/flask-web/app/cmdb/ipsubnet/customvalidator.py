#coding=utf-8

import os
import sys
import re

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app.models import IpSubnet, Site, IpPool
from app.utils.searchutils import re_date, re_ip

class CustomValidator():
    '''自定义检测
    如国检测正确返回 OK
    如国失败返回提示信息
    '''
    def __init__(self, item, value):
        self.item = item
        self.value = value
        self.sm =  {
            "subnet":self.validate_subnet,
            "start_ip":self.validate_ip,
            "end_ip":self.validate_ip,
            "site":self.validate_site,
            "start_time":self.validate_time,
            "expire_time":self.validate_time
        }

    def validate_return(self):
        if self.sm.get(self.item, None):
            return self.sm[self.item](self.value)
        return "OK"

    def validate_sbunet(self, value):
        if not re.match(re_ip, value):
            return u"更改失败 请输入一个正确的IP格式"
        if IpRange.query.filter_by(subnet=value).first():
            return u'更改失败 这个IP子网网已经添加'
        if IpPool.query.filter_by(subnet=value).first():
            return  u'更改失败 这个子网有IP使用'
        return "OK"

    def validate_ip(self, value):
        if re.match(re_ip, value):
            return "OK"
        return u"更改失败 IP格式不正确"

    def validate_site(self, value):
        if not Site.query.filter_by(site=value).first():
            return u'更改失败 这个机房不存在'
        return "OK"

    def validate_time(self, value):
        if re.match(re_date, value):
            return "OK"
        return u"更改失败 时间格式不正确"
