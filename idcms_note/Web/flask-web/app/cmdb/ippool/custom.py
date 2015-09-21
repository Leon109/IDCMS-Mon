#coding=utf-8

import re

from app.models import Sales, Client, Site, IpSubnet, IpPool, Cabinet
from app.utils.utils import re_ip

class CustomValidator():
    def __init__(self, item, item_id,value):
        self.item = item
        self.value = value
        self.change_ippool = IpPool.query.filter_by(id=int(item_id)).first()
        self.sm =  {
            "ip": self.validate_ip,
            "gateway": self.validate_gateway,
            "subnet": self.validate_subnet,
            "site": self.validate_site,
            "sales": self.validate_sales,
            "client": self.validate_client,
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
        return u"更改失败 不能直接更改IP"

    def validate_subnet(self, value):
        if not re.match(re_ip, value):
            return u"更改失败 请输入一个正确的IP格式"
        subnet = IpSubnet.query.filter_by(subnet=value).first()
        subnet_check = IP(subnet.subnet + '/' + subnet.netmask)
        if not subnet:
            return u'更改失败 没有找到 *** %s ***IP子网' % value
        if self.change_ippool.ip not in subnet_check:
            return u"更改失败 IP *** %s *** 不属于在这个子网" % self.change_ippool.ip
        return "OK"
 
    def validate_site(self, value):
        if not Site.query.filter_by(site=value).first():
            return u'更改失败，*** %s *** 机房不存在' % value
        return "OK"

    def validate_sales(self,value):
        """只要符合这两个规定就可以成功"""
        if Cabinet.query.filter_by(wan_ip=self.change_ippool.ip).first():
            return u'更改失败，IP *** %s **** 有设备在使用 只能通过更改设备来更改' \
                   % self.change_ippool.ip
        if value:
            if not Sales.query.filter_by(username=value).first():
                return u'更改失败 销售 *** %s *** 不存在' % value
        return "OK"

    def validate_client(self,value):
        """只要符合这两个规定就可以成功"""
        if Cabinet.query.filter_by(wan_ip=self.change_ippool.ip).first():
            return u'更改失败 IP *** %s **** 有设备在使用 只能通过更改设备来更改' \
                   % self.change_ippool.ip
        if value:
            if not Client.query.filter_by(username=value).first():
                return u'更改失败 客户 *** %s *** 不存在' % value
        return "OK"

    def validate_gateway(self, value):
        if not re.match(re_ip, value):
            return u"更改失败,IP格式不正确"
        subnet = IpSubnet.query.filter_by(self.change_ippool.subnet).first()
        subnet_check = IP(subnet.subnet + '/' + subnet.netmask)
        if value not in subnet_check:
            return u"更改失败 网关地址不属于这个子网"
        return "OK"
