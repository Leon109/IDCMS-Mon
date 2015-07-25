#coding=utf-8

import copy
from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required
from . import auth
from .forms import LoginForm, ChangePasswordForm
from ..models import User

@auth.route('/login', methods=['GET', 'POST'])
def login():
    '''用户登录'''
    form = LoginForm()
    if request.method=="POST":
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is not None and user.verify_password(form.password.data):
                # 通过login_user纪录登录用户，form.remember_me.data为真则会
                # 按照config设置纪录登录超时时间
                login_user(user, form.remember_me.data)
                # 登陆成功后跳转页面，如国有访问路径则指定到url的访问路径
                return redirect(request.args.get('next') or url_for('cmdb.index'))
            flash(u'用户名或密码错误')
        else:
            # 打印出输入错误的结果
            for key in form.errors.keys():
                flash(form.errors[key][0])
    return render_template('auth/loading.html', form=form)

@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    '''用户退出'''
    # 使用logout_user()退出用户
    logout_user()
    flash(u'你以退出') 
    return redirect(url_for('auth.login'))

@auth.route('/setting',  methods=['GET', 'POST'])
@login_required
def setting():
    '''用户设置'''
    titles = {'path':'/auth/setting', 'title':u'IDCMS-设置'}
    passwd_form = ChangePasswordForm()
    # 初始模版中的class等
    int_idclass = {
        'adduser':['', 'content hide'],
        'passwd':['active', 'content ']
    } 
    idclass = copy.deepcopy(int_idclass)
    if request.method == "POST":
        idclass = copy.deepcopy(int_idclass)
        # 如果是更改密码
        if request.form['action'] == 'passwd':
            idclass['passwd'] = ['active', 'content']
            if passwd_form.validate_on_submit():
                flash(u'更改完成')
            else:
                for key in passwd_form.errors.keys():
                    flash(passwd_form.errors[key][0])
                    
    return render_template(
            'auth/setting.html',
            passwd_form=passwd_form,
            titles=titles, 
            idclass = idclass
            )
