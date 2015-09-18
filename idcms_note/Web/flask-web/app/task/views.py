#coding=utf-8

import copy
import datetime

from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_required, current_user

from . import task
from .forms import TaskForm
from .sidebar import start_sidebar

from .. import db
from ..models import Task
from ..utils.permission import Permission, permission_validation
from app.utils.utils import search_res, init_sidebar, init_checkbox

# 初始化参数
sidebar_name = 'task'
#start_thead = [
#        [0, u'用户名','username', False, False], [1,u'密码', 'password', False, False], 
#        [2,u'权限', 'role', False, True], [3, u'操作', 'setting', True],
#        [4, u'批量处理', 'batch', True]
#]

@task.route('/task',  methods=['GET', 'POST'])
@login_required
def task():
    task_form = TaskForm()
    sidebar = copy.deepcopy(start_sidebar)
    sidebar = init_sidebar(sidebar, sidebar_name,'put_task')
    if request.method == "GET":
        pass
    if request.method == "POST":
        if request.form['action'] == 'put_task':
            idebar = init_sidebar(sidebar, sidebar_name,'put_task')
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            task = Task(
                author=current_user.username,
                title=task_form.title.data,
                task=task_form.task.data,
                site=task_form.site.data,
                body=task_form.body.data,
                date=date,
                status=u"审核"
            )
            db.session.add(task)
            flash(u'任务添加成功 可以继续添加新的任务')

    return render_template(
        'task/task.html', task_form=task_form, sidebar=sidebar, sidebar_name=sidebar_name
    )
