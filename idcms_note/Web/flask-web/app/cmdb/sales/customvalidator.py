#coding=utf-8

import os
import sys

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app.models import Sales, Rack, IpSubnet, Cabinet

class CustomValidator():
    '''自定义检测
    如国检测正确返回 OK
    如国失败返回提示信息
    '''
    def __init__(self, item, item_id, value):
        self.item = item
        self.change_sales = Sales.query.filter_by(id=int(item_id)).first()
        self.value = value
        self.sm =  {
            "username":self.validate_username,
        }

    def validate_return(self):
        if self.sm.get(self.item, None):
            return self.sm[self.item](self.value)
        else:
            if self.item in ("email", "remark") or self.value
                return "OK"
            return "这个项目不能为空"

    def validate_username(self, value):
        if Sales.query.filter_by(username=value).first():
            return u"更改失败 这个销售已经存在"
        if Rack.query.filter_by(sales=self.change_sales.username).first():
            return u"更改失败 这个销售有机架在使用"
        if IpSubnet.query.filter_by(sales=self.change_sales.username).first():
            return u"更改失败 这个销售有IP子网在使用"
        if Cabinet.query.filter_by(sales=self.change_sales.username).first():
            return u"更改失败 这个销售有设备在使用"
        else:
            return "OK"
