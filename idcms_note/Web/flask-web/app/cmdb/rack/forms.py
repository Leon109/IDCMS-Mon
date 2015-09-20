#coding=utf-8

import time

from flask.ext.wtf import Form
from wtforms import StringField, SelectField, ValidationError
from wtforms.validators import Required, Length, Regexp

from app.models import Site, Rack, Sales, Client
from app.utils.utils import re_date


class RackForm(Form):
    rack = StringField(u'机架名称', validators=[Required(message=u'机架名不能为空'), 
                       Length(1, 32, message=u'机架名最大32个字符')])
    site = StringField(u'机房名称', validators=[Required(message=u'机房名不能为空'), 
                       Length(1, 64, message=u'机房名最大64个字符')])
    count = SelectField(u'机架U数', choices=[('42U', '42U'),('48U', '48U'), ('60U', '60U' )])
    power = SelectField(u'机架电流', choices=[('10A', '10A'),('14A', '14A'), ('15A','15A' ),
                        ('20A','20A')])
    sales =  StringField(u'销售代表', validators=[Required(message=u'销售代表不能为空'),
                         Length(1, 32, message=u'销售代表最大32个字符')])
    client = StringField(u'使用用户', validators=[Required(message=u'使用用户不能为空'),
                         Length(1, 64, message=u'使用用户最大64个字符')])
    start_time = StringField(u'开通日期', validators=[Regexp(re_date, message=u'开通时间格式为yyyy-mm-dd')])
    expire_time = StringField(u'到期日期',validators=[Regexp(re_date, message=u'到期时间格式为yyyy-mm-dd')])
    remark = StringField(u'备注', validators=[Length(0, 64, message=u'备注最大64个字符')])
    
    def validate_rack(self, field):
        if Rack.query.filter_by(rack=field.data, site=self.site.data).first():
            raise ValidationError(u'添加失败 *** %s *** 机房已经有 *** %s *** 机柜'
                                  % (self.site.data, field.data))

    def validate_site(self, field):
        if not Site.query.filter_by(site=field.data).first():
            raise ValidationError(u'添加失败 ***%s*** 机房不存在' % field.data)

    def validate_sales(self, field):
        if not Sales.query.filter_by(username=field.data).first():
            raise ValidationError(u'添加失败 销售 *** %s *** 不存在' % field.data)

    def validate_client(self, field):
        if not Client.query.filter_by(username=field.data).first():
            raise ValidationError(u'添加失败 这个客户 *** %s *** 不存在' % field.data)

    def validate_expire_time(self, field):
        start_time = time.mktime(time.strptime(self.start_time.data,'%Y-%m-%d'))
        expire_time = time.mktime(time.strptime(self.expire_time.data,'%Y-%m-%d'))
        if expire_time < start_time:
            raise ValidationError(u'添加失败 到期时间小于开通时间')
