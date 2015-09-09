#coding=utf-8

import os
import sys
import copy

from flask import render_template, request, flash
from flask.ext.login import login_required, current_user

from .. import cmdb
from .forms import SiteForm
from .customvalidator import CustomValidator
from ..sidebar import start_sidebar

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app import db
from app.models import Site, Rack, IpSubnet
from app.utils.permission import Permission, permission_validation
from app.utils.utils import search_res, record_sql, init_sidebar, init_checkbox


# 初始化参数
sidebar_name = "site"
start_thead = [
    [0, u'机房','site', False, False], [1,u'ISP', 'isp', False, True], 
    [2,u'地理位置', 'location', False, False], [3, u'地址','address', False, False], 
    [4, u'联系方式', 'contact', False, True], [5, u'机房DNS', 'dns', False, True], 
    [6, u'备注' ,'remark', False, True], [7, u'操作', 'setting', True],
    [8, u'批量处理', 'batch', True]
]
# url分页地址函数
endpoint = '.site'
#处理修改页面
set_page = { 
    'del_page':  '/cmdb/site/delete',
    'change_page':  '/cmdb/site/change',
    'batch_del_page': '/cmdb/site/batchdelete',
    'batch_change_page': '/cmdb/site/batchchange'
}

@cmdb.route('/cmdb/site',  methods=['GET', 'POST'])
@login_required
def site():
    '''机房设置'''
    role_Permission = getattr(Permission, current_user.role)
    site_form = SiteForm()
    sidebar = copy.deepcopy(start_sidebar)
    thead = copy.deepcopy(start_thead)
    sidebar = init_sidebar(sidebar, sidebar_name,'edititem')
    search = ''
    if request.method == "POST" and \
            role_Permission >= Permission.ALTER:
        sidebar = init_sidebar(sidebar, sidebar_name, "additem")
        if site_form.validate_on_submit():
            site = Site(
                site=site_form.site.data,
                isp=site_form.isp.data,
                location=site_form.location.data,
                address=site_form.address.data,
                contact=site_form.contact.data,
                dns=site_form.dns.data,
                remark=site_form.remark.data
            )
            db.session.add(site)
            db.session.commit()
            value = (
                "site:%s isp:%s location:%s address:%s "
                "contact:%s  dns:%s remark:%s"
            ) % (site.site, site.isp, site.location, 
                 site.address, site.contact, site.dns, site.remark)
            record_sql(current_user.username, u"创建", u"机房",
                       site.id, "site", value)
            flash(u'机房添加成功')
        else:
            for key in site_form.errors.keys():
                flash(site_form.errors[key][0])
        
    if request.method == "GET":
        search = request.args.get('search', '')
        # hiddens用于分页隐藏字段处理
        checkbox = request.args.getlist('hidden') or request.args.get('hiddens', '')  
        if search:
            # 搜索
            thead = init_checkbox(thead, checkbox)
            sidebar = init_sidebar(sidebar, sidebar_name, "edititem")
            page = int(request.args.get('page', 1))
            res = search_res(Site, 'site' , search)
            res = res.search_return()
            if res:
                pagination = res.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html', thead=thead, endpoint=endpoint, set_page=set_page, 
                    item_form=site_form, pagination=pagination, search_value=search, 
                    sidebar=sidebar, sidebar_name=sidebar_name, items=items, checkbox=str(checkbox)
                )

    return render_template(
        'cmdb/item.html', item_form=site_form, thead=thead, set_page=set_page,
        sidebar=sidebar, sidebar_name=sidebar_name, search_value=search
    )

@cmdb.route('/cmdb/site/delete',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER)
def site_delete():
    del_id = int(request.form["id"])
    site = Site.query.filter_by(id=del_id).first()
    if site:
        # 删除机房只需要检查机架和IP子网就好，机架会检查机柜表
        # 子网会检查IP 所有只要这两个没有使用就可以删除
        if Rack.query.filter_by(site=site.site).first():
            return u"删除失败 这个机房有机架在使用"
        if IpSubnet.query.filter_by(site=site.site).first():
            return u"删除失败 这个机房有IP子网在使用"
        record_sql(current_user.username, u"删除", u"机房",
                   site.id, "site", site.site)
        db.session.delete(site)
        db.session.commit()
        return "OK"
    return u"删除失败 没有找到这个机房"

@cmdb.route('/cmdb/site/change',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER)
def site_change():
    change_id = int(request.form["id"])
    item = request.form["item"]
    value = request.form["value"]
    site = Site.query.filter_by(id=change_id).first()
    if site:
        verify = CustomValidator(item, change_id, value)
        res = verify.validate_return()
        if res == "OK":
            record_sql(current_user.username, u"更改", u"机房",
                        site.id, item, value)
            setattr(site, item, value) 
            db.session.add(site)
            return "OK"
        return res 
    return u"更改失败没有找到该用户"

@cmdb.route('/cmdb/site/batchdelete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def site_batch_delete():
    list_id = eval(request.form["list_id"])

    for id in list_id:
        site = Site.query.filter_by(id=id).first()
        if site:
            if Rack.query.filter_by(site=site.site).first():
                return u"删除失败 *** <b>%s</b> *** 有机架在使用" % site.site
            if IpSubnet.query.filter_by(site=site.site).first():
                return u"删除失败 *** <b>%s</b> *** 有IP子网在使用" % site.site
        else:
            return u"删除失败没有这些机房"

    for id in list_id:
        site = Site.query.filter_by(id=id).first()
        record_sql(current_user.username, u"删除", u"机房", site.id, "site", site.site)
        db.session.delete(site)
    db.session.commit()
    return "OK"

@cmdb.route('/cmdb/site/batchchange',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def site_batch_change():
    list_id = eval(request.form["list_id"])
    item = request.form["item"]
    value = request.form["value"]

    for id in list_id:
        site = Site.query.filter_by(id=id).first()
        if site:
            verify = CustomValidator(item, id, value)
            res = verify.validate_return()
            if not res == "OK":
                return res
        else:
            return u"更改失败没有找到这些机房"

    for id in list_id:
        site = Site.query.filter_by(id=id).first()
        record_sql(current_user.username, u"更改", u"机房", site.id, item, value)
        setattr(site, item, value)
        db.session.add(site)
    return "OK"
