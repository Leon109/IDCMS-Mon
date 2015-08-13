#coding=utf-8

import os
import sys

from flask import render_template, request
from flask.ext.login import login_required, current_user

from .. import cmdb

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app import db
from app.models import Record
from app.utils.permission import Permission, permission_validation
from app.utils.searchutils import search_res

# 初始化参数
titles = {'path':'/cmdb/record', 'title':u'IDCMS-CMDB-记录'}
thead = [
    [0, u'用户'], [1,u'状态'], [2,u'更改项目'],[3, u'更改ID'], 
    [4, u'更改字段'], [5, u'更改内容'],
    [6, u'更改时间']
]
# url分页地址函数
endpoint = '.record'

@cmdb.route('/cmdb/record',  methods=['GET'])
@login_required
@permission_validation(Permission.ALTER_REPLY)
def record():
    '''机房设置'''
    search = request.args.get('search', '')
    if search:
        # 搜索
        page = int(request.args.get('page', 1))
        res = search_res(Record, 'username' , search)
        if res:
            pagination = res.paginate(page, 100, False)
            items = pagination.items
            return render_template(
                'cmdb/record.html', titles=titles, thead=thead, 
                endpoint=endpoint, pagination=pagination,
                search_value=search, items=items
            )

    return render_template(
        'cmdb/record.html', titles = titles, 
    )
