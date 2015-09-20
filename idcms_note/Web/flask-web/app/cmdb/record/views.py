#coding=utf-8
# 操作记录 

from app.models import Record

from ..same import *

sidebar_name = 'record'
start_thead = [
    [0, u'用户', '', False], [1,u'状态', '', False], [2,u'更改项目', '',  False],
    [3, u'更改ID','', False], [4, u'更改字段', '', False], [5, u'更改内容', '', False],
    [6, u'更改时间', '',False]
]
endpoint = '.record'

@cmdb.route('/cmdb/record',  methods=['GET'])
@login_required
@permission_validation(Permission.ALTER)
def record():
    sidebar = copy.deepcopy(start_sidebar)
    thead = copy.deepcopy(start_thead)
    search_value = request.args.get('search', '')
    checkbox = request.args.getlist('hidden') or request.args.get('hiddens', '')
    sidebar = init_sidebar(sidebar, sidebar_name,'edititem')
    
    if search_value:
        page = int(request.args.get('page', 1))
        result = search(Record, 'username' , search_value)
        result = result.search_return()
        if result:
            thead = init_checkbox(thead, checkbox)
            pagination = result.paginate(page, 100, False)
            items = pagination.items
            return render_template(
                'cmdb/record.html', thead=thead, endpoint=endpoint,
                pagination=pagination, search_value=search_value, sidebar=sidebar,
                items=items, checkbox=str(checkbox)
            )

    return render_template('cmdb/record.html', thead=thead, sidebar=sidebar, 
                           search_value=search_value)
