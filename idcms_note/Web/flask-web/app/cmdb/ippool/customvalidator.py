#coding=utf-8

import os
import sys
import re

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app.models import Sales, Client, Site, IpSubnet, IpPool, Cabinet
from app.utils.utils import re_ip

class CustomValidator():
    '''自定义检测
    如国检测正确返回 OK
    如国失败返回提示信息
    '''
    def __init__(self, item, item_id,value):
        self.item = item
        self.value = value
        self.change_ippool = IpPool.query.filter_by(id=int(item_id)).first()
        self.sm =  {
            "ip": self.validate_ip,
            "subnet": self.validate_subnet,
            "site": self.validate_site,
            "sales": self.validate_sales,
            "client": self.validate_client,
            "netmask": self.validate_ipvali,
            "gateway": self.validate_ipvali
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

    def validate_ip(self, value):
        if not re.match(re_ip, value):
            return u"更改失败，请输入一个正确的IP格式"
        if IpPool.query.filter_by(ip=value).first():
            return u"更改失败 这个IP已经添加"
        if Cabinet.query.filter_by(wan_ip=value).first():
            return u"更改失败 这个IP有设备在使用"
        return "OK"

    def validate_subnet(self, value):
        if not re.match(re_ip, value):
            return u"更改失败，请输入一个正确的IP格式"
        if not IpSubnet.query.filter_by(subnet=value).first():
            return u'更改失败，没有找到这个IP子网'
        return "OK"
    
    def validate_site(self, value):
        if not Site.query.filter_by(site=value).first():
            return u'更改失败，这个机房不存在'
        return "OK"

    def validate_sales(self,value):
        """只要符合这两个规定就可以成功"""
        if Cabinet.query.filter_by(wan_ip=self.change_ippool.ip).first():
            return u'更改失败，这个IP有设备在使用,只能通过更改设备来更改'
        if value:
            if not Sales.query.filter_by(username=value).first():
                return u'更改失败 这个销售不存在'
        return "OK"

    def validate_client(self,value):
        """只要符合这两个规定就可以成功"""
        if Cabinet.query.filter_by(wan_ip=self.change_ippool.ip).first():
            return u'更改失败 这个IP有设备在使用,只能通过更改设备来更改'
        if value:
            if not Client.query.filter_by(username=value).first():
                return u'更改失败 这个客户不存在'
        return "OK"

    def validate_ipvali(self, value):
        if re.match(re_ip, value):
            return "OK"
        return u"更改失败,IP格式不正确"
