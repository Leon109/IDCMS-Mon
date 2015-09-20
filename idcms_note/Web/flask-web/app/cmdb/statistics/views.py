#coding=utf-8

from flask import jsonify

from app.models import Site, Rack, Client, Sales, Cabinet

from ..same import *

# 初始化函数
sidebar_name = "statistics"

def ehart_init():
    echart = {
        "graph": None,
        "option": {
            'title': {}, 'tooltip': {},
            'toolbox': {
                'show': True,
                'feature': {
                    'mark': {'show': True}, 'resulttore': {'show': True},
                    'saveAsImage': {'show': True}
                    }
            },
            'calculable': True, 'series': []
        }  
    }
    return echart

@cmdb.route('/cmdb/statistics',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ADMIN, Permission.ADVANCED_QUERY)
def statistics():
    sidebar = copy.deepcopy(start_sidebar)
    sidebar = init_sidebar(sidebar, sidebar_name,'base')
    all_site = Site.query.all()
    return render_template('/cmdb/statistics.html', sidebar=sidebar, sidebar_name=sidebar_name, all_site=all_site)

@cmdb.route('/cmdb/statistics/base_info',  methods=['GET'])
@login_required
@permission_validation(Permission.ADMIN, Permission.ADVANCED_QUERY)
def base_info():
    result = ehart_init()
    result["graph"] = 'echarts/chart/bar'
    option = result["option"]
    option['title']['text'] = u'基础资源统计'
    option['xAxis'] = {"type": 'value', "boundaryGap": [0, 0.01]}
    option["yAxis"] = {'type': 'category', 
        'data':[u'机房', u'机柜', u'设备', u'客户', u'销售']}
    data = []
    for item in [Site, Rack, Cabinet, Client, Sales]:
        data.append(item.query.count())
    option['series'].append({"type": "bar", "data": data})
    return json.dumps(result)

@cmdb.route('/cmdb/statistics/site_info/<sitename>',  methods=['GET'])
@login_required
@permission_validation(Permission.ADMIN, Permission.ADVANCED_QUERY)
def site_info(sitename):
    result = ehart_init()
    result["graph"] = 'echarts/chart/bar'
    option = result["option"]
    option['title']['text'] =  u'机房资源统计'
    option['xAxis'] = {"type": 'value', "boundaryGap": [0, 0.01]}
    option["yAxis"] = {'type': 'category', 'data': [u'机柜', u'设备']}
    data = []
    for item in [Rack, Cabinet]:
        data.append(item.query.filter_by(site=sitename).count())
    option['series'].append({"type": "bar", "data": data})
    return jsonify(result)

@cmdb.route('/cmdb/statistics/sales_info',  methods=['GET'])
@login_required
@permission_validation(Permission.ADMIN, Permission.ADVANCED_QUERY)
def sales_info():
    result = ehart_init()
    result["graph"] = 'echarts/chart/pie'
    option = result["option"]
    option['title'] = {'text': u'销售设备统计', 'x': 'center'}
    option['tooltip'] =  {'trigger':'item', 'formatter': "{a}<br/>{b} : {c} ({d}%)"}
    sales_all = Sales.query.all()
    ydata = []
    sdata = []
    for sales in sales_all:
        data = {}
        ydata.append(sales.username)
        data['name'] = sales.username
        data['value'] = Cabinet.query.filter_by(sales=sales.username).count()
        sdata.append(data)
    option['legend'] = {'orient':'vertical', 'x': 'left', 'data': ydata}
    option['series'].append({'name': u'销售',"type": "pie",  'radius': '55%', 'center': ['50%', '60%'], "data": sdata})
    return jsonify.dumps(result)
