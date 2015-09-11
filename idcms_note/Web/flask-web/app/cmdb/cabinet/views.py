#coding=utf-8

import os
import sys
import copy

from flask import render_template, request, flash
from flask.ext.login import login_required, current_user

from .. import cmdb
from .forms import CabinetForm
from .customvalidator import CustomValidator, ChangeCheck
from ..sidebar import start_sidebar

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app import db
from app.models import Cabinet, IpPool
from app.utils.permission import Permission, permission_validation
from app.utils.utils import search_res, record_sql, init_sidebar, init_checkbox

# 初始化参数
sidebar_name = "cabinet"
start_thead = [
    [0, u'资产编号','an', False, False], [1,u'外网IP', 'wan_ip', False, False], 
    [2,u'内网IP', 'lan_ip', False, False], [3,u'所在机房', 'site', False, False], 
    [4, u'所在机架','rack', False, True], [5,u'机架位置', 'seat', False, False],
    [6, u'设备带宽', 'bandwidth', False, True], [7, u'上联端口', 'up_link', False, True],
    [8, u'设备高度','height', False, False], [9, u'设备品牌', 'brand', False, True], 
    [10, u'设备型号', 'model', False, True], [11, u'设备SN','sn', True, False], 
    [12, u'销售代表', 'sales', False, True], [13,u'使用用户', 'client', False, True],
    [14, u'开通时间', 'start_time', True, True], [15, u'到期时间' ,'expire_time', True, True], 
    [16, u'备注' ,'remark', False, True], [17, u'操作', 'setting', True],
    [18, u'批量处理', 'batch', True] 
]
#url结尾字符
endpoint = '.cabinet'
set_page = { 
    'del_page': '/cmdb/cabinet/delete',
    'change_page': '/cmdb/cabinet/change',
    'batch_del_page': '/cmdb/cabinet/batchdelete',
    'batch_change_page': '/cmdb/cabinet/batchchange'
}

@cmdb.route('/cmdb/cabinet',  methods=['GET', 'POST'])
@login_required
def cabinet():
    '''机柜表'''
    role_Permission = getattr(Permission, current_user.role)
    cabinet_form = CabinetForm()
    sidebar = copy.deepcopy(start_sidebar)
    thead = copy.deepcopy(start_thead)
    sidebar = init_sidebar(sidebar, sidebar_name,'edititem')
    search = ''
    if request.method == "POST" and \
            role_Permission >= Permission.ALTER:
        sidebar = init_sidebar(sidebar, sidebar_name, "additem")
        if cabinet_form.validate_on_submit():
            cabinet = Cabinet(
                 an = cabinet_form.an.data,
                 wan_ip = cabinet_form.wan_ip.data,
                 lan_ip = cabinet_form.lan_ip.data,
                 site=cabinet_form.site.data,
                 rack=cabinet_form.rack.data,
                 seat=cabinet_form.seat.data,
                 bandwidth=cabinet_form.bandwidth.data,
                 up_link=cabinet_form.up_link.data,
                 height=cabinet_form.height.data,
                 brand=cabinet_form.brand.data,
                 model=cabinet_form.model.data,
                 sn=cabinet_form.sn.data,
                 sales=cabinet_form.sales.data,
                 client=cabinet_form.client.data,
                 start_time=cabinet_form.start_time.data,
                 expire_time=cabinet_form.expire_time.data,
                 remark=cabinet_form.remark.data
            )
            db.session.add(cabinet)
            db.session.commit()
            if cabinet_form.wan_ip.data:
                ip = IpPool.query.filter_by(ip=cabinet_form.wan_ip.data).first()
                record_sql(current_user.username, u"更改", u"IP池", ip.id, 
                           'sales', cabinet_form.sales.data)
                record_sql(current_user.username, u"更改", u"IP池", ip.id, 
                           'client', cabinet_form.client.data)
                ip.sales = cabinet_form.sales.data
                ip.client = cabinet_form.client.data
                db.session.add(ip)

            value = ("an:%s wan_ip:%s lan_ip:%s site:%s rack:%s seat:%s "
                    "bandwidth:%s up_link:%s height:%s brand:%s model:%s "
                    "sn:%s sales:%s client:%s start_time:%s expire_time:%s remark:%s"
            ) % (cabinet.an, cabinet.wan_ip, cabinet.lan_ip, cabinet.site, 
                 cabinet.rack, cabinet.seat, cabinet.bandwidth, cabinet.up_link,
                 cabinet.height, cabinet.brand, cabinet.model, cabinet.sn,
                 cabinet.sales, cabinet.client, cabinet.start_time, cabinet.expire_time,
                 cabinet.remark)
            record_sql(current_user.username, u"创建", u"机柜表", cabinet.id, "an", value)

            flash(u'设备添加成功')
        else:
            for key in cabinet_form.errors.keys():
                flash(cabinet_form.errors[key][0])

    if request.method == "GET":
        search = request.args.get('search', '')
        # hiddens用于分页隐藏字段处理
        checkbox = request.args.getlist('hidden') or request.args.get('hiddens', '') 
        if search:
            # 搜索
            thead = init_checkbox(thead, checkbox)
            sidebar = init_sidebar(sidebar, sidebar_name, "edititem")
            page = int(request.args.get('page', 1))
            res = search_res(Cabinet, 'an', search)
            res = res.search_return()
            if res:
                pagination = res.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html', thead=thead, endpoint=endpoint, set_page=set_page,
                    item_form=cabinet_form, pagination=pagination, sidebar=sidebar, 
                    sidebar_name=sidebar_name, search_value=search, items=items, checkbox=str(checkbox)
                )
    
    return render_template(
        'cmdb/item.html', item_form=cabinet_form,thead=thead, set_page=set_page,
        sidebar=sidebar, sidebar_name=sidebar_name, search_value=search
    )

