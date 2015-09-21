#coding=utf-8

import re
import time

from app.models import IpSubnet, Site, IpPool, Sales, Client
from app.utils.utils import re_date, re_ip
from IPy import IP

class CustomValidator():
    def __init__(self, item, item_id, value):
        self.item = item
        self.value = value
        self.change_ipsubnet = IpSubnet.query.filter_by(id=int(item_id)).first()
        self.sm =  {
            "subnet": self.validate_subnet,
            "netmask": self.validate_netmask,
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
        return u"更改失败 不能直接更改IP子网"

    def validata_netmask(self, value):
        return u"更改失败 不能直接更改IP子网子网掩码"

    def validate_start_ip(self, value):
        if not re.match(re_ip, value):
            return u"更改失败 起始掩码应该是IP格式"
        if value not in IP(self.change_ipsubnet.subnet  + '/' + self.change_ipsubnet.netmask):
            return u'更改失败 起始IP *** %s *** 不属于该子网' % value 
        if not IP(value) <= IP(self.change_ipsubnet.end_ip):
            raise ValidationError(u'更改失败 起始IP应等于小于结束IP')

    def validate_end_ip(self, value):
        if not re.match(re_ip, value):
            return u"更改失败 起始掩码应该是IP格式"
        if value not in IP(self.change_ipsubnet.subnet  + '/' + self.change_ipsubnet.netmask):
            return u'更改失败 结束IP *** %s *** 不属于该子网' % value
        if not IP(value) >= IP(self.change_ipsubnet.start_ip):
            raise ValidationError(u'更改失败 结束IP应大于等于起始IP')

    def validate_start(self, value):
        if re.match(re_ip, value):
            return "OK"
        return u"更改失败 IP格式不正确"

    def validate_site(self, value):
        if not Site.query.filter_by(site=value).first():
            return u'更改失败 *** %s *** 机房不存在' % value
        return "OK"

    def validate_sales(self,value):
        if not Sales.query.filter_by(username=value).first():
            return u'更改失败 销售 *** %s *** 不存在' % value
        return "OK"

    def validate_client(self,value):
        if not Client.query.filter_by(username=value).first():
            return u'更改失败 客户 *** %s *** 不存在' % value
        return "OK"

    def validate_start_time(self, value):
        if re.match(re_date, value):
            start_time = time.mktime(time.strptime(value,'%Y-%m-%d'))
            expire_time = time.mktime(time.strptime(str(self.change_ipsubnet.expire_time),'%Y-%m-%d'))
            if start_time > expire_time:
                return u"更改失败 开通时间大于到期时间"
            return "OK"
        return u"更改失败 时间格式不正确"

    def validate_expire_time(self, value):
        if re.match(re_date, value):
            start_time = time.mktime(time.strptime(str(self.change_ipsubnet.start_time),'%Y-%m-%d'))
            expire_time = time.mktime(time.strptime(value,'%Y-%m-%d'))
            if expire_time < start_time:
                return u"更改失败 到期时间小于开通时间"
            return "OK"
        return u'更改失败 时间格式不正确'
