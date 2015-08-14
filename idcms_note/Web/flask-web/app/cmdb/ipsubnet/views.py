#coding=utf-8

import os
import sys

from flask import render_template, request, flash
from flask.ext.login import login_required, current_user

from .. import cmdb
from .forms import IpSubnetForm
from .customvalidator import CustomValidator

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app import db
from app.models import IpSubnet, IpPool
from app.utils.permission import Permission, permission_validation
from app.utils.searchutils import search_res
from app.utils.record import record_sql

# 初始化参数
titles = {'path':'/cmdb/ipsubnet', 'title':u'IDCMS-CMDB-IP子网管理'}
thead = [
    [0, u'IP子网','subnet'], [1,u'起始IP', 'start_ip'], [2,u'结束IP', 'end_ip'],
    [3, u'子网掩码','netmask'], [4, u'所属机房', 'site'], [5, u'销售代表', 'sales'], 
    [6, u'使用用户', 'client'], [7, u'开通时间' ,'start_time'], [8, u'到期时间' ,'expire_time'],
    [9, u'备注' ,'remark']
]
# url分页地址函数
endpoint = '.ipsubnet'
del_page = '/cmdb/ipsubnet/delete'
change_page= '/cmdb/ipsubnet/change'

def init__sidebar(sidebar_class):
    sidebarclass = {
        'edititem':['', 'content hidden', u'管理IP子网'],
        'additem':['', 'content hidden', u'添加IP子网']
    }
    sidebarclass[sidebar_class][0] = 'active' 
    sidebarclass[sidebar_class][1] = 'content'
    return sidebarclass

@cmdb.route('/cmdb/ipsubnet',  methods=['GET', 'POST'])
@login_required
def ipsubnet():
    '''IP子网'''
    role_Permission = getattr(Permission, current_user.role)
    ipsubnet_form = IpSubnetForm()
    sidebarclass = init__sidebar('edititem')
    if request.method == "POST" and \
            role_Permission >= Permission.ALTER_REPLY:
        sidebarclass = init__sidebar('additem')
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
            value = ("subnet:%s start_ip:%s end_ip:%s netmask:%s"
                     "site:%s sales:%s client:%s start_time:%s"
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
        if search:
            # 搜索
            page = int(request.args.get('page', 1))
            sidebarclass = init__sidebar('edititem')
            res = search_res(IpSubnet, 'subnet', search)
            if res:
                pagination = res.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html', titles=titles, thead=thead, 
                    endpoint=endpoint, del_page=del_page, change_page=change_page,
                    item_form=ipsubnet_form, sidebarclass=sidebarclass, pagination=pagination,
                    search_value=search, items=items
                )
    
    return render_template(
        'cmdb/item.html', titles = titles, item_form=ipsubnet_form,
        sidebarclass=sidebarclass
    )

@cmdb.route('/cmdb/ipsubnet/delete',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER_REPLY)
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
    return u"删除失败 没有找到这个IP范围"

@cmdb.route('/cmdb/ipsubnet/change',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER_REPLY)
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
    return u"更改失败没有找到该用户"
