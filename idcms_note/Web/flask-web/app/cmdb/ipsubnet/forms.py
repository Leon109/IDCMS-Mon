#coding=utf-8

import os
import sys
import time

from flask.ext.wtf import Form
from wtforms import StringField
from wtforms import ValidationError
from wtforms.validators import Required, Length, IPAddress, Regexp

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app.models import Site, IpSubnet, Sales, Client
from app.utils.searchutils import re_date

class IpSubnetForm(Form):
    subnet = StringField(u'IP子网', validators=[Required(message=u'IP子网不能为空'), 
                          IPAddress(message=u'IP子网应该是一个IP格式')])
    start_ip = StringField(u'起始IP', validators=[Required(message=u'起始IP不能为空'), 
                       IPAddress(message=u'起始IP应该是一个IP格式')])
    end_ip = StringField(u'结束IP', validators=[Required(message=u'结束IP不能为空'), 
                       IPAddress(message=u'结束IP应该是一个IP格式')])
    netmask = StringField(u'子网掩码', validators=[Required(message=u'子网掩码不能为空'), 
                          IPAddress(message=u'子网掩码应该是一个IP格式')])
    site = StringField(u'所属机房', validators=[Required(message=u'所属机房不能为空'), 
                       Length(1, 64, message=u'机房名为1-64个字符')])
    sales = StringField(u'销售代表', validators=[Required(message=u'销售代表不能为空'),
                         Length(1, 32, message=u'销售代表为1-32个字符')])
    client = StringField(u'使用用户', validators=[Required(message=u'使用用户不能为空'),
                         Length(1, 64, message=u'使用用户为1-64个字符')])
    start_time = StringField(u'开通日期', validators=[Regexp(re_date, message=u'开通时间格式为yyyy-mm-dd')])
    expire_time = StringField(u'到期日期',validators=[Regexp(re_date, message=u'到期时间格式为yyyy-mm-dd')]) 
    remark = StringField(u'备注', validators=[Length(0, 64, message=u'备注最大64个字符')])

    def validate_subnet(self,field):
        if IpSubnet.query.filter_by(subnet=field.data).first():
             raise ValidationError(u'添加失败，这个IP子网已经存在')

    def validate_site(self, field):
        if not Site.query.filter_by(site=field.data).first():
            raise ValidationError(u'添加失败，这个机房不存在')

    def validate_sales(self, field):
        if not Sales.query.filter_by(username=field.data).first():
            raise ValidationError(u'添加失败 这个销售不存在')

    def validate_client(self, field):
        if not Client.query.filter_by(username=field.data).first():
            raise ValidationError(u'添加失败 这个客户不存在')

    def validate_expire_time(self, field):
        start_time = time.mktime(time.strptime(self.start_time.data,'%Y-%m-%d'))
        expire_time = time.mktime(time.strptime(self.expire_time.data,'%Y-%m-%d'))
        if expire_time < start_time:
            raise ValidationError(u'添加失败，到期时间小于开通时间')
