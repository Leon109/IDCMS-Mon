#coding=utf-8
from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_required, current_user
from . import cmdb
#from .forms import LoginForm
#from ..models import User

@cmdb.route('/', methods=['GET'])
@login_required
def index():
    return redirect(url_for('cmdb.cmdb'))
    
@cmdb.route('/cmdb', methods=['GET', 'POST'])
@login_required
def cmdb():
    uname =  current_user.username
    #form = LoginForm()
    #if form.validate_on_submit():
    #    user = User.query.filter_by(username=form.username.data).first()
    #    if user is not None and user.verify_password(form.password.data):
    #        login_user(user, form.remember_me.data)
    #        return redirect(request.args.get('next') or url_for('main.index'))
    #    flash('Invalid username or password.')
    #return render_template('auth/loading.html', form=form)
    return render_template('cmdb/cmdb.html', uname=uname)
