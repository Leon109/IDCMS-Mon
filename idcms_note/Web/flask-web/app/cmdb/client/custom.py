#coding=utf-8

from app.models import Client, Rack, IpSubnet, IpPool, Cabinet

class CustomValidator():
    def __init__(self, item, item_id, value):
        self.item = item
        self.change_client = Client.query.filter_by(id=int(item_id)).first()
        self.value = value
        self.sm =  {
            "username": self.validate_username,
        }

    def validate_return(self):
        if self.sm.get(self.item, None):
            return self.sm[self.item](self.value)
        else:
            if len(self.value) > 64:
                return u"更改失败 最大不能超过64个字符"
            if self.item in ("remark") or self.value:
                return "OK"
            return u"这个项目不能为空"

    def validate_username(self, value):
        check_item = [(Rack, u'机架'), (IpSubnet,u'IP子网'), (IpPool, u'IP'), (Cabinet, u'设备')]
        if len(self.value) > 64:
            return "更改失败 最大不能超过64个字符"
        if Client.query.filter_by(username=value).first():
            return u"更改失败 *** %s ***  已经存在" % value
        for item in check_item:
            print item[0]
            if getattr(item[0],'query').filter_by(sales=self.change_sales.username).first():
                return u"更改失败 *** %s *** 有%s在使用" \
                        % (change_sales.username, item[1])
        else:
            return "OK"
