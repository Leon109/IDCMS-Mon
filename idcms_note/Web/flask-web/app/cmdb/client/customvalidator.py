#coding=utf-8

from app.models import Client, Rack, IpSubnet, IpPool, Cabinet

class CustomValidator():
    '''自定义检测
    如国检测正确返回 OK
    如国失败返回提示信息
    '''
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
        if len(self.value) > 64:
            return "更改失败 最大不能超过64个字符"
        if Client.query.filter_by(username=value).first():
            return u"更改失败 这个客户已经存在"
        if Rack.query.filter_by(client=self.change_client.username).first():
            return u"更改失败 这个客户有机架在使用"
        if IpSubnet.query.filter_by(client=self.change_client.username).first():
            return u"更改失败 这个客户有IP子网在使用"
        if IpPool.query.filter_by(client=self.change_client.username).first():
            return u"更改失败 这个客户有IP在使用"
        if Cabinet.query.filter_by(client=self.change_client.username).first():
            return u"更改失败 这个客户有设备在使用"
        else:
            return "OK"
