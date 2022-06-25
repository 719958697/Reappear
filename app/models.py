# coding:utf-8

from datetime import datetime
from flask.app import Flask
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class BaseModel(object):
    """模型基类，为模型补充创建时间与更新时间"""
    
    # 记录的创建时间
    create_time = db.Column(db.DateTime, default=datetime.now)
    # 记录的更新时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class User(BaseModel, db.Model):
    """用户表"""
    __tablename__ = "user"
 
    # 用户编号id
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    # 用户名
    username = db.Column(db.String(32), unique=True,nullable=False)
    # 用户身份id 管理员:0 使用者:1
    roles = db.Column(db.SmallInteger)
    # 状态 0:正常 1:禁用 
    state = db.Column(db.SmallInteger)
    # 是否删除 0:正常 1:已删除
    is_delete = db.Column(db.SmallInteger)
    # 删除时间 
    delete_tiem = db.Column(db.String(32))
    # 邮箱
    email = db.Column(db.String(32))
    # 密码
    password = db.Column(db.String(256),nullable=False)
    # 用户头像
    avatar_url = db.Column(db.String(128))

    @property
    def generate_password(self):
        raise Exception("Error Action:密码不可读取")

    # 加密装饰器
    @generate_password.setter
    def generate_password(self, value):
        self.password = generate_password_hash(value)

    # 密码校验装饰器
    def check_password(self, passwd):
        return check_password_hash(self.password,passwd)
    
    def to_dict(self):
        """将对象数据转换为字典数据"""
        user_dict = {
            "id":self.id,
            "name":self.username,
            "roles":User.if_roles(self.roles),
            "isdelete":self.is_delete,
            "deletetiem":self.delete_tiem,
            "create_time":self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "email":self.email,
            "avatar_url":self.avatar_url
        }
        return user_dict
    # 设置权限返回值
    def if_roles(roles):
        if roles == 0:
            return "root"
        elif roles == 1:
            return "admin"
        elif roles == 2:
            return "editor"

class UserLog(BaseModel, db.Model):
    
    """用户日志"""
    __tablename__ = "userlog"

    # id
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    # 用户id
    name_id = db.Column(db.String(32))
    # 请求类型
    request_type = db.Column(db.String(8))
    # 请求地址
    request_address = db.Column(db.String(32))
    # 请求链接
    request_link = db.Column(db.String(64))
    # 网卡
    network_card = db.Column(db.String(32))
