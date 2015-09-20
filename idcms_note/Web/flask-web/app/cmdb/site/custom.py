#coding=utf-8

from app.models import Site, Rack, IpSubnet

class CustomValidator():
    def __init__(self, item, item_id, value):
        self.item = item
        self.change_site = Site.query.filter_by(id=int(item_id)).first()
        self.value = value
        self.sm =  {
            "site": self.validate_site,
        }

    def validate_return(self):
        if self.sm.get(self.item, None):
            return self.sm[self.item](self.value)
        else:
            if len(self.value) > 64:
                return u"更改失败 最大字符为64个字符"
            if self.item in ("dns", "remark") or self.value:
                return "OK"
            return u"这个项目不能为空"

    def validate_site(self, value):
        check_item = [(Rack, u'机架'), (IpSubnet, u'IP子网')]
        if len(self.value) > 64:
            return u"更改失败 最大字符为64个字符"
        if Site.query.filter_by(site=value).first():
            return u"更改失败 *** %s *** 已经存在" % value
        if Rack.query.filter_by(site=self.change_site.site).first():
            return u"更改失败 *** %s *** 机房有机架在使用" % self.change_site.site
        if IpSubnet.query.filter_by(site=self.change_site.site).first():
            return u"更改失败 *** %s *** 机房有IP子网在使用" % self.change_site.site
        return "OK"
