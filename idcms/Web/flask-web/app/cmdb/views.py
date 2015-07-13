#coding=utf-8
from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_required, current_user
from . import cmdb

@cmdb.route('/', methods=['GET'])
@login_required
def index():
    return redirect(url_for('cmdb.cmdb'))
    
@cmdb.route('/cmdb', methods=['GET', 'POST'])
@login_required
def cmdb():
    uname =  current_user.username
    return render_template('cmdb/cmdb.html', uname=uname)
