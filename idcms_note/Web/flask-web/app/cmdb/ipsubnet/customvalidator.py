#coding=utf-8

import os
import sys
import re
import time

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app.models import IpSubnet, Site, IpPool, Sales, Client
from app.utils.utils import re_date, re_ip

class CustomValidator():
    '''自定义检测
    如果检测正确返回 OK
    如果失败返回提示信息
    '''
    def __init__(self, item, item_id, value):
        self.item = item
        self.value = value
        self.change_ipsubnet = IpSubnet.query.filter_by(id=int(item_id)).first()
        self.sm =  {
            "subnet": self.validate_subnet,
            "start_ip": self.validate_ip,
            "end_ip": self.validate_ip,
            "site": self.validate_site,
            "sales": self.validate_sales,
            "client": self.validate_client,
            "start_time": self.validate_start_time,
            "expire_time": self.validate_expire_time
        }

    def validate_return(self):
        if self.sm.get(self.item, None):
            return self.sm[self.item](self.value)
        else:
            if len(self.value) > 64: 
                return u"更改失败 最大64个字符"
            if self.item in ("remark") or self.value:
                return "OK"
            return u"这个项目不能为空"

    def validate_subnet(self, value):
        if not re.match(re_ip, value):
            return u"更改失败 请输入一个正确的IP格式"
        if IpSubnet.query.filter_by(subnet=value).first():
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

    def validate_sales(self,value):
        if not Sales.query.filter_by(username=value).first():
            return u'更改失败 这个销售不存在'
        return "OK"

    def validate_client(self,value):
        if not Client.query.filter_by(username=value).first():
            return u'更改失败 这个客户不存在'
        return "OK"

    def validate_start_time(self, value):
        if re.match(re_date, value):
            start_time = time.mktime(time.strptime(value,'%Y-%m-%d'))
            expire_time = time.mktime(time.strptime(str(self.change_ipsubnet.expire_time),'%Y-%m-%d'))
            if start_time > expire_time:
                return u"添加失败，开通时间大于到期时间"
            return "OK"
        return u"更改失败，时间格式不正确"

    def validate_expire_time(self, value):
        if re.match(re_date, value):
            start_time = time.mktime(time.strptime(str(self.change_ipsubnet.start_time),'%Y-%m-%d'))
            expire_time = time.mktime(time.strptime(value,'%Y-%m-%d'))
            if expire_time < start_time:
                return u"添加失败，到期时间小于开通时间"
            return "OK"
        return u'更改失败，时间格式不正确'
