#coding=utf-8

import os
import sys
import copy

from flask import render_template, request, flash
from flask.ext.login import login_required, current_user

from .. import cmdb
from .forms import ClientForm
from .customvalidator import CustomValidator
from ..sidebar import start_sidebar

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app import db
from app.models import Client, Rack, IpSubnet, IpPool, Cabinet
from app.utils.permission import Permission, permission_validation
from app.utils.utils import search_res, record_sql, init_sidebar, init_checkbox

# 初始化参数
sidebar_name = "client"
start_thead = [
    [0, u'客户','username', False, False], [1,u'联系方式', 'contact', False, False], 
    [2, u'备注' ,'remark', False, True], [3, u'操作', 'setting', True],
    [4, u'批量处理', 'batch', True]
]
# url分页地址函数
endpoint = '.client'
set_page = { 
    'del_page': '/cmdb/client/delete',
    'change_page': '/cmdb/client/change',
    'batch_del_page': '/cmdb/client/batchdelete',
    'batch_change_page': '/cmdb/client/batchchange'
}

@cmdb.route('/cmdb/client',  methods=['GET', 'POST'])
@login_required
def client():
    '''机房设置'''
    role_Permission = getattr(Permission, current_user.role)
    client_form = ClientForm()
    sidebar = copy.deepcopy(start_sidebar)
    thead = copy.deepcopy(start_thead)
    sidebar = init_sidebar(sidebar, sidebar_name,'edititem')
    search = ''
    if request.method == "POST" and \
            role_Permission >= Permission.ALTER:
        sidebar = init_sidebar(sidebar, sidebar_name, "additem")
        if client_form.validate_on_submit():
            client = Client(
                username=client_form.username.data,
                contact=client_form.contact.data,
                remark=client_form.remark.data
            )
            db.session.add(client)
            db.session.commit()
            value = (
                "username:%s contact:%s remark:%s"
            ) % (client.username, client.contact, client.remark)
            record_sql(current_user.username, u"创建", u"销售", client.id, "client", value)
            flash(u'客户添加成功')
        else:
            for key in client_form.errors.keys():
                flash(client_form.errors[key][0])
        
    if request.method == "GET":
        search = request.args.get('search', '')
        # hiddens用于分页隐藏字段处理
        checkbox = request.args.getlist('hidden') or request.args.get('hiddens', '') 
        if search:
            # 搜索
            thead = init_checkbox(thead, checkbox)
            sidebar = init_sidebar(sidebar, sidebar_name, "edititem")
            page = int(request.args.get('page', 1)) 
            res = search_res(Client, 'username' , search)
            res = res.search_return()
            if res:
                pagination = res.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html', thead=thead, endpoint=endpoint, set_page=set_page,
                    item_form=client_form, pagination=pagination, search_value=search,
                    sidebar=sidebar, sidebar_name=sidebar_name, items=items, checkbox=str(checkbox)
                )

    return render_template(
        'cmdb/item.html', item_form=client_form, thead=thead, set_page=set_page,
        sidebar=sidebar, sidebar_name=sidebar_name, search_value=search
    )

@cmdb.route('/cmdb/client/delete',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER)
def client_delete():
    del_id = int(request.form["id"])
    client = Client.query.filter_by(id=del_id).first()
    if client:
        if Rack.query.filter_by(client=client.username).first():
            return u"删除失败 这个销售有机架在使用"
        if IpSubnet.query.filter_by(client=client.username).first():
            return u"删除失败 这个销售有IP子网在使用"
        if IpPool.query.filter_by(client=client.username).first():
            return u"删除失败 这个销售有IP在使用"
        if Cabinet.query.filter_by(client=client.username).first():
            return u"删除失败 这个销售有设备在使用"
        record_sql(current_user.username, u"删除", u"客户", client.id, "client", client.username)
        db.session.delete(client)
        db.session.commit()
        return "OK"
    return u"删除失败 没有找到这个客户"

@cmdb.route('/cmdb/client/change',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER)
def client_change():
    change_id = int(request.form["id"])
    item = request.form["item"]
    value = request.form["value"]
    client = Client.query.filter_by(id=change_id).first()
    if client:
        verify = CustomValidator(item, change_id, value)
        res = verify.validate_return()
        if res == "OK":
            record_sql(current_user.username, u"更改", u"客户", client.id, item, value)
            setattr(client, item, value) 
            db.session.add(client)
            return "OK"
        return res 
    return u"更改失败没有找到该客户"

# 批量删除
@cmdb.route('/cmdb/client/batchdelete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def client_batch_delete():
    list_id = eval(request.form["list_id"])

    for id in list_id:
        client = Client.query.filter_by(id=id).first()
        if client:
            if Rack.query.filter_by(client=client.username).first():
                return u"删除失败 *** <b>%s</b> *** 有机架在使用" % client.username
            if IpSubnet.query.filter_by(client=client.username).first():
                return u"删除失败 *** <b>%s</b> *** 有IP子网在使用" % client.username
            if IpPool.query.filter_by(client=client.username).first():
                return u"删除失败 *** <b>%s</b> *** 有IP在使用" % client.username
            if Cabinet.query.filter_by(client=client.username).first():
                return u"删除失败  *** <b>%s</b> *** 有设备在使用" % client.username
        else:
            return u"删除失败没有这些客户"

    for id in list_id:
        client = Client.query.filter_by(id=id).first()
        record_sql(current_user.username, u"删除", u"客户", client.id, "client", client.username)
        db.session.delete(client)
    db.session.commit()
    return "OK"

# 批量修改
@cmdb.route('/cmdb/client/batchchange',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def client_batch_change():
    list_id = eval(request.form["list_id"])
    item = request.form["item"]
    value = request.form["value"]

    for id in list_id:
        client = Client.query.filter_by(id=id).first()
        if client:
            verify = CustomValidator(item, id, value)
            res = verify.validate_return()
            if not res == "OK":
                return res
        else:
            return u"更改失败没有找到这些客户"

    for id in list_id:
        client = Client.query.filter_by(id=id).first()
        record_sql(current_user.username, u"更改", u"客户", client.id, item, value)
        setattr(client, item, value)
        db.session.add(client)
    return "OK"
