#coding=utf-8

import os
import sys
import re
import time

from flask.ext.wtf import Form
from wtforms import StringField, SelectField
from wtforms import ValidationError
from wtforms.validators import Required, Length, Regexp

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app.models import Site, Rack, IpPool, Cabinet, Sales, Client
from app.utils.searchutils import re_date, re_ip


class CabinetForm(Form):
    an = StringField(u'资产编号', validators=[Required(message=u'资产编号不能为空'), 
                     Length(1, 64, message=u'资产编号为1-64个字符')])
    wan_ip = StringField(u'外网IP', validators=[Length(0, 64, message=u'机房名为0-64个字符')])
    lan_ip = StringField(u'内网IP', validators=[Length(0, 64, message=u'机房名为0-64个字符')])
    site = StringField(u'所在机房', validators=[Required(message=u'机房名不能为空'), 
                       Length(1, 64, message=u'机房名为1-64个字符')])
    rack = StringField(u'所在机架', validators=[Required(message=u'机架名不能为空'), 
                       Length(1, 32, message=u'机架名为1-32个字符')])
    seat = StringField(u'机架位置', validators=[Length(0, 32, message=u'机架位置最大为32个字符')])
    bandwidth = SelectField(u'设备带宽', choices=[(u'百共', u'百兆共享'), ('2M', '2M'),('5M', '5M'), 
                            ('10M', '10M' ),('20M', '20M'), ('50M', '50M'),('100M','100M'),
                            (u'上联设备', u'上联设备')])
    up_link = StringField(u'上联端口', validators=[Required(message=u'上联端口不能为空'),
                           Length(1, 32, message=u'上连为1-32个字符')])
    height = SelectField(u'设备高度', choices=[('1U', '1U'),('2U', '2U'), ('3U','3U' ), ('4U','4U')])
    brand = SelectField(u'设备品牌', choices=[(u'戴尔', u'戴尔'), (u'惠普', u'惠普'), ('IBM', 'IBM'), 
                        (u'浪潮', u'浪潮' ), (u'联想', u'联想'), (u'金品', u'金品'), (u'思科', u'思科'),
                        (u'华为', u'华为'), ('H3C', 'H3C'), (u'兼容机', u'兼容机')])
    model = StringField(u'设备型号', validators=[Length(0, 32, message=u'设备型号最大为32个字符')])
    sn = StringField(u'设备SN', validators=[Length(0, 32, message=u'设备SN最大为32个字符')])
    sales = StringField(u'销售代表', validators=[Required(message=u'销售代表不能为空'),
                            Length(1, 32, message=u'销售代表最大为32个字符')])
    client = StringField(u'使用用户', validators=[Required(message=u'使用用户不能为空'),
                         Length(1, 64, message=u'使用用户为最大为64个字符')])
    start_time = StringField(u'开通日期', validators=[Regexp(re_date, message=u'开通时间格式为yyyy-mm-dd')])
    expire_time = StringField(u'到期日期',validators=[Regexp(re_date, message=u'到期时间格式为yyyy-mm-dd')])
    remark = StringField(u'备注', validators=[Length(0, 64, message=u'备注最大64个字符')])

    def validate_an(self, field):
        if Cabinet.query.filter_by(an=field.data).first():
            raise ValidationError(u'添加失败 这个资产编号已经存在')

    def validate_wan_ip(self, field):
        if field.data:
            if not  re.match(re_ip, field.data):
                raise ValidationError(u'添加失败 外网IP应该是一个IP格式')
            if Cabinet.query.filter_by(wan_ip=field.data).first():
                raise ValidationError(u'添加失败 这个外网IP已经添加')
            ip = IpPool.query.filter_by(ip=field.data).first()
            if ip:
                if ip.client:
                    raise ValidationError(u'添加失败 这个外网IP已经使用')
            else:
                raise ValidationError(u'添加失败 这个外网IP还没有添加')
    
    def validate_lan_ip(self, field):
        if field.data:
            if not re.match(re_ip, field.data):
                raise ValidationError(u'添加失败 内网IP应该是一个IP格式')

    def validate_site(self, field):
        if not Site.query.filter_by(site=field.data).first():
            raise ValidationError(u'添加失败 这个机房不存在')

    def validate_rack(self, field):
        if not Rack.query.filter_by(rack=field.data, site=self.site.data).first():
            raise ValidationError(u'添加失败 这个机架不存在')

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
            raise ValidationError(u'添加失败 到期时间小于开通时间')
