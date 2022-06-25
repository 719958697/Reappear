# coding:utf-8
from app.models import User,UserLog
from app import db,models

class CheckLog():
    # 日志函数
    def check_log(name,method,path,request_link,network_card):
        log = UserLog()
        log.name_id = name
        log.request_type = method
        log.request_address = path
        log.request_link = request_link
        log.network_card = network_card
        db.session.add(log)
        db.session.commit()







