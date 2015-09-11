#coding=utf-8

import datetime
from .. import db
from ..models import Record

from sqlalchemy import or_

# 正则验证时间格式 xxxx-xx-xx
re_date = ('(^((1[8-9]\d{2})|([2-9]\d{3}))(-)(10|12|0?[13578])(-)(3[01]|[12][0-9]|0?[1-9])$)|'
    '(^((1[8-9]\d{2})|([2-9]\d{3}))(-)(11|0?[469])(-)(30|[12][0-9]|0?[1-9])$)|(^((1[8-9]\d{2})|'
    '([2-9]\d{3}))(-)(0?2)(-)(2[0-8]|1[0-9]|0?[1-9])$)|(^([2468][048]00)(-)(0?2)(-)(29)$)|'
    '(^([3579][26]00)(-)(0?2)(-)(29)$)|(^([1][89][0][48])(-)(0?2)(-)(29)$)|(^([2-9][0-9][0][48])(-)(0?2)(-)(29)$)|'
    '(^([1][89][2468][048])(-)(0?2)(-)(29)$)|(^([2-9][0-9][2468][048])(-)(0?2)(-)(29)$)|'
    '(^([1][89][13579][26])(-)(0?2)(-)(29)$)|(^([2-9][0-9][13579][26])(-)(0?2)(-)(29)$)')

# 正则则验证IP格式
re_ip = '^((25[0-5]|2[0-4]\d|[01]?\d\d?)($|(?!\.$)\.)){4}$'

# 搜索方法
class search_res():
    '''数据库查询搜索返回
    item:搜索项目(如 Site,Rack)
    field: 不执行项目的默认搜索字段，要使用字符串
    search：搜索内容
    '''
    def __init__(self, item, field, search):
        self.item = item
        self.field = field
        self.search = search
        self.search_run = {
            "ALL": self.search_all,
            "OR": self.search_or,
            "recursive":self.search_recursive
        }

    def search_return(self):
        search_info = self.search.split("::")
        if len(search_info) == 2:
            search_type = self.search.split("::")[0]
            if search_type in self.search_run:
                search = self.search.split("::")[1]
                return self.search_run[search_type](self.item, self.field, search)
        return self.search_run['recursive']()

    def search_all(self, item, field, search):
        return getattr(item,'query')
    
    def search_or(self, item, field, search):
        try:
            option = [getattr(item,docm.split("==")[0])==docm.split("==")[1] for docm in search.split()]
            return getattr(item,'query').filter(or_(*option))
        except AttributeError:
            return None

    def search_recursive(self):
        item = self.item
        field = self.field
        search = self.search
        try:
            option = {docm.split("==")[0]:docm.split("==")[1] for docm in search.split()}
            if not option:
                return None
            for key in option.keys():
                # 第一次进行初始查询，后面的开始从上一次的基础上进行过滤
                if key == option.keys()[0]:
                    # 如果是时间，单独处理
                    if key in ("start_time", "expire_time"):
                        value = option[key].split(":")
                        if len(value) == 2:
                            res = getattr(item,'query').filter(getattr(item,key).between(value[0], value[1]))
                    else:
                        if option[key]:
                            res = getattr(item,'query').filter(getattr(item,key).like("%"+option[key]+"%"))
                        # 如果搜索为空使用精确搜索
                        else:
                            res = getattr(item,'query').filter(getattr(item,key)==option[key])
                else:
                    if key in ("start_time", "expire_time"):
                        value = option[key].split(":")
                        if len(value) == 2:
                            res = res.filter(getattr(item,key).between(value[0], value[1]))
                    else:
                        if option[key]:
                            res = res.filter(getattr(item,key).like("%"+option[key]+"%"))
                        else:
                            res = res.filter(getattr(item,key)==option[key])
        # 如果不是多重搜索
        except IndexError:
            # 如果使用模糊搜索
            # res = getattr(item,'query').filter(getattr(item,field).endswith(search))
            res = getattr(item,'query').filter(getattr(item,field).like("%"+search+"%"))
        # 如果搜索的项目发生错误
        except AttributeError:
            return  None
        return res

# 基础cmdb操作
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
        for th in  thead:
            if str(th[0]) in checkbox:
                th [3] = True
            else:
                th[3] = False
    else:
        for box in range(0,len(thead)):
            thead[box][3] = False
    return thead
