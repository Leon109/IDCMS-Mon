#coding=utf-8

from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, current_user

from forms import LoginForm, ChangePasswordForm, RegistrationForm
from . import auth
from .. import db
from ..models import User
from ..utils.permission import Permission, permission_validation

def int_idclass(id_class):
    idclass = { 
        'register':['', 'content hide'],
        'passwd':['', 'content hide'],
        'edituser':['', 'content hide']
    }   
    idclass[id_class] = ['active', 'content ']
    return idclass

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
    passwd_form = ChangePasswordForm()
    register_form = RegistrationForm()
    idclass = int_idclass('passwd')
    if request.method == "POST":
        # 更改密码
        if request.form['action'] == 'passwd':
            idclass = int_idclass('passwd')
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
        if request.form['action'] == 'register':
            idclass = int_idclass('register')
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
            idclass = int_idclass('edituser')
            try:
                option = {docm.split("==")[0]:docm.split("==")[1] for docm in search.split()}
                if option:
                    for key in option.keys():
                        # 第一次进行初始查询，后面的开始从上一次的基础上进行过滤
                        if key == option.keys()[0]:
                            res = User.query.filter(getattr(User,key).endswith(option[key]))
                        res = res.filter(getattr(User,key).endswith(option[key]))
    
            except IndexError:
                if search == "ALL":
                    res = User.query
                else:
                    res = User.query.filter(User.username.endswith(search))
            except (ValueError, AttributeError):
                res = None
            if res:
                pagination = res.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'auth/setting.html',
                    passwd_form=passwd_form,
                    register_form=register_form,
                    idclass=idclass,
                    pagination=pagination,
                    search_value=search,
                    items=items,
                )
    return render_template(
        'auth/setting.html',
        passwd_form=passwd_form,
        register_form=register_form,
        idclass=idclass,
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
        return "ok"
    return u"删除失败没有找到改用户"
