#coding=utf-8

import os
import sys
import json

from flask import render_template
from flask.ext.login import login_required

from .. import cmdb

workdir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, workdir + "/../../../")

from app import db
from app.models import Site, Rack, Client, Sales, Cabinet
from app.utils.permission import Permission, permission_validation
# 初始化参数
titles = {'path':'/cmdb/statistics', 'title':u'IDCMS-CMDB-统计分析'}

def ehart_init():
    echart = {
        "graph": None,
        "option": {
            'title': {}, 'tooltip': {},
            'toolbox': {
                'show': True,
                'feature': {
                    'mark': {'show': True}, 'restore': {'show': True},
                    'saveAsImage': {'show': True}
                    }
            },
            'calculable': True, 'series': []
        }  
    }
    return echart


@cmdb.route('/cmdb/statistics',  methods=['GET', 'POST'])
@login_required
@permission_validation(Permission.ADMIN)
def statistics():
    all_site = Site.query.all()
    return render_template('/cmdb/statistics.html', titles=titles, all_site=all_site)

@cmdb.route('/cmdb/statistics/base_info',  methods=['GET'])
@login_required
@permission_validation(Permission.ADMIN)
def base_info():
    res = ehart_init()
    res["graph"] = 'echarts/chart/bar'
    option = res["option"]
    option['title']['text'] = u'基础资源统计'
    option['xAxis'] = {"type": 'value', "boundaryGap": [0, 0.01]}
    option["yAxis"] = {'type': 'category', 
        'data':[u'机房', u'机柜', u'设备', u'客户', u'销售']}
    data = []
    for item in [Site, Rack, Cabinet, Client, Sales]:
        data.append(item.query.count())
    option['series'].append({"type": "bar", "data": data})
    return json.dumps(res)

@cmdb.route('/cmdb/statistics/site_info/<sitename>',  methods=['GET'])
@login_required
@permission_validation(Permission.ADMIN)
def site_info(sitename):
    res = ehart_init()
    res["graph"] = 'echarts/chart/bar'
    option = res["option"]
    option['title']['text'] =  u'机房资源统计'
    option['xAxis'] = {"type": 'value', "boundaryGap": [0, 0.01]}
    option["yAxis"] = {'type': 'category', 'data': [u'机柜', u'设备']}
    data = []
    for item in [Rack, Cabinet]:
        data.append(item.query.filter_by(site=sitename).count())
    option['series'].append({"type": "bar", "data": data})
    return json.dumps(res)

@cmdb.route('/cmdb/statistics/sales_info',  methods=['GET'])
@login_required
@permission_validation(Permission.ADMIN)
def sales_info():
    res = ehart_init()
    res["graph"] = 'echarts/chart/pie'
    option = res["option"]
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
    return json.dumps(res)
