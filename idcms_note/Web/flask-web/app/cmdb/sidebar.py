#coding=utf-8

start_sidebar = {
    "sidebar_for":[
        "sales", "client", "site", "rack",
        "ipsubnet", "ippool", "cabinet",
        "record", "statistics"
    ],
    
    "sales":{
        "class":"start",
        "href":"/cmdb/sales",
        "icon":"icon-user-female",
        "title":u"销售管理",
        "li_for":["edititem", "additem"],
        "li":{ 
            "edititem": ["", "edititem",  u"销售管理", 'content hidden'],
            "additem": ["", "additem", u"添加销售", 'content hidden']
        }
    },
    
    "client":{
        "class":"",
        "href":"/cmdb/client",
        "icon":"icon-users",
        "title":u"客户管理",
        "li_for":["edititem", "additem"],
        "li":{ 
            "edititem": ["", "edititem",  u"客户管理", 'content hidden'],
            "additem": ["", "additem", u"添加客户", 'content hidden']
        } 
    },

    "site":{
        "class":"",
        "href":"/cmdb/site",
        "icon":"icon-home",
        "title":u"机房管理",
        "li_for":["edititem", "additem"],
        "li":{ 
            "edititem": ["", "edititem",  u"机房管理", 'content hidden'],
            "additem": ["", "additem", u"添加机房", 'content hidden']
        }   
    },

    "rack":{
        "class":"",
        "href":"/cmdb/rack",
        "icon":"icon-grid",
        "title":u"机柜管理",
        "li_for":["edititem", "additem"],
        "li":{ 
            "edititem": ["", "edititem",  u"机柜管理", 'content hidden'],
            "additem": ["", "additem", u"添加机柜", 'content hidden']
        }   
    },

    "ipsubnet":{
        "class":"",
        "href":"/cmdb/ipsubnet",
        "icon":"icon-flag",
        "title":u"IP子网管理",
        "li_for":["edititem", "additem"],
        "li":{ 
            "edititem": ["", "edititem",  u"子网管理", 'content hidden'],
            "additem": ["", "additem", u"添加子网", 'content hidden']
        }   
    },

    "ippool":{
        "class":"",
        "href":"/cmdb/ippool",
        "icon":"icon-rocket",
        "title":u"IP管理",
        "li_for":["edititem", "additem"],
        "li":{ 
            "edititem": ["", "edititem",  u"IP管理", 'content hidden'],
            "additem": ["", "additem", u"添加IP", 'content hidden']
        }   
    },

    "cabinet":{
        "class":"",
        "href":"/cmdb/cabinet",
        "icon":"icon-screen-desktop",
        "title":u"机柜表管理",
        "li_for":["edititem", "additem"],
        "li":{ 
            "edititem": ["", "edititem",  u"管理机柜表", 'content hidden'],
            "additem": ["", "additem", u"添加设备", 'content hidden']
        }   
    },

    "record":{
        "class":"",
        "href":"/cmdb/record",
        "icon":"icon-notebook",
        "title":u"操作记录",
        "li_for":["edititem"],
        "li":{"edititem": ["", "edititem", u"查询操作记录", 'content hidden']}
    },

    "statistics":{
        "class":"",
        "href":"/cmdb/statistics",
        "icon":"icon-bar-chart",
        "title":u"统计分析",
        "li_for":["base", "site", "salse"],
        "li":{
            "base": ["", "base", u"查询操作记录", 'content hidden', '/cmdb/statistics/base_info'],
            "site": ["", "site", u'机房资源统计', 'content hidden', '/cmdb/statistics/site_info/'],
            "salse": ["", "salse", u'销售设备统计', 'content hidden', '/cmdb/statistics/sales_info']
        }
    },  

}
