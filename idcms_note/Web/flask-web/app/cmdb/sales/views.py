#coding=utf-8
# 销售管理

from app.models import Sales, Rack, IpSubnet, IpPool, Cabinet

from ..same import *
from .forms import SalesForm
from .custom import CustomValidator

# 初始化参数

# 这个模块对应的侧边栏名称
sidebar_name = 'sales'

# 用于搜索显示
# 列表 0 表位置  1 显示名 2 数据库字段 3 初始化True是隐藏 False是隐藏 4 批量搜索是否能够更改
start_thead = [
    [0, u'销售','username', False, False], [1, u'联系方式', 'contact', False, False], 
    [2, u'备注' ,'remark', False, True], [3, u'操作', 'setting', True],
    [4, u'批量处理', 'batch', True]
]

# url分页地址函数
endpoint = '.sales'

# 删除修改页面
set_page = {
    'del_page': '/cmdb/sales/delete',
    'change_page': '/cmdb/sales/change',
    'batch_del_page': '/cmdb/sales/batchdelete',
    'batch_change_page': '/cmdb/sales/batchchange'
}

# 删除时需要检查的项目
check_item = [(Rack, u'机架'), (IpSubnet, u'IP子网'), (IpPool, u'IP池'), 
              (Cabinet, u'机柜表')]

@cmdb.route('/cmdb/sales',  methods=['GET', 'POST'])
@login_required
def sales():
    '''销售管理'''
    role_permission = getattr(Permission, current_user.role)
    sales_form = SalesForm()
    # 深拷贝，避免更改后相互影响
    sidebar = copy.deepcopy(start_sidebar)
    thead = copy.deepcopy(start_thead)
    # 默认显示页面
    sidebar = init_sidebar(sidebar, sidebar_name, 'edititem')
    # 默认搜索栏内容
    search_value = ''
    # 添加
    if request.method == "POST" and role_permission >= Permission.ALTER:
        sidebar = init_sidebar(sidebar, sidebar_name, "additem")
        if sales_form.validate_on_submit():
            sales = Sales(
                username=sales_form.username.data,
                contact=sales_form.contact.data,
                remark=sales_form.remark.data
            )
            # edit 方法处理增 删 改
            add_sql = edit(current_user.username, sales, "sales" )
            add_sql.add()
            flash(u'销售 *** %s *** 添加成功' % sales_form.username.data)
        else:
            # 提示错误信息
            for thead in start_thead:
                key = thead[2]
                if ipsubnet_form.errors.get(key, None):
                    flash(ipsubnet_form.errors[key][0])
                    break
    # 查询    
    if request.method == "GET":
        search_value = request.args.get('search', '')
        # 获取前台选择框 hiddens用于分页隐藏字段处理
        checkbox = request.args.getlist('hidden') or request.args.get('hiddens', '') 
        if search_value:
            sidebar = init_sidebar(sidebar, sidebar_name, "edititem")
            thead = init_checkbox(thead, checkbox)
            page = int(request.args.get('page', 1))
            # search 方法处理搜索
            result = search(Sales, 'username' , search_value)
            result = result.search_return()
            if result:
                # 100 是默认页面显示数量
                pagination = result.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html', thead=thead, endpoint=endpoint, set_page=set_page,
                    item_form=sales_form, sidebar=sidebar, sidebar_name=sidebar_name,
                    pagination=pagination, search_value=search_value, items=items, checkbox=str(checkbox)
                )
    return render_template(
        'cmdb/item.html', item_form=sales_form, thead=thead, set_page=set_page,
        sidebar=sidebar, sidebar_name=sidebar_name, search_value=search_value
    )

# 删除
@cmdb.route('/cmdb/sales/delete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def sales_delete():
    del_id = int(request.form["id"])
    sales = Sales.query.filter_by(id=del_id).first()
    if sales:
        for item in check_item:
            if getattr(item[0],'query').filter_by(sales=sales.username).first():
                return u"删除失败 *** %s *** 有%s在使用" % (sales.username, item[1])
        delete_sql = edit(current_user.username, sales, "sales", sales.username)
        delete_sql.delete()
        return "OK"
    return u"删除失败 没有找到这个销售"

# 修改
@cmdb.route('/cmdb/sales/change',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def sales_change():
    change_id = int(request.form["id"])
    item = request.form["item"]
    value = request.form["value"]
    sales = Sales.query.filter_by(id=change_id).first()
    if sales:
        verify = CustomValidator(item, change_id, value)
        result = verify.validate_return()
        if result == "OK":
            change_sql = edit(current_user.username, sales, item, value)
            change_sql.change()
            return "OK"
        return result 
    return u"更改失败 没有找到这个销售"

# 批量删除
@cmdb.route('/cmdb/sales/batchdelete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def sales_batch_delete():
    list_id = eval(request.form["list_id"])

    for id in list_id:
        sales = Sales.query.filter_by(id=id).first()
        if sales:
            for item in check_item:
                if getattr(item[0],'query').filter_by(sales=sales.username).first():
                    return u"删除失败，*** %s *** 有%s在使用" % (sales.username, item[1])
        else:
            return u"删除失败 没有找到这些销售"

    for id in list_id:
        sales = Sales.query.filter_by(id=id).first()
        delete_sql = edit(current_user.username, sales, "sales", sales.username)
        delete_sql.delete()
    return "OK"

# 批量修改
@cmdb.route('/cmdb/sales/batchchange',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def sales_batch_change():
    list_id = eval(request.form["list_id"])
    item = request.form["item"]
    value = request.form["value"]
    
    for id in list_id:
        sales = Sales.query.filter_by(id=id).first()
        if sales:
            verify = CustomValidator(item, id, value)
            result = verify.validate_return()
            if not result == "OK":
                return result
        else:
            return u"更改失败 没有找到这些销售"

    for id in list_id:
        sales = Sales.query.filter_by(id=id).first()
        change_sql = edit(current_user.username, sales, item, value)
        change_sql.change()
    return "OK"
