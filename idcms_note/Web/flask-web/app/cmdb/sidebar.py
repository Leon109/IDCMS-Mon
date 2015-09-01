#coding=utf-8

init__sidebar = {
    "sidebar_for":[
        "sales",
    ],
    
    "sales":{
        "class":"start",
        "herf":"/cmdb/sales",
        "icon":"icon-user-female",
        "title":u"销售管理",
        "li_for":["edititem", "additem"],
        "li":{ 
            "edititem": ["", "edititem",  u"销售管理"],
            "additem": ["", "additem", u"添加销售"]
        }
    },
    
    "client":{
        "class":"",
        "icon":"icon-users",
        "title":u"客户管理",
        "li":[["", "edititem", "",  u"管理客户"],["", "additem", "", u"添加客户"]]
    }
}

def sidebar():
    return init__sidebar
