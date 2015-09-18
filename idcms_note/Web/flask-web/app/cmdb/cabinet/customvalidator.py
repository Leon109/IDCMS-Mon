#coding=utf-8

import re
import time

from flask.ext.login import current_user

from app import db
from app.models import Rack, Site, IpPool, Cabinet, Sales, Client
from app.utils.utils import re_date, re_ip, record_sql

class CustomValidator():
    '''自定义检测
    如果检测正确返回 OK
    如果失败返回提示信息
    '''
    def __init__(self, item, item_id, value):
        self.item = item
        self.value = value
        self.change_cabinet = Cabinet.query.filter_by(id=int(item_id)).first()
        self.sm =  {
            "rack": self.validate_an,
            "wan_ip": self.validate_wan_ip,
            "lan_ip": self.validate_lan_ip,
            "site": self.validate_site,
            "rack": self.validate_rack,
            "bandwidth": self.validate_bandwidth,
            "height": self.validate_height,
            "sales": self.validate_sales,
            "client": self.validate_client,
            "start_time": self.validate_start_time,
            "expire_time": self.validate_expire_time
        }

    def validate_return(self):
        if self.sm.get(self.item, None):
            return self.sm[self.item](self.value)
        else:
            if self.item in ("model", "sn") and len(self.value) > 32: 
                return u"更改失败 最大32个字符"
            if len(self.value) > 64:
                return u"更改事变最大 64个字符"
            if self.item in ("remark") or self.value:
                return "OK"
            return u"这个项目不能为空"

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
            if ip.sales or ip.client:
                return u'添加失败 这个外网IP已经使用'
            return "OK"
        else:
            return u'添加失败 这个外网IP还没有添加'
 
    def validate_lan_ip(self,value):
        if not re.match(re_ip, value):
            return  u'添加失败 内网IP应该是一个IP格式'
        return "OK"

    def validate_site(self,value):
        return u"不能更改机房更改机房要先执行下架(删除) 然后从新添加"

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
        re_power = '^\d+U$'
        if re.match(re_power, value):
            return "OK"
        return u"更改失败 格式为 数字+U"

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
            expire_time = time.mktime(time.strptime(str(self.change_cabinet.expire_time),'%Y-%m-%d'))
            if start_time > expire_time:
                return u"添加失败，开通时间小于到期时间"
            return "OK"
        return u"更改失败，时间格式不正确"

    def validate_expire_time(self, value):
        if re.match(re_date, value):
            start_time = time.mktime(time.strptime(str(self.change_cabinet.start_time),'%Y-%m-%d'))
            expire_time = time.mktime(time.strptime(value,'%Y-%m-%d'))
            if expire_time < start_time:
                return u"添加失败，到期时间小于开通时间"
            return "OK"
        return u'更改失败，时间格式不正确'


class ChangeCheck():
    """根据不同的字段进行修改
    主要是检查了ip是不是更改，如果更改了同事更改ip信息
    """
    def __init__(self,item, value, cabinet):
        self.item = item
        self.value = value
        self.cabinet = cabinet
        self.sm = {
            "sales": self.sales_and_clinet,
            "client": self.sales_and_clinet,
            "wan_ip": self.wan_ip,
        }
    
    def change_run(self):
        if self.sm.get(self.item, None):
            self.sm[self.item]()
            record_sql(current_user.username, u"更改", u"机柜表",
                    self.cabinet.id, self.item, self.value)
            setattr(self.cabinet, self.item, self.value)
            db.session.add(self.cabinet)
        else:
            record_sql(current_user.username, u"更改", u"机柜表",
                    self.cabinet.id, self.item, self.value)
            setattr(self.cabinet, self.item, self.value)
            db.session.add(self.cabinet)

    def sales_and_clinet(self):
        if self.cabinet.wan_ip:
            ip = IpPool.query.filter_by(ip=self.cabinet.wan_ip).first()
            record_sql(current_user.username, u"更改", u"IP池", ip.id,
                    self.item, self.value)
            setattr(ip, self.item, self.value)
            db.session.add(ip)

    def wan_ip(self):
        if self.cabinet.wan_ip:
            old_ip = IpPool.query.filter_by(ip=self.cabinet.wan_ip).first()
            record_sql(current_user.username, u"更改", u"IP池", old_ip.id,
                       'sales', '')
            record_sql(current_user.username, u"更改", u"IP池", old_ip.id,
                       'client', '')
            old_ip.sales = ''
            old_ip.client = ''
            db.session.add(old_ip)
        add_ip = IpPool.query.filter_by(ip=self.value).first()
        record_sql(current_user.username, u"更改", u"IP池", add_ip.id,
                   'sales', self.cabinet.sales)
        record_sql(current_user.username, u"更改", u"IP池", add_ip.id,
                   'client', self.cabinet.client)
        add_ip.sales = self.cabinet.sales
        add_ip.client = self.cabinet.client
        db.session.add(add_ip)
