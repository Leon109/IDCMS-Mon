#coding=utf-8
import copy

from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, current_user

from . import auth
from .forms import LoginForm, ChangePasswordForm, RegistrationForm
from .customvalidator import CustomValidator
from .sidebar import start_sidebar

from .. import db
from ..models import User
from ..utils.permission import Permission, permission_validation
from app.utils.utils import search_res, init_sidebar, init_checkbox

# 初始化参数
sidebar_name = 'setting'
start_thead = [
        [0, u'用户名','username', False, False], [1, u'别名', 'alias', False, False],  
        [1, u'密码', 'password', False, False], [2, u'权限', 'role', False, True], 
        [3, u'操作', 'setting', True], [4, u'批量处理', 'batch', True]
]

endpoint='.users_setting'

set_page ={
    "del_page": '/auth/setting/delete',
    "change_page": '/auth/setting/change',
    'batch_del_page': '/cmdb/auth/batchdelete',
    'batch_change_page': '/cmdb/auth/batchchange'
}

@auth.route('/', methods=['GET'])
@login_required
def index():
    return redirect(url_for('cmdb.cabinet'))

@auth.route('/auth/login', methods=['GET', 'POST'])
def login():
    '''用户登录'''
    form = LoginForm()
    if request.method=="POST":
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is not None and user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next')  or url_for('cmdb.cabinet'))
            flash(u'用户名或密码错误')
        else:
            for key in form.errors.keys():
                flash(form.errors[key][0])
    return render_template('auth/loading.html', form=form)

@auth.route('/auth/logout', methods=['GET'])
@login_required
def logout():
    '''用户退出'''
    logout_user()
    flash(u'你以退出') 
    return redirect(url_for('auth.login'))

@auth.route('/auth/setting',  methods=['GET', 'POST'])
@login_required
def users_setting():
    '''用户设置'''
    role_Permission = getattr(Permission, current_user.role)
    passwd_form = ChangePasswordForm()
    register_form = RegistrationForm()
    sidebar = copy.deepcopy(start_sidebar)
    thead = copy.deepcopy(start_thead)
    sidebar = init_sidebar(sidebar, sidebar_name,'passwd')
    search = ''
    if request.method == "POST":
        # 更改密码
        if request.form['action'] == 'passwd':
            sidebar = init_sidebar(sidebar, sidebar_name,'passwd')
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
            sidebar = init_sidebar(sidebar, sidebar_name,'register')
            if register_form.validate_on_submit():
                user = User(username=register_form.username.data,
                    password=register_form.password.data,
                    alias=register_form.alias.data,
                    role=register_form.role.data)
                db.session.add(user) 
                flash(u'用户添加成功')
            else:
                for key in register_form.errors.keys():
                    flash(register_form.errors[key][0])
    
    if request.method == "GET":
        search = request.args.get('search', '')
        checkbox = request.args.getlist('hidden') or request.args.get('hiddens', '')
        if search:
            # 搜索
            thead = init_checkbox(thead, checkbox)
            sidebar = init_sidebar(sidebar, sidebar_name,'edituser')
            page = int(request.args.get('page', 1))
            res = search_res(User, 'username' , search)
            res = res.search_return()
            if res:
                pagination = res.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'auth/setting.html', passwd_form=passwd_form, register_form=register_form, set_page=set_page,
                    thead=thead, endpoint=endpoint, sidebar=sidebar, sidebar_name=sidebar_name, pagination=pagination,
                    search_value=search, items=items, checkbox=str(checkbox)
                )
    return render_template(
        'auth/setting.html', passwd_form=passwd_form, register_form=register_form, set_page=set_page,
        thead=thead, sidebar=sidebar, sidebar_name=sidebar_name
    )

@auth.route('/auth/setting/delete',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ADMIN)
def users_delete():
    del_id = int(request.form["id"])
    user = User.query.filter_by(id=del_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return "OK"
    return u"删除失败没有找到该用户"

@auth.route('/auth/setting/change',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ADMIN)
def users_change():
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

@auth.route('/cmdb/auth/batchdelete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def users_batch_delete():
    list_id = eval(request.form["list_id"])
    for id in list_id:
        user = User.query.filter_by(id=id).first()
        if not user:
            return u"删除失败没有找到这些用户"

    for id in list_id:
        user = User.query.filter_by(id=id).first()
        db.session.delete(user)
    db.session.commit()
    return "OK"

@auth.route('/cmdb/auth/batchchange',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def users_batch_change():
    list_id = eval(request.form["list_id"])
    item = request.form["item"]
    value = request.form["value"]

    for id in list_id:
        user = User.query.filter_by(id=id).first()
        if user:
            verify = CustomValidator(item, value)
            res = verify.validate_return()
            if not res == "OK":
                return res
        else:
            return u"更改失败没有找到这些用户"

    for id in list_id:
        user = User.query.filter_by(id=id).first()
        setattr(user, item, value)
        db.session.add(user)
    return "OK"
