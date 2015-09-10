#coding=utf-8

import os
import sys
import copy

from flask import render_template, request, flash
from flask.ext.login import login_required, current_user

from .. import cmdb
from .forms import IpPoolForm
from .customvalidator import CustomValidator
from ..sidebar import start_sidebar

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app import db
from app.models import IpPool, Cabinet
from app.utils.permission import Permission, permission_validation
from app.utils.utils import search_res, record_sql, init_sidebar, init_checkbox

# 初始化参数
sidebar_name = 'ippool'
start_thead = [
    [0, u'IP','ip', False, False], [1,u'子网掩码', 'netmask', False, True], 
    [2,u'网关地址', 'gateway', False, True], [3, u'所属子网','subnet', False, True], 
    [4, u'所属机房', 'site', False, True], [5, u'销售代表', 'sales', False, True],
    [6, u'使用用户' ,'client', False, True], [7, u'备注' ,'remark', False, True],
    [8, u'操作', 'setting', True], [9, u'批量处理', 'batch', True]
]
# url分页地址函数
endpoint = '.ippool'
set_page = { 
    'del_page': '/cmdb/ippool/delete',
    'change_page': '/cmdb/ippool/change',
    'batch_del_page': '/cmdb/ippool/batchdelete',
    'batch_change_page': '/cmdb/ippool/batchchange'
}

@cmdb.route('/cmdb/ippool',  methods=['GET', 'POST'])
@login_required
def ippool():
    '''IP池'''
    role_Permission = getattr(Permission, current_user.role)
    ippool_form = IpPoolForm()
    sidebar = copy.deepcopy(start_sidebar)
    thead = copy.deepcopy(start_thead)
    sidebar = init_sidebar(sidebar, sidebar_name,'edititem')
    search = ''
    if request.method == "POST" and \
            role_Permission >= Permission.ALTER:
        sidebar = init_sidebar(sidebar, sidebar_name,'additem')
        if ippool_form.validate_on_submit():
            ip_list = ippool_form.start_ip.data.split('.')
            fornt_ip = '.'.join(ip_list[:-1])
            start_ip = int(ip_list[-1]) 
            end_ip = int(ippool_form.end_ip.data) + 1
            for i in range(start_ip, end_ip):
                add_ip = fornt_ip + ".%s" % i
                if not IpPool.query.filter_by(ip=add_ip).first():
                    ippool = IpPool(
                        ip = add_ip,
                        netmask=ippool_form.netmask.data,
                        gateway=ippool_form.gateway.data,
                        subnet=ippool_form.subnet.data,
                        site=ippool_form.site.data,
                        sales=ippool_form.sales.data,
                        client=ippool_form.client.data,
                        remark=ippool_form.remark.data
                    )
                    db.session.add(ippool)
                    db.session.commit()
                    
                    value = ("ip:%s netmask:%s gateway:%s subnet:%s site:%s "
                            "sales:'%s" "client:%s remark:%s"
                    ) % (ippool.ip, ippool.netmask, ippool.gateway, ippool.subnet,
                         ippool.site, ippool.sales, ippool.client, ippool.remark)
                    record_sql(current_user.username, u"创建", u"IP池",
                               ippool.id, "ip", value)
                else:
                    flash(u'添加失败 %s 已经添加' % add_ip)
                    break
            flash(u'IP添加成功')    
        else:
            for key in ippool_form.errors.keys():
                flash(ippool_form.errors[key][0])

    if request.method == "GET":
        search = request.args.get('search', '')
        # hiddens用于分页隐藏字段处理
        checkbox = request.args.getlist('hidden') or request.args.get('hiddens', '')
        if search:
            # 搜索
            thead = init_checkbox(thead, checkbox)
            sidebar = init_sidebar(sidebar, sidebar_name, "edititem")
            page = int(request.args.get('page', 1))
            res = search_res(IpPool, 'ip', search)
            res = res.search_return()
            if res:
                pagination = res.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html', thead=thead, endpoint=endpoint, set_page=set_page, 
                    item_form=ippool_form, pagination=pagination, search_value=search,
                    sidebar=sidebar, sidebar_name=sidebar_name, items=items, checkbox=str(checkbox)
                )
    
    return render_template(
        'cmdb/item.html', item_form=ippool_form, thead=thead, set_page=set_page,
        sidebar=sidebar, sidebar_name=sidebar_name, search_value=search
    )

@cmdb.route('/cmdb/ippool/delete',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER)
def ippool_delete():
    del_id = int(request.form["id"])
    ippool = IpPool.query.filter_by(id=del_id).first()
    if ippool:
        if Cabinet.query.filter_by(wan_ip=ippool.ip).first():
            return "删除失败 这个IP有设备在使用"
        record_sql(current_user.username, u"删除", u"IP池",
                   ippool.id, "ip", ippool.ip)
        db.session.delete(ippool)
        db.session.commit()
        return "OK"
    return u"删除失败 没有找到这个IP"

@cmdb.route('/cmdb/ippool/change',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER)
def ippool_change():
    change_id = int(request.form["id"])
    item = request.form["item"]
    value = request.form['value']
    ippool = IpPool.query.filter_by(id=change_id).first()
    if ippool:
        verify = CustomValidator(item, value)
        res = verify.validate_return()
        if res == "OK":
            record_sql(current_user.username, u"更改", u"IP池",
                       ippool.id, item, value)
            setattr(ippool, item, value) 
            db.session.add(ippool)
            return "OK"
        return res
    return u"更改失败没有找到该IP"

@cmdb.route('/cmdb/ippool/batchdelete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def ippool_batch_delete():
    list_id = eval(request.form["list_id"])

    for id in list_id:
        ippool = IpPool.query.filter_by(id=id).first()
        if ippool:
            if Cabinet.query.filter_by(wan_ip=ippool.ip).first():
                return u"删除失败 *** <b>%s</b> *** 有设备在使用" % ippool.ip
        else:
            return u"删除失败没有这些IP"

    for id in list_id:
        ippool = IpPool.query.filter_by(id=id).first()
        record_sql(current_user.username, u"删除", u"IP池", ippool.id, "ip", ippool.ip)
        db.session.delete(ippool)
    db.session.commit()
    return "OK"

@cmdb.route('/cmdb/ippool/batchchange',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def ippool_batch_change():
    list_id = eval(request.form["list_id"])
    item = request.form["item"]
    value = request.form["value"]

    for id in list_id:
        ippool = IpPool.query.filter_by(id=id).first()
        if ippool:
            verify = CustomValidator(item, value)
            res = verify.validate_return()
            if not res == "OK":
                return res
        else:
            return u"更改失败没有找到这些IP"

    for id in list_id:
        ippool = IpPool.query.filter_by(id=id).first()
        record_sql(current_user.username, u"更改", u"IP池", ippool.id, item, value)
        setattr(ippool, item, value)
        db.session.add(ippool)
    return "OK"
