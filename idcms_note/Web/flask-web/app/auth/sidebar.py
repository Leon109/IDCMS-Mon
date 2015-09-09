#coding=utf-8

start_sidebar = {
    "sidebar_for":[
        "setting"
    ],
    
    "setting":{
        "class":"",
        "href":"/auth/setting",
        "icon":"icon-settings",
        "title":u"设置",
        "li_for":["passwd", "register", "edituser"],
        "li":{
            "passwd": ["", "passwd", u"修改密码", 'content hidden'],
            "register": ["", "register", u'添加用户', 'content hidden'],
            "edituser": ["", "edituser", u'管理用户', 'content hidden']
        }
    },  

}
