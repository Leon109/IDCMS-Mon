#coding=utf-8

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SelectField, ValidationError
from wtforms.validators import Required, Length, EqualTo

from app.models import User

class LoginForm(Form):
    username = StringField(u'用户名', validators=[Required(message=u'用户名不能为空'), 
                           Length(1, 12, message=u'用户名为1-12个字符')])
    password = PasswordField(u'密码',  validators=[Required(message=u'密码不能为空')])
    remember_me = BooleanField("rememberme")


class RegistrationForm(Form):
    username = StringField(u'用户名', validators=[Required(message=u'用户名不能为空'), 
                           Length(1, 12, message=u'用户名为1-12个字符')])
    alias = StringField(u'别名', validators=[Required(message=u'别名不能为空'),
                        Length(1, 12, message=u'别名为1-12个字符')])
    password = PasswordField(u'密码', validators=[Required(u'密码不能为空'), EqualTo('password2', 
                             message=u'两次输入的密码不一致')])
    password2 = PasswordField(u'确认密码', validators=[Required(u'确认密码不能为空')])
    role = SelectField(u'选择角色', choices=[('QUERY', u'查询'), ('ADVANCED_QUERY',u'高级查询'),
                       ('ALTER',u'修改' ), ('ADMIN', u'管理员')])
    
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'添加失败 用户 *** %s *** 已存在' % field.data)

    def validate_alias(self, field):
        if User.query.filter_by(alias=field.data).first():
            raise ValidationError(u'添加失败 别名 *** %s *** 已存在' % field.data)


class ChangePasswordForm(Form):
    old_password = PasswordField(u'旧密码', validators=[Required(message=u'旧密码不能为空')])
    password = PasswordField(u'新密码', validators=[Required(message=u'新密码不能为空'), 
                             EqualTo('password2', message=u'两次输入的密码不一致')])
    password2 = PasswordField(u'确认新密码', validators=[Required(message=u'确认新密码不能为空')])
