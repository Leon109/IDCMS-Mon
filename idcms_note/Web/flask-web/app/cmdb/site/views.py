#coding=utf-8

import os
import sys

from flask import render_template, redirect, request, flash
from flask.ext.login import login_required, current_user

from .. import cmdb
from .forms import SiteForm
from .customvalidator import CustomValidator

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app import db
from app.models import  Site
from app.utils.permission import Permission, permission_validation

titles = {'path':'/cmdb/site', 'title':u'IDCMS-CMDB-机房'}
thead = [[0, u'机房','site'], [1,u'ISP', 'isp'], [2,u'地理位置', 'location'],
    [3, u'地址','address'], [4, u'联系方式', 'contact'], [5, u'备注' ,'remark']
    ]
del_page = '/cmdb/site/delete'
change_page= '/cmdb/site/change'


def init__sidebar(sidebar_class):
    sidebarclass = {
        'editsite':['', 'content hide'],
        'addsite':['', 'content hide']
    }
    sidebarclass[sidebar_class] = ['active', 'content ']
    return sidebarclass



@cmdb.route('/cmdb/site',  methods=['GET', 'POST'])
@login_required
def site():
    '''机房设置'''
    role_Permission = getattr(Permission, current_user.role)
    site_form = SiteForm()
    sidebarclass = init__sidebar('editsite')
    if request.method == "POST" and \
            role_Permission >= Permission.ALTER_REPLY:
        sidebarclass = init__sidebar('addsite')
        if site_form.validate_on_submit():
            site = Site(site=site_form.site.data,
                isp=site_form.isp.data,
                location=site_form.location.data,
                address=site_form.address.data,
                contact=site_form.contact.data,
                remark=site_form.remark.data)
            db.session.add(site)
            flash(u'机房添加成功')
        else:
            for key in site_form.errors.keys():
                flash(site_form.errors[key][0])

    if request.method == "GET":
        search = request.args.get('search', '')
        if search:
            # 搜索
            page = int(request.args.get('page', 1))
            sidebarclass = init__sidebar('editsite')
            try:
                option = {docm.split("==")[0]:docm.split("==")[1] for docm in search.split()}
                if option:
                    for key in option.keys():
                        # 第一次进行初始查询，后面的开始从上一次的基础上进行过滤
                        if key == option.keys()[0]:
                            res = Site.query.filter(getattr(Site,key).endswith(option[key]))
                        res = res.filter(getattr(Site,key).endswith(option[key]))
            # 如果不是多重搜索
            except IndexError:
                if search == "ALL":
                    res = Site.query
                else:
                    res = Site.query.filter(Site.site.endswith(search))
            # 如果搜索的项目发生错误
            except AttributeError:
                res = None
            if res:
                pagination = res.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/site.html',
                    titles=titles,
                    thead=thead,
                    del_page=del_page,
                    change_page=change_page,
                    site_form=site_form,
                    sidebarclass=sidebarclass,
                    pagination=pagination,
                    search_value=search,
                    items=items,
                )
    return render_template(
        'cmdb/site.html',
        titles = titles,
        thead=thead,
        del_page=del_page,
        change_page=change_page,
        site_form=site_form,
        sidebarclass=sidebarclass
    )

@cmdb.route('/cmdb/site/delete',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER_REPLY)
def delete():
    del_id = int(request.form["id"])
    user = Site.query.filter_by(id=del_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return "OK"
    return u"删除失败没有找到这个机房"

@cmdb.route('/cmdb/site/change',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER_REPLY)
def change():
    change_id = int(request.form["id"])
    item = request.form["item"]
    value = request.form['value']
    user = Site.query.filter_by(id=change_id).first()
    if user:
        verify = CustomValidator(item,value)
        res = verify.validata_return()
        if res == "OK":
            setattr(user, item, value) 
            db.session.add(user)
            return "OK"
        return res 
    return u"更改失败没有找到该用户"
