#coding=utf-8

import os
import sys

from flask import render_template, request, flash
from flask.ext.login import login_required, current_user

from .. import cmdb
from .forms import IpPoolForm
from .customvalidator import CustomValidator

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app import db
from app.models import IpPool, Cabinet
from app.utils.permission import Permission, permission_validation
from app.utils.searchutils import search_res

# 初始化参数
titles = {'path':'/cmdb/iprange', 'title':u'IDCMS-CMDB-IP子网管理'}
thead = [
    [0, u'IP','ip'], [1,u'子网掩码', 'netmask'], [2,u'网关地址', 'gateway'],
    [3, u'所属子网','subnet'], [4, u'所属机房', 'site'], [5, u'使用用户' ,'client'],
    [6, u'备注' ,'remark']
]
# url分页地址函数
endpoint = '.ippool'
del_page = '/cmdb/ippool/delete'
change_page= '/cmdb/ippool/change'

def init__sidebar(sidebar_class):
    sidebarclass = {
        'edititem':['', 'content hide', u'管理IP池'],
        'additem':['', 'content hide', u'添加IP']
    }
    sidebarclass[sidebar_class][0] = 'active' 
    sidebarclass[sidebar_class][1] = 'content'
    return sidebarclass

@cmdb.route('/cmdb/ippool',  methods=['GET', 'POST'])
@login_required
def ippool():
    '''IP池'''
    role_Permission = getattr(Permission, current_user.role)
    ippool_form = IpPoolForm()
    sidebarclass = init__sidebar('edititem')
    if request.method == "POST" and \
            role_Permission >= Permission.ALTER_REPLY:
        sidebarclass = init__sidebar('additem')
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
                        client=ippool_form.client.data,
                        remark=ippool_form.remark.data
                    )
                    db.session.add(ippool)
                    flash(u'IP添加成功')
                else:
                    flash(u'添加失败 %s 已经添加' % add_ip)
                    break
             
        else:
            for key in ippool_form.errors.keys():
                flash(ippool_form.errors[key][0])

    if request.method == "GET":
        search = request.args.get('search', '')
        if search:
            # 搜索
            page = int(request.args.get('page', 1))
            sidebarclass = init__sidebar('edititem')
            res = search_res(IpPool, 'ip', search)
            if res:
                pagination = res.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html', titles=titles, thead=thead, 
                    endpoint=endpoint, del_page=del_page, change_page=change_page,
                    item_form=ippool_form, sidebarclass=sidebarclass, pagination=pagination,
                    search_value=search, items=items
                )
    
    return render_template(
        'cmdb/item.html', titles = titles, item_form=ippool_form, sidebarclass=sidebarclass
    )

@cmdb.route('/cmdb/ippool/delete',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER_REPLY)
def ippool_delete():
    del_id = int(request.form["id"])
    ippool = IpPool.query.filter_by(id=del_id).first()
    if ippool:
        if Cabinet.query.filter_by(wan_ip=ippool.ip).first():
            return "删除失败 这个IP有设备在使用"
        db.session.delete(ippool)
        db.session.commit()
        return "OK"
    return u"删除失败没有找到这个IP子网"

@cmdb.route('/cmdb/ippool/change',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER_REPLY)
def ippool_change():
    change_id = int(request.form["id"])
    item = request.form["item"]
    value = request.form['value']
    ippool = IpPool.query.filter_by(id=change_id).first()
    if ippool:
        verify = CustomValidator(item, value)
        res = verify.validate_return()
        if res == "OK":
            setattr(ippool, item, value) 
            db.session.add(ippool)
            return "OK"
        return res 
    return u"更改失败没有找到该用户"
