#coding=utf-8

# 正则验证时间格式 xxxx-xx-xx
re_date = ('(^((1[8-9]\d{2})|([2-9]\d{3}))(-)(10|12|0?[13578])(-)(3[01]|[12][0-9]|0?[1-9])$)|'
    '(^((1[8-9]\d{2})|([2-9]\d{3}))(-)(11|0?[469])(-)(30|[12][0-9]|0?[1-9])$)|(^((1[8-9]\d{2})|'
    '([2-9]\d{3}))(-)(0?2)(-)(2[0-8]|1[0-9]|0?[1-9])$)|(^([2468][048]00)(-)(0?2)(-)(29)$)|'
    '(^([3579][26]00)(-)(0?2)(-)(29)$)|(^([1][89][0][48])(-)(0?2)(-)(29)$)|(^([2-9][0-9][0][48])(-)(0?2)(-)(29)$)|'
    '(^([1][89][2468][048])(-)(0?2)(-)(29)$)|(^([2-9][0-9][2468][048])(-)(0?2)(-)(29)$)|'
    '(^([1][89][13579][26])(-)(0?2)(-)(29)$)|(^([2-9][0-9][13579][26])(-)(0?2)(-)(29)$)')

# 正则则验证IP格式
re_ip = '^((25[0-5]|2[0-4]\d|[01]?\d\d?)($|(?!\.$)\.)){4}$'

def search_res(item, field, search):
    '''数据库查询搜索返回
    item:搜索项目(如 Site,Rack)
    field: 不执行项目的默认搜索字段，要使用字符串
    search：搜索内容
    '''
    try:
      option = {docm.split("==")[0]:docm.split("==")[1] for docm in search.split()}
      if option:
          for key in option.keys():
              # 第一次进行初始查询，后面的开始从上一次的基础上进行过滤
              if key == option.keys()[0]:
                  res = getattr(item,'query').filter(getattr(item,key).endswith(option[key]))
              res = res.filter(getattr(item,key).endswith(option[key]))
     # 如果不是多重搜索
    except IndexError:
        if search == "ALL":
            res = getattr(item,'query')
        else:
            res = getattr(item,'query').filter(getattr(item,field).endswith(search))
    # 如果搜索的项目发生错误
    except AttributeError:
        res = None
    return res

