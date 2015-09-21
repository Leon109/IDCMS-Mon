#coding=utf-8

from ..same import *

sidebar_name = 'help'

@cmdb.route('/cmdb/help',  methods=['GET'])
@login_required
def help():
    '''帮助'''
    sidebar = copy.deepcopy(start_sidebar)
    sidebar = init_sidebar(sidebar, sidebar_name,'usage')
    return render_template('cmdb/help.html', sidebar=sidebar)
