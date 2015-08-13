#coding=utf-8

import os
import sys
import re
import time

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app.models import Rack, Site, IpPool, Cabinet
from app.utils.searchutils import re_date, re_ip


class CustomValidator():
    '''自定义检测
    如国检测正确返回 OK
    如国失败返回提示信息
    '''
    def __init__(self, item, item_id, value):
        self.item = item
        self.value = value
        self.change_cabinet = Cabinet.query.filter_by(id=int(item_id)).first()
        self.sm =  {
            "rack":self.validate_an,
            "wan_ip":self.validate_wan_ip,
            "lan_ip":self.validate_lan_ip,
            "site":self.validate_site,
            "rack":self.validate_rack,
            "bandwidth":self.validate_bandwidth,
            "height":self.validate_height,
            "start_time":self.validate_start_time,
            "expire_time":self.validate_expire_time
        }

    def validate_return(self):
        if self.sm.get(self.item, None):
            return self.sm[self.item](self.value)
        return "OK"

    def validate_an(self,value):
        if Cabinet.query.filter_by(an=value).first():
            return u'更改失败这个外网资产编号已经使用'

    def validate_wan_ip(self,value):
        if not re.match(re_ip, value):
            return u'添加失败，外网IP应该是一个IP格式'
        if Cabinet.query.filter_by(wan_ip=value).first():
            return u'更改失败呢，这个外网IP已经使用'
        ip = IpPool.query.filter_by(ip=value).first()
        if ip: 
            if not ip.client:
                return "OK"
            return u'添加失败 这个IP已经使用'
        else:
            return u'添加失败 这个IP还没有添加'
 
    def validate_lan_ip(self,value):
        if not re.match(re_ip, value):
            return  u'添加失败 内网IP应该是一个IP格式'
        return "OK"

    def validate_site(self,value):
        return u"不能更改机房 更护机房要先执行下架"

    def validate_rack(self,value):
        if not Rack.query.filter_by(rack=value ,site=self.change_cabinet.site).first():
            return u'更改失败 没有在该机房找到这个机柜'
        return "OK"

    def validate_bandwidth(self,value):
        re_count = '^\d+M$'
        if re.match(re_count, value):
            return "OK"
        return u"更改失败 格式为 数字+M"
    
    def validate_height(self,value):
        re_power = '^\d\dU$'
        if re.match(re_power, value):
            return "OK"
        return u"更改失败 格式为 数字+U"
    
    def validate_start_time(self, value):
        if re.match(re_date, value):
            start_time = time.mktime(time.strptime(value,'%Y-%m-%d'))
            expire_time = time.mktime(time.strptime(self.change_cabinet.expire_time,'%Y-%m-%d'))
            if start_time > expire_time:
                return u"添加失败，开通时间小于到期时间"
            return "OK"
        return u"更改失败，时间格式不正确"

    def validate_expire_time(self, value):
        if re.match(re_date, value):
            start_time = time.mktime(time.strptime(self.change_cabinet.start_time,'%Y-%m-%d'))
            expire_time = time.mktime(time.strptime(value,'%Y-%m-%d'))
            if expire_time < start_time:
                return u"添加失败，到期时间小于开通时间"
            return "OK"
        return u'更改失败，时间格式不正确'