@cmdb.route('/cmdb/cabinet/delete',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER)
def cabinet_delete():
    del_id = int(request.form["id"])
    cabinet = Cabinet.query.filter_by(id=del_id).first()
    if cabinet:
        if cabinet.wan_ip:
            change_ip = IpPool.query.filter_by(ip=cabinet.wan_ip).first()
            record_sql(current_user.username, u"更改", u"IP池", change_ip.id, 
                       'sales', '')
            record_sql(current_user.username, u"更改", u"IP池", change_ip.id,
                       'client', '')
            change_ip.sales = ''
            change_ip.client = ''
            db.session.add(change_ip)
        record_sql(current_user.username, u"删除", u"机柜表", cabinet.id, "an", cabinet.an)
        db.session.delete(cabinet)
        db.session.commit()
        return "OK"
    return u"删除失败没有找到这个设备"


@cmdb.route('/cmdb/cabinet/change',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER)
def cabinet_change():
    change_id = int(request.form["id"])
    item = request.form["item"]
    value = request.form['value']
    cabinet = Cabinet.query.filter_by(id=change_id).first()
    if cabinet:
        verify = CustomValidator(item, change_id, value)
        res = verify.validate_return()
        if res == "OK":
           change = ChangeCheck(item, value, cabinet)
           change.change_run()
           return "OK"
        return res
    return u"更改失败没有找到该设备"

@cmdb.route('/cmdb/cabinet/batchdelete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def cabinet_batch_delete():
    list_id = eval(request.form["list_id"])

    for id in list_id:
        cabinet = Cabinet.query.filter_by(id=id).first()
        if not cabinet:
            return u"删除失败没有这些设备"

    for id in list_id:
        cabinet = Cabinet.query.filter_by(id=id).first()
        if cabinet.wan_ip:
            change_ip = IpPool.query.filter_by(ip=cabinet.wan_ip).first()
            record_sql(current_user.username, u"更改", u"IP池", change_ip.id,
                       'sales', '')
            record_sql(current_user.username, u"更改", u"IP池", change_ip.id,
                       'client', '')
            change_ip.sales = ''
            change_ip.client = ''
            db.session.add(change_ip)
        record_sql(current_user.username, u"删除", u"机柜表", cabinet.id, "an", cabinet.an)
        db.session.delete(cabinet)
    db.session.commit()
    return "OK"

@cmdb.route('/cmdb/cabinet/batchchange',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def cabinet_batch_change():
    list_id = eval(request.form["list_id"])
    item = request.form["item"]
    value = request.form["value"]

    for id in list_id:
        cabinet = Cabinet.query.filter_by(id=id).first()
        if cabinet:
            verify = CustomValidator(item, id, value)
            res = verify.validate_return()
            if not res == "OK":
                return res
        else:
            return u"更改失败没有找到这些设备"

    for id in list_id:
        cabinet = Cabinet.query.filter_by(id=id).first()
        change = ChangeCheck(item, value, cabinet)
        change.change_run()
    return "OK"
