#coding=utf-8

import os
import sys

from flask.ext.wtf import Form
from wtforms import StringField
from wtforms import ValidationError
from wtforms.validators import Required, Length, IPAddress, Regexp

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app.models import Sales, Site, IpSubnet, IpPool, Client

re_ip_one = '^(25[0-5]|2[0-4]\d|[01]?\d\d?)$'

class IpPoolForm(Form):
    start_ip = StringField(u'起始IP', validators=[Required(message=u'起始IP不能为空'), 
                       IPAddress(message=u'起始IP应该是一个IP格式')])
    end_ip = StringField(u'结束IP', validators=[Regexp(re_ip_one, message=u'结束IP应为0-255')])
    netmask = StringField(u'子网掩码', validators=[Required(message=u'子网掩码不能为空'), 
                          IPAddress(message=u'子网掩码应该是一个IP格式')])
    gateway = StringField(u'网关地址', validators=[Required(message=u'网关地址不能为空'),
                          IPAddress(message=u'网关地址应该是一个IP格式')])
    subnet = StringField(u'IP子网', validators=[Required(message=u'IP子网不能为空'),
                         IPAddress(message=u'ip子网应该是一个IP格式')])
    site = StringField(u'所属机房', validators=[Required(message=u'所属机房不能为空'), 
                       Length(1, 64, message=u'机房名为1-64个字符')])
    sales = StringField(u'销售代表', validators=[Length(0, 32, message=u'销售代表为1-32个字符')])
    client = StringField(u'使用用户', validators=[Length(0, 64, message=u'使用用户最大为64个字符')])
    remark = StringField(u'备注', validators=[Length(0, 64, message=u'备注最大64个字符')])
   
    def validate_end_ip(self, field):
        start_ip = self.start_ip.data
        if int(start_ip.split('.')[-1]) > int(field.data):
            raise ValidationError(u'添加失败 结束IP应该大于起始IP')

    def validate_subnet(self, field):
        if not IpSubnet.query.filter_by(subnet=field.data).first():
            raise ValidationError(u'添加失败 这个子网不存在')

    def validate_site(self, field):
        if not Site.query.filter_by(site=field.data).first():
            raise ValidationError(u'添加失败 这个机房不存在')

    def validate_sales(self, field):
        if field.data:
            if not Sales.query.filter_by(username=field.data).first():
                raise ValidationError(u'添加失败 这个销售不存在')

    def validate_client(self, field):
        if field.data:
            if not Client.query.filter_by(username=field.data).first():
                raise ValidationError(u'添加失败 这个客户不存在')
