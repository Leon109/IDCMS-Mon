#coding=utf-8

import os
import sys
import re

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app.models import Rack,Site
from app.utils.searchutils import re_date


class CustomValidator():
    '''自定义检测
    如国检测正确返回 OK
    如国失败返回提示信息
    '''
    def __init__(self, item, item_id, value):
        self.item = item
        self.change_rack = Rack.query.filter_by(id=int(item_id)).first()
        self.value = value
        self.sm =  {
            "rack":self.validate_rack,
            "site":self.validate_site,
            "count":self.validate_count,
            "power":self.validate_power,
            "start_time":self.validate_time,
            "expire_time":self.validate_time
        }

    def validate_return(self):
        if self.sm.get(self.item, None):
            return self.sm[self.item](self.value)
        return "OK"

    def validate_rack(self,value):
        if Rack.query.filter_by(rack=value, site=self.change_rack.site).first():
            return u'更改失败，这个机房已经有该机柜'
        if Cabinet.query.filter_by(rack=value, site=self.change_rack.site).first():
            return u'更改失败，这个机柜已经有设备使用'
        return "OK"

    def validate_site(self,value):
        if not Site.query.filter_by(site=value).first():
            return u'更改失败，这个机房不存在'
        if Rack.query.filter_by(site=value,rack=self.change_rack.rack).first():
            return u'更改失败，这个机房已经添加该机柜'
        if Cabinet.query.filter_by(site=value, rack=self.change_rack.rack).first():
            return u'更改失败，这个机柜已经有设备使用'
        return "OK"
    
    def validate_count(self,value):
        re_count = '^\d\dU$'
        if re.match(re_count, value):
            return "OK"
        return u"更改失败, 格式为 数字+U"
    
    def validate_power(self,value):
        re_power = '^\d\dA$'
        if re.match(re_power, value):
            return "OK"
        return u"更改失败, 格式为 数字+A"
    
    def validate_time(self, value):
        if re.match(re_date, value):
            return "OK"
        return u"更改失败，时间格式不正确"
