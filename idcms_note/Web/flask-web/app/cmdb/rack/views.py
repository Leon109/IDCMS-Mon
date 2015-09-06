#coding=utf-8

import os
import sys
import copy

from flask import render_template, request, flash
from flask.ext.login import login_required, current_user

from .. import cmdb
from .forms import RackForm
from .customvalidator import CustomValidator
from ..sidebar import start_sidebar

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app import db
from app.models import Rack, Cabinet
from app.utils.permission import Permission, permission_validation
from app.utils.utils import search_res, record_sql, init_sidebar, init_checkbox

# 初始化参数
sidebar_name = "rack"
start_thead = [
    [0, u'机柜','rack', False], [1,u'机房', 'site', False], 
    [2,u'机架U数', 'count', False],[3, u'机架电流','power', False], 
    [4, u'销售代表', 'sales', False], [5, u'机架用户', 'client', False], 
    [6, u'开通时间' ,'start_time', False],[7, u'到期时间' ,'expire_time', False],
    [8, u'备注' ,'remark', False], [9, u'操作', 'setting', False]
]
# url结尾函数
endpoint = '.rack'
del_page = '/cmdb/rack/delete'
change_page= '/cmdb/rack/change'

@cmdb.route('/cmdb/rack',  methods=['GET', 'POST'])
@login_required
def rack():
    '''机架设置'''
    role_Permission = getattr(Permission, current_user.role)
    rack_form = RackForm()
    sidebar = copy.deepcopy(start_sidebar)
    thead = copy.deepcopy(start_thead)
    sidebar = init_sidebar(sidebar, sidebar_name,'edititem')
    search = ''
    if request.method == "POST" and \
            role_Permission >= Permission.ALTER_REPLY:
        sidebar = init_sidebar(sidebar, sidebar_name, "additem")
        if rack_form.validate_on_submit():
            rack = Rack(
                rack=rack_form.rack.data,
                site=rack_form.site.data,
                count=rack_form.count.data,
                power=rack_form.power.data,
                sales=rack_form.sales.data,
                client=rack_form.client.data,
                start_time=rack_form.start_time.data,
                expire_time=rack_form.expire_time.data,
                remark=rack_form.remark.data
            )
            db.session.add(rack)
            db.session.commit()
            value = (
                "rack:%s site:%s count:%s power:%s sales:%s client:%s"
                "start_time:%s expire_time:%s remark:%s"
            ) % (rack.rack, rack.site, rack.count, rack.power, rack.sales,
                 rack.client, rack.start_time, rack.expire_time, rack.remark)
            record_sql(current_user.username, u"创建", u"机架", rack.id, "rack", value)
            flash(u'机柜添加成功')
        else:
            for key in rack_form.errors.keys():
                flash(rack_form.errors[key][0])

    if request.method == "GET":
        search = request.args.get('search', '')
        checkbox = request.args.getlist('hidden')
        thead = init_checkbox(start_thead, checkbox)
        if search:
            # 搜索
            sidebar = copy.deepcopy(start_sidebar)
            sidebar = init_sidebar(sidebar, sidebar_name, "edititem")
            page = int(request.args.get('page', 1))
            res = search_res(Rack, 'rack', search)
            res = res.search_return()
            if res:
                pagination = res.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html', thead=thead, endpoint=endpoint, 
                    del_page=del_page, change_page=change_page,
                    item_form=rack_form, pagination=pagination,
                    search_value=search,  sidebar=sidebar, sidebar_name=sidebar_name,
                    items=items 
                )
    
    return render_template(
        'cmdb/item.html', item_form=rack_form, thead=thead,
        sidebar=sidebar, sidebar_name=sidebar_name, search_value=search
    )

@cmdb.route('/cmdb/rack/delete',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER_REPLY)
def rack_delete():
    del_id = int(request.form["id"])
    rack = Rack.query.filter_by(id=del_id).first()
    if rack:
        if Cabinet.query.filter_by(rack=rack.rack, site=rack.site).first():
            return u'删除失败，还有设置使用这个机柜'
        record_sql(current_user.username, u"删除", u"机架",
                   rack.id, "rack", rack.rack)
        db.session.delete(rack)
        db.session.commit()
        return "OK"
    return u"删除失败没有找到这个机柜"

@cmdb.route('/cmdb/rack/change',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER_REPLY)
def reak_change():
    change_id = int(request.form["id"])
    item = request.form["item"]
    value = request.form['value']
    rack = Rack.query.filter_by(id=change_id).first()
    if rack:
        verify = CustomValidator(item, change_id, value)
        res = verify.validate_return()
        if res == "OK":
            record_sql(current_user.username, u"更改", u"机架",
                       rack.id, item, value)
            setattr(rack, item, value) 
            db.session.add(rack)
            return "OK"
        return res 
    return u"更改失败没有找到该用户"
