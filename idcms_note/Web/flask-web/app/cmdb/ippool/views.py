#coding=utf-8

from app.models import IpPool, Cabinet

from ..same import *
from .forms import RackForm
from .custom import CustomValidator

sidebar_name = 'ippool'
start_thead = [
    [0, u'IP','ip', False, False], [1,u'子网掩码', 'netmask', False, True], 
    [2,u'网关地址', 'gateway', False, True], [3, u'所属子网','subnet', False, True], 
    [4, u'所属机房', 'site', False, True], [5, u'销售代表', 'sales', False, True],
    [6, u'使用用户' ,'client', False, True], [7, u'备注' ,'remark', False, True],
    [8, u'操作', 'setting', True], [9, u'批量处理', 'batch', True]
]
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
    role_permission = getattr(Permission, current_user.role)
    ippool_form = IpPoolForm()
    sidebar = copy.deepcopy(start_sidebar)
    thead = copy.deepcopy(start_thead)
    sidebar = init_sidebar(sidebar, sidebar_name,'edititem')
    search = ''
    if request.method == "POST" and \
            role_permission >= Permission.ALTER:
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
                    add_sql = edit(current_user.username, ippool, "ip" )
                    add_sql.add()
                else:
                    flash(u'添加失败 %s 已经添加, 在此IP之前的IP已经添加成功' % add_ip)
                    break
            flash(u'IP添加成功')    
        else:
            for key in ippool_form.errors.keys():
                flash(ippool_form.errors[key][0])

    if request.method == "GET":
        search = request.args.get('search', '')
        # hiddens用于分页隐藏字段处理
        checkbox = request.args.getlist('hidden') or request.args.get('hiddens', '')
        if search_value:
            # 搜索
            thead = init_checkbox(thead, checkbox)
            sidebar = init_sidebar(sidebar, sidebar_name, "edititem")
            page = int(request.args.get('page', 1))
            result = search(IpPool, 'ip', search_value)
            result = result.search_return()
            if result:
                pagination = result.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html', thead=thead, endpoint=endpoint, set_page=set_page, 
                    item_form=ippool_form, pagination=pagination, search_value=search_value,
                    sidebar=sidebar, sidebar_name=sidebar_name, items=items, checkbox=str(checkbox)
                )
    
    return render_template(
        'cmdb/item.html', item_form=ippool_form, thead=thead, set_page=set_page,
        sidebar=sidebar, sidebar_name=sidebar_name, search_value=search_value
    )

@cmdb.route('/cmdb/ippool/delete',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ALTER)
def ippool_delete():
    del_id = int(request.form["id"])
    ippool = IpPool.query.filter_by(id=del_id).first()
    if ippool:
        if Cabinet.query.filter_by(wan_ip=ippool.ip).first():
            return "删除失败 IP *** %s *** 有设备在使用" % ippool.ip
        delete_sql = edit(current_user.username, ippool, "ip", ippool.ip)
        delete_sql.delete()
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
        verify = CustomValidator(item, change_id, value)
        result = verify.validate_return()
        if result == "OK":
            change_sql = edit(current_user.username, ippool, item, value)
            change_sql.change()
            return "OK"
        return result
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
                return u"删除失败  IP*** %s *** 有设备在使用" % ippool.ip
        else:
            return u"删除失败没有这些IP"

    for id in list_id:
        ippool = IpPool.query.filter_by(id=id).first()
        delete_sql = edit(current_user.username, ippool, "ip", ippool.ip)
        delete_sql.delete()
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
            verify = CustomValidator(item, id, value)
            result = verify.validate_return()
            if not result == "OK":
                return result
        else:
            return u"更改失败没有找到这些IP"

    for id in list_id:
        ippool = IpPool.query.filter_by(id=id).first()
        change_sql = edit(current_user.username, ippool, item, value)
        change_sql.change()
    return "OK"
