#coding=utf-8
# 机房管理

from app.models import Site, Rack, IpSubnet

from ..same import *
from .forms import SiteForm
from .custom import CustomValidator

# 初始化参数
sidebar_name = "site"
start_thead = [
    [0, u'机房','site', False, False], [1,u'ISP', 'isp', False, True], 
    [2,u'地理位置', 'location', False, False], [3, u'地址','addresults', False, False], 
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
    role_permission = getattr(Permission, current_user.role)
    site_form = SiteForm()
    sidebar = copy.deepcopy(start_sidebar)
    thead = copy.deepcopy(start_thead)
    sidebar = init_sidebar(sidebar, sidebar_name,'edititem')
    search_value = ''
    if request.method == "POST" and \
            role_permission >= Permission.ALTER:
        sidebar = init_sidebar(sidebar, sidebar_name, "additem")
        if site_form.validate_on_submit():
            site = Site(
                site=site_form.site.data,
                isp=site_form.isp.data,
                location=site_form.location.data,
                addresults=site_form.address.data,
                contact=site_form.contact.data,
                dns=site_form.dns.data,
                remark=site_form.remark.data
            )
            add_sql = edit(current_user.username, site, "site" )
            add_sql.add()
            flash(u'机房添加成功')
        else:
            for key in site_form.errors.keys():
                flash(site_form.errors[key][0])
        
    if request.method == "GET":
        search_value = request.args.get('search', '')
        # hiddens用于分页隐藏字段处理
        checkbox = request.args.getlist('hidden') or request.args.get('hiddens', '')  
        if search_value:
            # 搜索
            thead = init_checkbox(thead, checkbox)
            sidebar = init_sidebar(sidebar, sidebar_name, "edititem")
            page = int(request.args.get('page', 1))
            result = search(Site, 'site' , search_value)
            result = result.search_return()
            if result:
                pagination = result.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html', thead=thead, endpoint=endpoint, set_page=set_page, 
                    item_form=site_form, pagination=pagination, search_value=search_value, 
                    sidebar=sidebar, sidebar_name=sidebar_name, items=items, checkbox=str(checkbox)
                )

    return render_template(
        'cmdb/item.html', item_form=site_form, thead=thead, set_page=set_page,
        sidebar=sidebar, sidebar_name=sidebar_name, search_value=search_value
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
            return u"删除失败 *** %s *** 机房有机架在使用" % site.site
        if IpSubnet.query.filter_by(site=site.site).first():
            return u"删除失败 *** %s *** 机房有IP子网在使用" % site.site
        delete_sql = edit(current_user.username, site, "site", site.site)
        delete_sql.delete()
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
        result = verify.validate_return()
        if result == "OK":
            change_sql = edit(current_user.username, site, item, value)
            change_sql.change()
            return "OK"
        return result 
    return u"更改失败没有找到该机房"

@cmdb.route('/cmdb/site/batchdelete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def site_batch_delete():
    list_id = eval(request.form["list_id"])

    for id in list_id:
        site = Site.query.filter_by(id=id).first()
        if site:
            if Rack.query.filter_by(site=site.site).first():
                return u"删除失败 *** %s *** 有机架在使用" % site.site
            if IpSubnet.query.filter_by(site=site.site).first():
                return u"删除失败 *** %s *** 有IP子网在使用" % site.site
        else:
            return u"删除失败没有这些机房"

    for id in list_id:
        site = Site.query.filter_by(id=id).first()
        delete_sql = edit(current_user.username, site, "site", site.site)
        delete_sql.delete()
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
            result = verify.validate_return()
            if not result == "OK":
                return result
        else:
            return u"更改失败没有找到这些机房"

    for id in list_id:
        site = Site.query.filter_by(id=id).first()
        change_sql = edit(current_user.username, site, item, value)
        change_sql.change()
    return "OK"
