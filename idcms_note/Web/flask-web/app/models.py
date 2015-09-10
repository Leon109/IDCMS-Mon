#coding=utf-8

from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from app import db, login_manager


class User(UserMixin, db.Model):
    '''用户表
    为了使用flask-login用户模型需要继承UserMixin'''
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(64))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

    def to_list(self):
        return [self.username, '******', self.role]

@login_manager.user_loader
def load_user(user_id):
    '''这是个回调函数接收(理论上该方法放在任何一个被导入的模块中都可以，
    @login_manager.user_loader会将这个方法注册到程序中去，类似蓝本通过
    __init__ 导入,放在models，因为使用数据库的程序都会使用这个模块，保证
    这个方法会先运行下)
    以Unicode字符串形式表示的用户标识符，如果能找到用户，这个函数必须返
    回用户对象；否则应该返回None
    user_id 就是用User模型表里的id,通过id确定用户是否存在
    '''
    return User.query.get(int(user_id))


class Sales(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, index=True)
    contact = db.Column(db.String(64))
    remark = db.Column(db.String(64))
    
    def __repr__(self):
        return '<Sales %r>' % self.username

    def to_list(self):
        return [self.username, self.contact, self.remark]


class Client(db.Model):
    __tablename__ = 'client'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    contact = db.Column(db.String(64))
    remark = db.Column(db.String(64))   

    def __repr__(self):
        return '<Clinet %r>' % self.username

    def to_list(self):
        return [self.username, self.contact, self.remark]


class Site(db.Model):
    __tablename__ = 'site'
    id = db.Column(db.Integer, primary_key=True)
    site = db.Column(db.String(64), unique=True, index=True)
    isp = db.Column(db.String(64))
    location = db.Column(db.String(64))
    address = db.Column(db.String(64))
    contact = db.Column(db.String(64))
    dns = db.Column(db.String(64))
    remark = db.Column(db.String(64))

    def __repr__(self):
        return '<Site %r>' % self.site

    def to_list(self):
        return [self.site,self.isp, self.location,
                self.address, self.contact, self.dns, self.remark] 


class Rack(db.Model):
    __tablename__ = 'rack'
    id = db.Column(db.Integer, primary_key=True)
    rack = db.Column(db.String(64), index=True)
    site = db.Column(db.String(64), index=True)
    count = db.Column(db.String(32))
    power = db.Column(db.String(32))
    sales = db.Column(db.String(32))
    client = db.Column(db.String(64))
    start_time = db.Column(db.Date)
    expire_time = db.Column(db.Date)
    remark = db.Column(db.String(64))
    
    def __repr__(self):
        return '<Rack %r>' % self.rack

    def to_list(self):
        return [self.rack, self.site, self.count, self.power, 
                self.sales, self.client, self.start_time,
                self.expire_time, self.remark]


class IpSubnet(db.Model):
    __tablename__ = 'ipsubnet'
    id = db.Column(db.Integer, primary_key=True)
    subnet = db.Column(db.String(64), unique=True, index=True)
    start_ip = db.Column(db.String(64))
    end_ip = db.Column(db.String(64))
    netmask = db.Column(db.String(64))
    site = db.Column(db.String(64))
    sales = db.Column(db.String(32))
    client = db.Column(db.String(64))
    start_time = db.Column(db.Date)
    expire_time = db.Column(db.Date)
    remark = db.Column(db.String(64))
    
    def __repr__(self):
        return '<IpSubnet %r>' % self.subnet

    def to_list(self):
        return [self.subnet, self.start_ip, self.end_ip,
                self.netmask, self.site, self.sales, self.client,
                self.start_time, self.expire_time, self.remark]


class IpPool(db.Model):
    __tablename__ = 'ippool'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(64), unique=True, index=True)
    netmask = db.Column(db.String(64))
    gateway = db.Column(db.String(64))
    subnet = db.Column(db.String(64))
    site = db.Column(db.String(64))
    sales = db.Column(db.String(32))
    client = db.Column(db.String(64))
    remark = db.Column(db.String(64))
    
    def __repr__(self):
        return '<IpPool %r>' % self.ip

    def to_list(self):
        return [self.ip, self.netmask, self.gateway,self.subnet, 
                self.site, self.sales, self.client, self.remark]

class Cabinet(db.Model):
    __tablename__ = 'cabinet'
    id = db.Column(db.Integer, primary_key=True)
    an = db.Column(db.String(64), unique=True, index=True)
    wan_ip = db.Column(db.String(64), index=True)
    lan_ip = db.Column(db.String(64), index=True)
    site = db.Column(db.String(64))
    rack = db.Column(db.String(32))
    seat = db.Column(db.String(32))
    bandwidth = db.Column(db.String(32))
    up_link = db.Column(db.String(32))
    height = db.Column(db.String(32))
    brand = db.Column(db.String(32))
    model = db.Column(db.String(32))
    sn = db.Column(db.String(64))
    sales = db.Column(db.String(32))
    client = db.Column(db.String(64))
    start_time = db.Column(db.Date)
    expire_time = db.Column(db.Date)
    remark = db.Column(db.String(64))
    
    def __repr__(self):
        return '<Cabinet %r>' % self.an

    def to_list(self):
        return [self.an, self.wan_ip, self.lan_ip,self.site, 
                self.rack, self.seat, self.bandwidth, self.up_link,
                self.height, self.brand, self.model, self.sn, self.sales,
                self.client, self.start_time, self.expire_time,self.remark]

class Record(db.Model):
    __tablename__ = 'record'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    status = db.Column(db.String(32))
    table = db.Column(db.String(32))
    table_id = db.Column(db.String(32))
    item = db.Column(db.String(32))
    value = db.Column(db.String(600))
    date = db.Column(db.DateTime)

    def __repr__(self):
        return '<Record %r>' % self.username
   
    def to_list(self):
        return [self.username, self.status, self.table,
                self.table_id, self.item, self.value, self.date]
