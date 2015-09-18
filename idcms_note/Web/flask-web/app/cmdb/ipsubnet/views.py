#coding=utf-8

import copy

from flask import render_template, request, flash
from flask.ext.login import login_required, current_user

from .. import cmdb
from .forms import IpSubnetForm
from .customvalidator import CustomValidator
from ..sidebar import start_sidebar

from app import db
from app.models import IpSubnet, IpPool
from app.utils.permission import Permission, permission_validation
from app.utils.utils import search_res, record_sql, init_sidebar, init_checkbox

# 初始化参数
sidebar_name = "ipsubnet"
start_thead = [
    [0, u'IP子网','subnet', False, False], [1,u'起始IP', 'start_ip', False, False], 
    [2,u'结束IP', 'end_ip', False, False],[3, u'子网掩码','netmask', False, False], 
    [4, u'所属机房', 'site', False, True], [5, u'销售代表', 'sales', False, True], 
    [6, u'使用用户', 'client', False, True], [7, u'开通时间' ,'start_time', False, True], 
    [8, u'到期时间' ,'expire_time', False, True], [9, u'备注' ,'remark', False],
    [10, u'操作', "setting", True], [11, u'批量处理', 'batch', True]
]
# url分页地址函数
endpoint = '.ipsubnet'
set_page = { 
    'del_page': '/cmdb/ipsubnet/delete',
    'change_page': '/cmdb/ipsubnet/change',
    'batch_del_page': '/cmdb/ipsubnet/batchdelete',
    'batch_change_page': '/cmdb/ipsubnet/batchchange'
}

@cmdb.route('/cmdb/ipsubnet',  methods=['GET', 'POST'])
@login_required
def ipsubnet():
    '''IP子网'''
    role_Permission = getattr(Permission, current_user.role)
    ipsubnet_form = IpSubnetForm()
    sidebar = copy.deepcopy(start_sidebar)
    thead = copy.deepcopy(start_thead)
    sidebar = init_sidebar(sidebar, sidebar_name,'edititem')
    search = ''
    if request.method == "POST" and \
            role_Permission >= Permission.ALTER:
        sidebar = init_sidebar(sidebar, sidebar_name,'additem')
        if ipsubnet_form.validate_on_submit():
            ipsubnet=IpSubnet(
                 subnet=ipsubnet_form.subnet.data,
                 start_ip=ipsubnet_form.start_ip.data,
                 end_ip=ipsubnet_form.end_ip.data,
                 netmask=ipsubnet_form.netmask.data,
                 site=ipsubnet_form.site.data,
                 sales=ipsubnet_form.sales.data,
                 client=ipsubnet_form.client.data,
                 start_time=ipsubnet_form.start_time.data,
                 expire_time=ipsubnet_form.expire_time.data,
                 remark=ipsubnet_form.remark.data
            )
            db.session.add(ipsubnet)
            db.session.commit()
            value = ("subnet:%s start_ip:%s end_ip:%s netmask:%s "
                     "site:%s sales:%s client:%s start_time:%s "
                     "expire_time:%s remark:%s" 
            ) % (ipsubnet.subnet, ipsubnet.start_ip, ipsubnet.end_ip,
                 ipsubnet.netmask, ipsubnet.site, ipsubnet.sales, ipsubnet.client,
                 ipsubnet.start_time, ipsubnet.expire_time, ipsubnet.remark)
            record_sql(current_user.username, u"创建", u"IP子网",
                       ipsubnet.id, "subnet", value)
            
            flash(u'IP子网添加成功')
        else:
            for key in ipsubnet_form.errors.keys():
                flash(ipsubnet_form.errors[key][0])

    if request.method == "GET":
        search = request.args.get('search', '')
        # hiddens用于分页隐藏字段处理
        checkbox = request.args.getlist('hidden') or request.args.get('hiddens', '') 
        if search:
            # 搜索
            thead = init_checkbox(thead, checkbox)
            sidebar = init_sidebar(sidebar, sidebar_name, "edititem")
            page = int(request.args.get('page', 1))
            res = search_res(IpSubnet, 'subnet', search)
            res = res.search_return()
            if res:
                pagination = res.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html', thead=thead, endpoint=endpoint, set_page=set_page, 
                    item_form=ipsubnet_form, pagination=pagination, search_value=search, 
                    sidebar=sidebar, sidebar_name=sidebar_name, items=items, checkbox=str(checkbox)
                )
    
    return render_template(
        'cmdb/item.html', item_form=ipsubnet_form,thead=thead, set_page=set_page,
        sidebar=sidebar, sidebar_name=sidebar_name, search_value=search
    )

@cmdb.route('/cmdb/ipsubnet/delete',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER)
def ipsubnet_delete():
    del_id = int(request.form["id"])
    ipsubnet = IpSubnet.query.filter_by(id=del_id).first()
    if ipsubnet:
        if IpPool.query.filter_by(subnet=ipsubnet.subnet).first():
            return u"删除失败 有IP使用这个子网"
        record_sql(current_user.username, u"删除", u"IP子网",
                   ipsubnet.id, "ipsubnet", ipsubnet.subnet)
        db.session.delete(ipsubnet)
        db.session.commit()
        return "OK"
    return u"删除失败 没有找到这个IP子网"

@cmdb.route('/cmdb/ipsubnet/change',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER)
def ipsubnet_change():
    change_id = int(request.form["id"])
    item = request.form["item"]
    value = request.form['value']
    ipsubnet = IpSubnet.query.filter_by(id=change_id).first()
    if ipsubnet:
        verify = CustomValidator(item, change_id, value)
        res = verify.validate_return()
        if res == "OK":
            record_sql(current_user.username, u"更改", u"IP子网",
                       ipsubnet.id, item, value)
            setattr(ipsubnet, item, value) 
            db.session.add(ipsubnet)
            return "OK"
        return res 
    return u"更改失败没有找到该IP子网"

@cmdb.route('/cmdb/ipsubnet/batchdelete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def ipsubnet_batch_delete():
    list_id = eval(request.form["list_id"])

    for id in list_id:
        ipsubnet = IpSubnet.query.filter_by(id=id).first()
        if ipsubnet:
            if IpPool.query.filter_by(subnet=ipsubnet.subnet).first():
                return u"删除失败 *** <b>%s</b> *** 有IP在使用" % ipsubnet.subnet
        else:
            return u"删除失败没有这些IP子网"

    for id in list_id:
        ipsubnet = IpSubnet.query.filter_by(id=id).first()
        record_sql(current_user.username, u"删除", u"IP子网",
                   ipsubnet.id, "ipsubnet", ipsubnet.subnet)
        db.session.delete(ipsubnet)
    db.session.commit()
    return "OK"

@cmdb.route('/cmdb/ipsubnet/batchchange',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def ipsubnet_batch_change():
    list_id = eval(request.form["list_id"])
    item = request.form["item"]
    value = request.form["value"]

    for id in list_id:
        ipsubnet = IpSubnet.query.filter_by(id=id).first()
        if ipsubnet:
            verify = CustomValidator(item, id, value)
            res = verify.validate_return()
            if not res == "OK":
                return res
        else:
            return u"更改失败没有找到这些IP子网"

    for id in list_id:
        ipsubnet = IpSubnet.query.filter_by(id=id).first()
        record_sql(current_user.username, u"更改", u"IP子网", ipsubnet.id, item, value)
        setattr(ipsubnet, item, value)
        db.session.add(ipsubnet)
    return "OK"
