#coding=utf-8

import os
import sys

from flask.ext.wtf import Form
from wtforms import StringField, SelectField
from wtforms import ValidationError
from wtforms.validators import Required, Length, Regexp

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app.models import Site, Rack
from app.utils.searchutils import re_date


class RackForm(Form):
    rack = StringField(u'机架名称', validators=[Required(message=u'机架名不能为空'), 
                Length(1, 32, message=u'机房名为1-32个字符')])
    site = StringField(u'机房名称', validators=[Required(message=u'机房名不能为空'), 
        Length(1, 64, message=u'机房名为1-64个字符')])
    count = SelectField(u'机架U数', choices=[('42U', '42U'),('48U', '48U'), ('60U', '60U' )])
    power = SelectField(u'机架电流', choices=[('10A', '10A'),('14A', '14A'), ('15A','15A' ),
        ('20A','20A')])
    client = StringField(u'机架用户', validators=[Length(1, 64, message=u'机架用户为1-64个字符')])
    c_time = StringField(u'开通日期', validators=[Regexp(re_date, message=u'开通时间格式为yyyy-mm-dd')])
    e_time = StringField(u'到期日期',validators=[Regexp(re_date, message=u'到期时间格式为yyyy-mm-dd')])
    remark = StringField(u'备注')
    
    def validate_rack(self, field):
        if Rack.query.filter_by(rack=field.data, site=self.site.data).first():
            raise ValidationError(u'添加失败，这个机房已经有该机柜')

    def validate_site(self, field):
        if not Site.query.filter_by(site=field.data).first():
            raise ValidationError(u'添加失败，这个机房不存在')
