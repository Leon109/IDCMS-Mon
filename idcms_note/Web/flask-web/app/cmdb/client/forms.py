#coding=utf-8

import os
import sys

from flask.ext.wtf import Form
from wtforms import StringField
from wtforms import ValidationError
from wtforms.validators import Required, Email, Length

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app.models import Sales

class SalesForm(Form):
    username = StringField(u'客户', validators=[Required(message=u'销售名不能为空'), 
                       Length(1, 64, message=u'机房名最大64个字符')])
    contact = StringField(u'联系方式', validators=[Required(message=u'联系方式不能为空'),
                          Length(1, 64, message=u'联系方式为最大64个字符')])
    email = StringField(u'详细地址', validators=[Email(u'请输入一个正确的email地址'), Length(0, 64, message=u'详细地址最大为65个字符')])
    remark = StringField(u'备注', validators=[Length(0, 64, message=u'备注最大64个字符')])
    
    def validate_username(self, field):
        '''如果这么写，wtf会自动监测这个问题'''
        if Sales.query.filter_by(username=field.data).first():
            raise ValidationError(u'这个客户已经添加,不能再次添加')
