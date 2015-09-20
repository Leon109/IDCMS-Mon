#coding=utf-8

import datetime

from .. import db
from ..models import Record

# 正则验证时间格式 xxxx-xx-xx
re_date = ('(^((1[8-9]\d{2})|([2-9]\d{3}))(-)(10|12|0?[13578])(-)(3[01]|[12][0-9]|0?[1-9])$)|'
    '(^((1[8-9]\d{2})|([2-9]\d{3}))(-)(11|0?[469])(-)(30|[12][0-9]|0?[1-9])$)|(^((1[8-9]\d{2})|'
    '([2-9]\d{3}))(-)(0?2)(-)(2[0-8]|1[0-9]|0?[1-9])$)|(^([2468][048]00)(-)(0?2)(-)(29)$)|'
    '(^([3579][26]00)(-)(0?2)(-)(29)$)|(^([1][89][0][48])(-)(0?2)(-)(29)$)|(^([2-9][0-9][0][48])(-)(0?2)(-)(29)$)|'
    '(^([1][89][2468][048])(-)(0?2)(-)(29)$)|(^([2-9][0-9][2468][048])(-)(0?2)(-)(29)$)|'
    '(^([1][89][13579][26])(-)(0?2)(-)(29)$)|(^([2-9][0-9][13579][26])(-)(0?2)(-)(29)$)')

# 正则则验证IP格式
re_ip = '^((25[0-5]|2[0-4]\d|[01]?\d\d?)($|(?!\.$)\.)){4}$'

# 记录操作
def record_sql(user, status, table, table_id, item, value):
    '''记录cmdb操作记录'''
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = Record(
        username=user,
        status=status,
        table=table,
        table_id=table_id,
        item=item,
        value=value,
        date=date,
    )   
    db.session.add(record)

# 侧边栏初始化
def init_sidebar(sidebar, sidebar_name,item):
    sidebar[sidebar_name]['class'] = "active open"
    sidebar[sidebar_name]['li'][item][0] = "active"
    sidebar[sidebar_name]['li'][item][3] = 'content'
    li_list = sidebar[sidebar_name]['li'].keys()
    li_list.remove(item)
    for licss  in li_list:
        sidebar[sidebar_name]['li'][licss][0] = ""
        sidebar[sidebar_name]['li'][licss][3] = "content hidden"
    return sidebar

# 选择框初始化
def init_checkbox(thead, checkbox):
    '''处理需要隐藏的字段
    checkbox 是一个列表，对应需要隐藏的字段的索引
    '''
    if checkbox:
        if isinstance(checkbox, str):
            checkbox = eval(checkbox)
        for th in thead:
            if str(th[0]) in checkbox:
                th [3] = True
            else:
                th[3] = False
    else:
        for box in range(0, len(thead)):
            thead[box][3] = False
    return thead
