#coding=utf-8

import os
import sys
import copy

from flask import render_template, request, flash
from flask.ext.login import login_required, current_user

from .. import cmdb
from .forms import CabinetForm
from .customvalidator import CustomValidator
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
    [0, u'资产编号','an', False], [1,u'外网IP', 'wan_ip', False], [2,u'内网IP', 'lan_ip', False],
    [3,u'所在机房', 'site', False], [4, u'所在机架','rack', False], [5,u'机架位置', 'seat', False],
    [6, u'设备带宽', 'bandwidth', False], [7, u'上联端口', 'up_link', False],[8, u'设备高度','height', False], 
    [9, u'设备品牌', 'brand', False], [10, u'设备型号', 'model', False],[11, u'设备SN','sn', False], 
    [12, u'销售代表', 'sales', False], [13,u'使用用户', 'client', False],[14, u'开通时间', 'start_time', False],
    [15, u'到期时间' ,'expire_time', False], [16, u'备注' ,'remark', False], [17, u'操作', 'setting', False]
    
]
#url结尾字符
endpoint = '.cabinet'
del_page = '/cmdb/cabinet/delete'
change_page= '/cmdb/cabinet/change'

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
            role_Permission >= Permission.ALTER_REPLY:
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
                ip.client = cabinet_form.client.data
                db.session.add(ip)

            value = ("an:%s wan_ip:%s lan_ip:%s site:%s rack:%s seat:%s"
                    "bandwidth:%s up_link:%s height:%s brand:%s model:%s"
                    "sn:%s sales:%s client:%s start_time:%s expire_time%s remark:%s"
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
        checkbox = request.args.getlist('hidden')
        thead = init_checkbox(thead, checkbox)
        if search:
            # 搜索
            sidebar = init_sidebar(sidebar, sidebar_name, "edititem")
            page = int(request.args.get('page', 1))
            res = search_res(Cabinet, 'an', search)
            res = res.search_return()
            if res:
                pagination = res.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html', thead=thead, endpoint=endpoint, 
                    del_page=del_page, change_page=change_page, item_form=cabinet_form, 
                    pagination=pagination, sidebar=sidebar, sidebar_name=sidebar_name, search_value=search, 
                    items=items
                )
    
    return render_template(
        'cmdb/item.html', item_form=cabinet_form,thead=thead,
        sidebar=sidebar, sidebar_name=sidebar_name, search_value=search
    )

@cmdb.route('/cmdb/cabinet/delete',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER_REPLY)
def cabinet_delete():
    del_id = int(request.form["id"])
    cabinet = Cabinet.query.filter_by(id=del_id).first()
    if cabinet:
        if cabinet.wan_ip:
            change_ip = IpPool.query.filter_by(ip=cabinet.wan_ip).first()
            change_ip.client=''
            db.session.add(change_ip)
        record_sql(current_user.username, u"删除", u"机柜表", cabinet.id, "an", cabinet.an)
        db.session.delete(cabinet)
        db.session.commit()
        return "OK"
    return u"删除失败没有找到这个设备"

@cmdb.route('/cmdb/cabinet/change',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER_REPLY)
def cabinet_change():
    change_id = int(request.form["id"])
    item = request.form["item"]
    value = request.form['value']
    cabinet = Cabinet.query.filter_by(id=change_id).first()
    if cabinet:
        verify = CustomValidator(item, change_id, value)
        res = verify.validate_return()
        if res == "OK":
            if item == "wan_ip":
                if cabinet.wan_ip:
                    old_ip = IpPool.query.filter_by(ip=cabinet.wan_ip).first()
                    old_ip.client=""
                    db.session.add(old_ip)
                add_ip = IpPool.query.filter_by(ip=value).first()
                add_ip.client = cabinet.client
                db.session.add(add_ip)
            record_sql(current_user.username, u"更改", u"机柜表",
                       cabinet.id, item, value)
            setattr(cabinet, item, value) 
            db.session.add(cabinet)
            return "OK"
        return res
    return u"更改失败没有找到该用户"
