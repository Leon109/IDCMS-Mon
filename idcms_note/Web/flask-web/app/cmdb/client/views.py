#coding=utf-8

import os
import sys

from flask import render_template, request, flash
from flask.ext.login import login_required, current_user

from .. import cmdb
from .forms import clientForm
from .customvalidator import CustomValidator

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app import db
from app.models import Client, Rack, IpPool, Cabinet
from app.utils.permission import Permission, permission_validation
from app.utils.searchutils import search_res
from app.utils.record import record_sql

# 初始化参数
titles = {'path':'/cmdb/client', 'title':u'IDCMS-CMDB-客户管理'}
thead = [
    [0, u'客户','username'], [1,u'联系方式', 'contact'], [2,u'邮箱地址', 'email'],
    [3, u'备注' ,'remark']
]
# url分页地址函数
endpoint = '.client'
del_page = '/cmdb/client/delete'
change_page= '/cmdb/client/change'


def init__sidebar(sidebar_class):
    sidebarclass = {
        'edititem':['', 'content hidden', u'管理销售'],
        'additem':['', 'content hidden', u'添加销售']
    }
    sidebarclass[sidebar_class][0] = 'active' 
    sidebarclass[sidebar_class][1] = 'content'
    return sidebarclass

@cmdb.route('/cmdb/client',  methods=['GET', 'POST'])
@login_required
def client():
    '''机房设置'''
    role_Permission = getattr(Permission, current_user.role)
    client_form = ClientForm()
    sidebarclass = init__sidebar('edititem')
    if request.method == "POST" and \
            role_Permission >= Permission.ALTER_REPLY:
        sidebarclass = init__sidebar('additem')
        if client_form.validate_on_submit():
            client = Client(
                client=Client_form.username.data,
                contact=client_form.contact.data,
                email=client_form.email.data,
                remark=client_form.remark.data
            )
            db.session.add(client)
            db.session.commit()
            value = (
                "username:%s isp:%s contact:%s email:%s","remark:%s"
            ) % (client.usrename, client.contact, client.email, client.remark)
            record_sql(current_user.username, u"创建", u"销售",
                       client.id, "client", value)
            flash(u'客户添加成功')
        else:
            for key in client_form.errors.keys():
                flash(client_form.errors[key][0])
        
    if request.method == "GET":
        search = request.args.get('search', '')
        if search:
            # 搜索
            page = int(request.args.get('page', 1))
            sidebarclass = init__sidebar('edititem')
            res = search_res(client, 'client' , search)
            if res:
                pagination = res.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html', titles=titles, thead=thead, 
                    endpoint=endpoint, del_page=del_page, change_page=change_page, 
                    item_form=client_form, sidebarclass=sidebarclass, pagination=pagination,
                    search_value=search, items=items
                )

    return render_template(
        'cmdb/item.html', titles = titles, item_form=client_form, 
        sidebarclass=sidebarclass
    )

@cmdb.route('/cmdb/client/delete',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER_REPLY)
def client_delete():
    del_id = int(request.form["id"])
    client = Client.query.filter_by(id=del_id).first()
    if client:
        if Rack.query.filter_by(client=client.username).first():
            return u"删除失败 这个销售有机架在使用"
        if IpPool.query.filter_by(client=client.username).first():
            return u"删除失败 这个销售有IP子网在使用"
        if Cabinet.query.filter_by(client=client.username).first():
            return u"删除失败 这个销售有设备在使用"
        record_sql(current_user.username, u"删除", u"客户",
                   client.id, "client", client.username)
        db.session.delete(client)
        db.session.commit()
        return "OK"
    return u"删除失败 没有找到这个客户"

@cmdb.route('/cmdb/client/change',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER_REPLY)
def client_change():
    change_id = int(request.form["id"])
    item = request.form["item"]
    value = request.form["value"]
    client = Client.query.filter_by(id=change_id).first()
    if client:
        verify = CustomValidator(item, change_id, value)
        res = verify.validate_return()
        if res == "OK":
            record_sql(current_user.username, u"更改", u"客户",
                        client.id, item, value)
            setattr(client, item, value) 
            db.session.add(client)
            return "OK"
        return res 
    return u"更改失败没有找到该客户"
