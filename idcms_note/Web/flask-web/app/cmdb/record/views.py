#coding=utf-8

import os
import sys
import copy

from flask import render_template, request
from flask.ext.login import login_required, current_user

from .. import cmdb
from ..sidebar import start_sidebar

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app import db
from app.models import Record
from app.utils.permission import Permission, permission_validation
from app.utils.utils import search_res, init_sidebar, init_checkbox

# 初始化参数
sidebar_name = 'record'
start_thead = [
    [0, u'用户', '', False], [1,u'状态', '', False], [2,u'更改项目', '',  False],
    [3, u'更改ID','', False], [4, u'更改字段', '', False], [5, u'更改内容', '', False],
    [6, u'更改时间', '',False]
]
# url分页地址函数
endpoint = '.record'

@cmdb.route('/cmdb/record',  methods=['GET'])
@login_required
@permission_validation(Permission.ALTER_REPLY)
def record():
    '''机房设置'''
    sidebar = copy.deepcopy(start_sidebar)
    thead = copy.deepcopy(start_thead)
    search = request.args.get('search', '')
    checkbox = request.args.getlist('hidden')
    thead = init_checkbox(thead, checkbox)
    sidebar, li_css = init_sidebar(sidebar, sidebar_name,'edititem')
    if search:
        # 搜索
        page = int(request.args.get('page', 1))
        res = search_res(Record, 'username' , search)
        res = res.search_return()
        if res:
            pagination = res.paginate(page, 100, False)
            items = pagination.items
            return render_template(
                'cmdb/record.html', thead=thead, 
                endpoint=endpoint, pagination=pagination,
                search_value=search, sidebar=sidebar,
                items=items
            )

    return render_template(
        'cmdb/record.html', thead=thead, sidebar=sidebar,
         search_value=search
    )
