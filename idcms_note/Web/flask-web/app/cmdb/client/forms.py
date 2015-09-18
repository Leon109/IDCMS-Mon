#coding=utf-8

from flask.ext.wtf import Form
from wtforms import StringField
from wtforms import ValidationError
from wtforms.validators import Required, Length

from app.models import Client

class ClientForm(Form):
    username = StringField(u'客户', validators=[Required(message=u'销售名不能为空'), 
                       Length(1, 32, message=u'客户名最大64个字符')])
    contact = StringField(u'联系方式', validators=[Required(message=u'联系方式不能为空'),
                          Length(1, 64, message=u'联系方式为最大64个字符')])
    remark = StringField(u'备注', validators=[Length(0, 64, message=u'备注最大64个字符')])
    
    def validate_username(self, field):
        if Client.query.filter_by(username=field.data).first():
            raise ValidationError(u'这个客户已经添加,不能再次添加')
