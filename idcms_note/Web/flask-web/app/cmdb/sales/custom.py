#coding=utf-8

from app.models import Sales, Rack, IpSubnet, IpPool, Cabinet

class CustomValidator():
    '''自定义检测
    如果检测正确返回 OK
    如果失败返回提示信息
    '''
    def __init__(self, item, item_id, value):
        self.item = item
        self.change_sales = Sales.query.filter_by(id=int(item_id)).first()
        self.value = value
        self.sm =  {
            "username": self.validate_username,
        }

    def validate_return(self):
        if self.sm.get(self.item, None):
            return self.sm[self.item](self.value)
        else:
            if len(self.value) > 64:
                return u"更改失败 不能超过64个字符"
            # 判断是是否可以将值更改为空
            if self.item in ("remark") or self.value:
                return "OK"
            return u"这个项目不能为空"

    def validate_username(self, value):
        check_item = [(Rack, u'机架'), (IpSubnet, u'IP子网'), (IpPool, u'IP'), (Cabinet, u'设备')]
        if len(value) > 32:
            return u"更改失败 不能超过32个字符"
        if Sales.query.filter_by(username=value).first():
            return u"更改失败 *** %s ***  已经存在" % value
        for item in check_item:
            if getattr(item[0],'query').filter_by(sales=self.change_sales.username).first():
                return u"更改失败 *** %s *** 有%s在使用" \
                        % (change_sales.username, item[1])
        return "OK"
