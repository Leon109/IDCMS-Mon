#coding=utf-8

init__sidebar = {
    "sidebar_for":[
        "sales", "client", "site", "rack",
        "ipsubnet", "ippool", "cabinet",
        "record"
    ],
    
    "sales":{
        "class":"start",
        "href":"/cmdb/sales",
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
        "href":"/cmdb/client",
        "icon":"icon-users",
        "title":u"客户管理",
        "li_for":["edititem", "additem"],
        "li":{ 
            "edititem": ["", "edititem",  u"客户管理"],
            "additem": ["", "additem", u"添加客户"]
        } 
    },

    "site":{
        "class":"",
        "href":"/cmdb/site",
        "icon":"icon-home",
        "title":u"机房管理",
        "li_for":["edititem", "additem"],
        "li":{ 
            "edititem": ["", "edititem",  u"机房管理"],
            "additem": ["", "additem", u"添加机房"]
        }   
    },

    "rack":{
        "class":"",
        "href":"/cmdb/rack",
        "icon":"icon-grid",
        "title":u"客户管理",
        "li_for":["edititem", "additem"],
        "li":{ 
            "edititem": ["", "edititem",  u"机柜管理"],
            "additem": ["", "additem", u"添加机柜"]
        }   
    },

    "ipsubnet":{
        "class":"",
        "href":"/cmdb/ipsubnet",
        "icon":"icon-flag",
        "title":u"IP子网管理",
        "li_for":["edititem", "additem"],
        "li":{ 
            "edititem": ["", "edititem",  u"子网管理"],
            "additem": ["", "additem", u"添加子网"]
        }   
    },

    "ippool":{
        "class":"",
        "href":"/cmdb/ippool",
        "icon":"icon-rocket",
        "title":u"IP管理",
        "li_for":["edititem", "additem"],
        "li":{ 
            "edititem": ["", "edititem",  u"IP管理"],
            "additem": ["", "additem", u"添加IP"]
        }   
    },

    "cabinet":{
        "class":"",
        "href":"/cmdb/cabinet",
        "icon":"icon-screen-desktop",
        "title":u"机柜表管理",
        "li_for":["edititem", "additem"],
        "li":{ 
            "edititem": ["", "edititem",  u"管理机柜表"],
            "additem": ["", "additem", u"添加设备"]
        }   
    },

    "record":{
        "class":"",
        "href":"/cmdb/record",
        "icon":"icon-notebook",
        "title":u"操作记录",
        "li_for":["edititem"],
        "li":{ 
            "edititem": ["", "edititem",  u"操作记录"],
        }   
    },

}

def sidebar():
    return init__sidebar
