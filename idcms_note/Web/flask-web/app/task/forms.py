#coding=utf-8

from flask.ext.wtf import Form
from wtforms import StringField,  SelectField, TextAreaField
from wtforms import ValidationError
from wtforms.validators import Required, Length
from ..models import Site

from manage import app

# 获取主机列表，配置使用了工厂模式，需要使用 app.app_context，
# 先将应用上下问题推入才能使用数据库查询
def site_list():
    with app.app_context():
        site = [(site.site,site.site) for site in Site.query.all()]
    return site

class TaskForm(Form):
    title = StringField(u'标题', validators=[Required(message=u'标题不能为空'), 
                        Length(1, 64, message=u'标题为1-64个字符')])
    task = SelectField(u'选择任务', choices=[(u'上架', u'上架'), (u'下架',u'下架'),
                       (u'迁移',u'迁移' ), (u'更换IP', u'更换IP'),(u'更改带宽',u'更改带宽'),
                       (u'其他', u'其他')])
    site = SelectField(u'选择机房', choices= site_list())
    body = TextAreaField(u"任务内容", validators=[Required(message=u'任务内容不能为空')])


#class RegistrationForm(Form):
#    username = StringField(u'用户名', validators=[
#        Required(message=u'用户名不能为空'), Length(1, 12, message=u'用户名为1-12个字符')])
#    password = PasswordField(u'密码', validators=[
#        Required(u'密码不能为空'), EqualTo('password2', message=u'两次输入的密码不一致')])
#    password2 = PasswordField(u'确认密码', validators=[Required(u'确认密码不能为空')])
#    role = SelectField(u'选择角色', choices=[('QUERY', u'查询'), ('ADVANCED_QUERY',u'高级查询'),
#        ('ALTER',u'修改' ), ('ADMIN', u'管理员')])
#    
#    def validate_username(self, field):
#        '''如果这么写，wtf会自动监测这个问题
#        格式 alidate_ 加字段名
#        '''
#        if User.query.filter_by(username=field.data).first():
#            raise ValidationError(u'用户名已经存在')
#
#
#class ChangePasswordForm(Form):
#    old_password = PasswordField(u'旧密码', validators=[Required(message=u'旧密码不能为空')])
#    password = PasswordField(u'新密码', validators=[
#        Required(message=u'新密码不能为空'), EqualTo('password2', message=u'两次输入的密码不一致')])
#    password2 = PasswordField(u'确认新密码', validators=[Required(message=u'确认新密码不能为空')])
