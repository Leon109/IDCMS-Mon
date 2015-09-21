#coding=utf-8

from flask.ext.wtf import Form
from wtforms import StringField, ValidationError
from wtforms.validators import Required, Length, IPAddress, Regexp
from IPy import IP

from app.models import Sales, Site, IpSubnet, IpPool, Client

re_ip_one = '^(25[0-5]|2[0-4]\d|[01]?\d\d?)$'

class IpPoolForm(Form):
    subnet = StringField(u'IP子网', validators=[Required(message=u'IP子网不能为空'),
                         IPAddress(message=u'ip子网应该是一个IP格式')])
    start_ip = StringField(u'起始IP', validators=[Required(message=u'起始IP不能为空'), 
                       IPAddress(message=u'起始IP应该是一个IP格式')])
    end_ip = StringField(u'结束IP', validators=[Regexp(re_ip_one, message=u'结束IP应为0-255')])
    gateway = StringField(u'网关地址', validators=[Required(message=u'网关地址不能为空'),
                          IPAddress(message=u'网关地址应该是一个IP格式')])
    site = StringField(u'所属机房', validators=[Required(message=u'所属机房不能为空'), 
                       Length(1, 64, message=u'机房名为1-64个字符')])
    sales = StringField(u'销售代表', validators=[Length(0, 32, message=u'销售代表为1-32个字符')])
    client = StringField(u'使用用户', validators=[Length(0, 64, message=u'使用用户最大为64个字符')])
    remark = StringField(u'备注', validators=[Length(0, 64, message=u'备注最大64个字符')])
   
    def validate_end_ip(self, field):
        subnet = IpSubnet.query.filter_by(subnet=field.data).first()
        end_ip = self.start_ip[:-3] + field.data
        subnet_check = IP(subnet.subnet + '/' + subnet.netmask)

        if not subnet:
            raise ValidationError(u'添加失败 子网 *** %s *** 不存在' % subnet.subnet)
        if self.start_ip.data not in subnet_check:
            raise ValidationError(u'添加失败 起始IP *** %s *** 不属于该子网' % field.data)
        if end_ip not in subnet_check:
            raise ValidationError(u'添加失败 结束IP *** %s *** 不属于该子网' % end_ip)
        if not int(self.start_ip[-3:]) <= int(field.data):
            raise ValidationError(u'添加失败 结束IP应大于等于起始IP')
        if self.gateway.data not in subnet_check:
            raise ValidationError(u'添加失败 网关地址 *** %s *** 不属于该子网' % self.gateway.data)

    def validate_site(self, field):
        if not Site.query.filter_by(site=field.data).first():
            raise ValidationError(u'添加失败 机房 *** %s *** 不存在' % field.data)

    def validate_sales(self, field):
        if field.data:
            if not Sales.query.filter_by(username=field.data).first():
                raise ValidationError(u'添加失败 销售 *** %s *** 不存在' % field.data)

    def validate_client(self, field):
        if field.data:
            if not Client.query.filter_by(username=field.data).first():
                raise ValidationError(u'添加失败 客户 *** %s *** 不存在' % field.data)
