#coding=utf-8
# 数据库增删改查

from sqlalchemy import or_

from .. import db
from utils import record_sql

# 添加，删除，修改数据
class edit():
    # 以下内容不记录，参考数据库模型统计
    _exclude = ['id', 'metadata', 'query', 'query_class', 'password', 'password_hash', 
                'to_list', 'verify_password','get_id']

    def __init__(self, name,  data, item, value=None):
        self.name = name
        self.data = data
        self.item = item
        self.value = value
    
    def add(self):
        db.session.add(self.data)
        item_list = [item for item in dir(self.data) if "_" not in item[0:1] \
                     and "is_" not in item  and item not in self. _exclude ]
        db.session.commit()
        value_list = []
        for item in item_list:
            value_list.append(item + ' = %s' % getattr(self.data, item))
        value = ' '.join(value_list)
        record_sql(self.name, 'add', self.data.__tablename__, self.data.id, self.item, value)

    def delete(self):
         # 防止批量删除的时候有人提前删除了 收到的是个空值
        if self.data:
            record_sql(self.name, 'delete', self.data.__tablename__, self.data.id, self.item, self.value)
            db.session.delete(self.data)
            db.session.commit()

    def change(self):
        # 防止批量修改的时候有人提前删除了 收到的是个空值
        if self.data:
            if self.item == "password":
                value = "******"
            else:
                value = self.value
            record_sql(self.name, 'change', self.data.__tablename__, self.data.id, self.item, value)
            setattr(self.data, self.item, self.value)
            db.session.add(self.data)
            db.session.commit()

# 查询数据
class search():
    '''数据库查询搜索返回
    item:搜索项目(如 Site,Rack)
    field: 不执行项目的默认搜索字段，要使用字符串
    search：搜索内容
    '''
    def __init__(self, item, field, search_value):
        self.item = item
        self.field = field
        self.search_value = search_value
        self.result = getattr(item,'query')
        self.search_run = { 
            "ALL": self.search_all,
            "OR": self.search_or,
            "multiple":self.search_multiple
        }   

    def search_return(self):
        search_info = self.search_value.split("::")
        if len(search_info) == 2:
            search_type = self.search_value.split("::")[0]
            if search_type in self.search_run:
                search_value = self.search_value.split("::")[1]
                return self.search_run[search_type](self.item, self.field, search_value)
        return self.search_run['multiple']()

    def search_all(self, *args, **kwargs):
        return self.result

    def search_or(self, item, field, search_value):
        try:
            option = [getattr(item,docm.split("==")[0])==docm.split("==")[1] for docm in search_value.split()]
            return self.result.filter(or_(*option))
        except AttributeError:
            return None

    def search_multiple(self):
        item = self.item
        field = self.field
        search_value = self.search_value
        try:
            option = {docm.split("==")[0]:docm.split("==")[1] for docm in search_value.split()}
            if not option:
                return None
            result = self.result
            for key in option.keys():
                # 如果是时间，单独处理
                if key in ("start_time", "expire_time"):
                    value = option[key].split(":")
                    # 如果有2部分，搜索时间段
                    if len(value) == 2:
                        result = result.filter(getattr(item,key).between(value[0], value[1]))
                else:
                    if option[key]:
                        result = result.filter(getattr(item,key).like("%"+option[key]+"%"))
                    # 如果搜索为空使用精确搜索(查询项目为空的值)
                    else:
                        result = result.filter(getattr(item,key)==option[key])
        # 如果不是多条件搜索
        except IndexError:
            # 如果使用模糊搜索，搜索默认字段
            # result = self.result.filter(getattr(item,field).endswith(search))
            result = self.result.filter(getattr(item,field).like("%"+search_value+"%"))
        # 如果搜索的项目发生错误
        except AttributeError:
            return  None
        return result
