#coding=utf-8

import os
import sys

from flask import render_template, request, flash
from flask.ext.login import login_required, current_user

from .. import cmdb
from .forms import CabinetForm
from .customvalidator import CustomValidator

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app import db
from app.models import Cabinet, IpPool
from app.utils.permission import Permission, permission_validation
from app.utils.searchutils import search_res

# 初始化参数
titles = {'path':'/cmdb/cabinet', 'title':u'IDCMS-CMDB-机柜表'}
thead = [
    [0, u'资产编号','an'], [1,u'外网IP', 'wan_ip'], [2,u'内网IP', 'lan_ip'],
    [3,u'所在机房', 'site'], [4, u'所在机架','rack'], [5,u'机架位置', 'seat'],
    [6, u'设备带宽', 'bandwidth'], [7, u'上联端口', 'up_link'],[8, u'设备高度','height'], 
    [9, u'设备品牌', 'brand'], [10, u'设备型号', 'model'],[11, u'设备SN','sn'], 
    [12, u'销售代表', 'salesman'], [13,u'使用用户', 'clinet'],[14, u'开通时间', 'start_time'],
    [15, u'到期时间' ,'expire_time'], [16, u'备注' ,'remark']
]
#url结尾字符
endpoint = '.cabinet'
del_page = '/cmdb/cabinet/delete'
change_page= '/cmdb/cabinet/change'

def init__sidebar(sidebar_class):
    sidebarclass = {
        'edititem':['', 'content hide', u'管理设备'],
        'additem':['', 'content hide', u'添加设备']
    }
    sidebarclass[sidebar_class][0] = 'active' 
    sidebarclass[sidebar_class][1] = 'content'
    return sidebarclass

@cmdb.route('/cmdb/cabinet',  methods=['GET', 'POST'])
@login_required
def cabinet():
    '''机柜表'''
    role_Permission = getattr(Permission, current_user.role)
    cabinet_form = CabinetForm()
    sidebarclass = init__sidebar('edititem')
    if request.method == "POST" and \
            role_Permission >= Permission.ALTER_REPLY:
        sidebarclass = init__sidebar('additem')
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
                 salesman=cabinet_form.salesman.data,
                 client=cabinet_form.client.data,
                 start_time=cabinet_form.start_time.data,
                 expire_time=cabinet_form.expire_time.data,
                 remark=cabinet_form.remark.data
            )
            db.session.add(cabinet)
            if cabinet_form.wan_ip.data:
                ip = IpPool.query.filter_by(ip=cabinet_form.wan_ip.data).first()
                ip.client = cabinet_form.client.data
                db.session.add(ip)
            flash(u'设备添加成功')
        else:
            for key in cabinet_form.errors.keys():
                flash(cabinet_form.errors[key][0])

    if request.method == "GET":
        search = request.args.get('search', '')
        if search:
            # 搜索
            page = int(request.args.get('page', 1))
            sidebarclass = init__sidebar('edititem')
            res = search_res(Cabinet, 'an', search)
            if res:
                pagination = res.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html', titles=titles, thead=thead, 
                    endpoint=endpoint, del_page=del_page, change_page=change_page,
                    item_form=cabinet_form, sidebarclass=sidebarclass, pagination=pagination,
                    search_value=search, items=items
                )
    
    return render_template(
        'cmdb/item.html', titles = titles, item_form=cabinet_form,
        sidebarclass=sidebarclass
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
            setattr(cabinet, item, value) 
            db.session.add(cabinet)
            return "OK"
        return res
    return u"更改失败没有找到该用户"
