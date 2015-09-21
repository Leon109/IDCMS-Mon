#coding=utf-8

import re
import time

from app.models import Rack, Site, Sales, Client, Cabinet
from app.utils.utils import re_date


class CustomValidator():
    def __init__(self, item, item_id, value):
        self.item = item
        self.change_rack = Rack.query.filter_by(id=int(item_id)).first()
        self.value = value
        self.sm =  {
            "rack": self.validate_rack,
            "site": self.validate_site,
            "count": self.validate_count,
            "power": self.validate_power,
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

    def validate_rack(self,value):
        if Rack.query.filter_by(rack=value, site=self.change_rack.site).first():
            return u'更改失败 *** %s *** 机房已经有 *** %s *** 机柜' % (self.change_rack.site, value)
        if Cabinet.query.filter_by(rack=value, site=self.change_rack.site).first():
            return u'更改失败 *** %s *** 机柜有设备在使用' % value 
        return "OK"

    def validate_site(self,value):
        if not Site.query.filter_by(site=value).first():
            return u'更改失败 *** %s *** 机房不存在' % value
        if Rack.query.filter_by(site=value,rack=self.change_rack.rack).first():
            return u'更改失败 *** %s *** 机房已经有 *** %s *** 机柜' % (value, self.change_rack.rack)
        if Cabinet.query.filter_by(site=value, rack=self.change_rack.rack).first():
            return u'更改失败 *** %s *** 机柜有设备在使用' % self.change_rack.rack
        return "OK"
    
    def validate_count(self,value):
        re_count = '^\d\dU$'
        if re.match(re_count, value):
            return "OK"
        return u"更改失败 格式为 数字+U"
    
    def validate_power(self,value):
        re_power = '^\d\dA$'
        if re.match(re_power, value):
            return "OK"
        return u"更改失败 格式为 数字+A"

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
            expire_time = time.mktime(time.strptime(str(self.change_rack.expire_time),'%Y-%m-%d'))
            if start_time > expire_time:
                return u"更改失败 开通时间大于到期时间"
            return "OK"
        return u"更改失败 时间格式不正确"

    def validate_expire_time(self, value):
        if re.match(re_date, value):
            start_time = time.mktime(time.strptime(str(self.change_rack.start_time),'%Y-%m-%d'))
            expire_time = time.mktime(time.strptime(value,'%Y-%m-%d'))
            if expire_time < start_time:
                return u"更改失败 到期时间小于开通时间"
            return "OK"
        return u'更改失败 时间格式不正确'
