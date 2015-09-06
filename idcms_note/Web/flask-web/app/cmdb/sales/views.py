#coding=utf-8

import os
import sys
import copy  

from flask import render_template, request, flash
from flask.ext.login import login_required, current_user

from .. import cmdb
from .forms import SalesForm
from .customvalidator import CustomValidator
from ..sidebar import start_sidebar

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app import db
from app.models import Sales, Rack, IpSubnet, Cabinet
from app.utils.permission import Permission, permission_validation
from app.utils.utils import search_res, record_sql, init_sidebar, init_checkbox


# 初始化参数
sidebar_name = 'sales'
start_thead = [
    [0, u'销售','username', False], [1, u'联系方式', 'contact', False], 
    [2, u'备注' ,'remark', False], [3, u'操作', 'setting', True],
    [4, u'批量处理', 'batch', True]
]
# url分页地址函数
endpoint = '.sales'
del_page = '/cmdb/sales/delete'
change_page= '/cmdb/sales/change'

@cmdb.route('/cmdb/sales',  methods=['GET', 'POST'])
@login_required
def sales():
    '''机房设置'''
    role_Permission = getattr(Permission, current_user.role)
    sales_form = SalesForm()
    sidebar = copy.deepcopy(start_sidebar)
    thead = copy.deepcopy(start_thead)
    sidebar = init_sidebar(sidebar, sidebar_name,'edititem')
    search = ''
    if request.method == "POST" and \
            role_Permission >= Permission.ALTER_REPLY:
        sidebar = init_sidebar(sidebar, sidebar_name, "additem")
        if sales_form.validate_on_submit():
            sales = Sales(
                username=sales_form.username.data,
                contact=sales_form.contact.data,
                remark=sales_form.remark.data
            )
            db.session.add(sales)
            db.session.commit()
            value = (
                "usrename:%s contact:%s remark:%s"
            ) % (sales.username, sales.contact, sales.remark)
            record_sql(current_user.username, u"创建", u"销售",sales.id, "sales", value)
            flash(u'销售添加成功')
        else:
            for key in sales_form.errors.keys():
                flash(sales_form.errors[key][0])
        
    if request.method == "GET":
        search = request.args.get('search', '')
        # hiddens用于分页隐藏字段处理
        checkbox = request.args.getlist('hidden') or request.args.get('hiddens', '') 
        if search:
            thead = init_checkbox(thead, checkbox)
            sidebar = init_sidebar(sidebar, sidebar_name, "edititem")
            page = int(request.args.get('page', 1))
            res = search_res(Sales, 'username' , search)
            res = res.search_return()
            if res:
                pagination = res.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html', thead=thead, endpoint=endpoint, 
                    del_page=del_page, change_page=change_page, item_form=sales_form,
                    sidebar=sidebar, sidebar_name=sidebar_name,  pagination=pagination,
                    search_value=search, items=items, checkbox=str(checkbox)
                )
        return render_template(
            'cmdb/item.html', item_form=sales_form, thead=thead,
            sidebar=sidebar, sidebar_name=sidebar_name, search_value=search
        )

@cmdb.route('/cmdb/sales/delete',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER_REPLY)
def sales_delete():
    del_id = int(request.form["id"])
    sales = Sales.query.filter_by(id=del_id).first()
    if sales:
        if Rack.query.filter_by(sales=sales.username).first():
            return u"删除失败 这个销售有机架在使用"
        if IpSubnet.query.filter_by(sales=sales.username).first():
            return u"删除失败 这个销售有IP子网在使用"
        if Cabinet.query.filter_by(sales=sales.username).first():
            return u"删除失败 这个销售有设备在使用"
        record_sql(current_user.username, u"删除", u"销售", sales.id, "sales", sales.username)
        db.session.delete(sales)
        db.session.commit()
        return "OK"
    return u"删除失败 没有找到这个机房"

@cmdb.route('/cmdb/sales/change',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER_REPLY)
def sales_change():
    change_id = int(request.form["id"])
    item = request.form["item"]
    value = request.form["value"]
    sales = Sales.query.filter_by(id=change_id).first()
    if sales:
        verify = CustomValidator(item, change_id, value)
        res = verify.validate_return()
        if res == "OK":
            record_sql(current_user.username, u"更改", u"销售", sales.id, item, value)
            setattr(sales, item, value) 
            db.session.add(sales)
            return "OK"
        return res 
    return u"更改失败没有找到这个销售"
