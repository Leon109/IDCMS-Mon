#coding=utf-8

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, EqualTo


class LoginForm(Form):
    username = StringField('Username', validators=[Required(message=u'用户名不能为空'), 
        Length(1, 12, message=u'用户名最大为12个字符')])
    password = PasswordField('Password',  validators=[Required(message=u'密码不能为空')])
    remember_me = BooleanField("rememberme")

class ChangePasswordForm(Form):
    old_password = PasswordField(u'旧密码', validators=[Required(message=u'旧密码不能为空')])
    password = PasswordField(u'新密码', validators=[
        Required(message=u'新密码不能为空'), EqualTo('password2', message=u'两次输入的密码不一致')])
    password2 = PasswordField(u'确认新密码', validators=[Required(message=u'确认新密码不能为空')])
