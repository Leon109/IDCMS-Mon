#coding=utf-8

from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, current_user

from . import auth
from .forms import LoginForm, ChangePasswordForm, RegistrationForm
from .customvalidator import CustomValidator
from .. import db
from ..models import User
from ..utils.permission import Permission, permission_validation
from ..utils.utils import search_res

thead = [[0, u'用户名','username'], [1,u'密码', 'password'], [2,u'权限', 'role']]

def init__sidebar(sidebar_class):
    sidebarclass = { 
        'register':['', 'content hidden'],
        'passwd':['', 'content hidden'],
        'edituser':['', 'content hidden']
    }   
    sidebarclass[sidebar_class] = ['active', 'content ']
    return sidebarclass

@auth.route('/login', methods=['GET', 'POST'])
def login():
    '''用户登录'''
    form = LoginForm()
    if request.method=="POST":
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is not None and user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or url_for('cmdb.index'))
            flash(u'用户名或密码错误')
        else:
            for key in form.errors.keys():
                flash(form.errors[key][0])
    return render_template('auth/loading.html', form=form)

@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    '''用户退出'''
    logout_user()
    flash(u'你以退出') 
    return redirect(url_for('auth.login'))

@auth.route('/setting',  methods=['GET', 'POST'])
@login_required
def setting():
    '''用户设置'''
    role_Permission = getattr(Permission, current_user.role)
    passwd_form = ChangePasswordForm()
    register_form = RegistrationForm()
    sidebarclass = init__sidebar('passwd')
    if request.method == "POST":
        # 更改密码
        if request.form['action'] == 'passwd' and \
                role_Permission >= Permission.ADMIN:
            sidebarclass = init__sidebar('passwd')
            if passwd_form.validate_on_submit():
                if current_user.verify_password(passwd_form.old_password.data):
                    current_user.password = passwd_form.password.data
                    db.session.add(current_user)
                    flash(u'密码更改成功')
                else:
                    flash(u'旧密码错误')
            else:
                for key in passwd_form.errors.keys():
                    flash(passwd_form.errors[key][0])
        # 用户注册
        if request.form['action'] == 'register' and \
                role_Permission >= Permission.ADMIN:
            sidebarclass = init__sidebar('register')
            if register_form.validate_on_submit():
                user = User(username=register_form.username.data,
                    password=register_form.password.data,
                    role=register_form.role.data)
                db.session.add(user) 
                flash(u'用户添加成功')
            else:
                for key in register_form.errors.keys():
                    flash(register_form.errors[key][0])
    
    if request.method == "GET":
        search = request.args.get('search', '')
        if search:
            # 搜索
            page = int(request.args.get('page', 1))
            sidebarclass = init__sidebar('edituser')
            res = search_res(User, 'username' , search)
            if res:
                pagination = res.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'auth/setting.html', thead=thead, passwd_form=passwd_form, register_form=register_form,
                    sidebarclass=sidebarclass, pagination=pagination, search_value=search,
                    items=items
                )
    return render_template(
        'auth/setting.html', passwd_form=passwd_form, register_form=register_form,
        sidebarclass=sidebarclass
    )

@auth.route('/setting/delete',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ADMIN)
def delete():
    del_id = int(request.form["id"])
    user = User.query.filter_by(id=del_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return "OK"
    return u"删除失败没有找到该用户"

@auth.route('/setting/change',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ADMIN)
def change():
    change_id = int(request.form["id"])
    item = request.form["item"]
    value = request.form['value']
    user = User.query.filter_by(id=change_id).first()
    if user:
        verify = CustomValidator(item,value)
        res = verify.validate_return()
        if res == "OK":
            setattr(user, item, value) 
            db.session.add(user)
            return "OK"
        return res
    return u"更改失败没有找到该用户"
