# coding:utf-8
from app.api.v1.check import CheckUser
from flask import request
from flask import Blueprint
from app import redis_store
import time

dy_api = Blueprint("v1", __name__)

# 用户登录
@dy_api.route("/login", methods=['POST'])
def login():
    # 获取参数
    # data = request.get_json()
    
    # login = CheckUser.check_dylogin(data)

    # return login
    try:
        # conn = redis_store.setex("aaaaa", 60, "Assss")
        pass
    except Exception as e:
        return "redis失败: %s" % e
    # data = conn.get(key)
    print(redis_store.get(1))
    print(redis_store.keys())
    return "redis成功"
# 获取dy用户信息
@dy_api.route("/getInfo", methods=['POST'])
def dygetInfo():

    # data = request.headers.get("token")
    data = request.get_json()
    # print(data)
    getInfo = CheckUser.check_dygetInfo(data)

    return getInfo
# dy单条去水印
@dy_api.route("/single", methods=['POST'])
def dy_single():

    data = request.get_json()
    
    getInfo = CheckUser.check_dy_single_video(data)

    return getInfo
# dy多条去水印
@dy_api.route("/many", methods=['POST'])
def dy_many():

    data = request.get_json()
    
    getInfo = CheckUser.check_dy_many_video(data)

    return getInfo
# dy日志
@dy_api.route("/log", methods=['POST'])
def dy_log():

    data = request.get_json()
    
    getInfo = CheckUser.check_dy_log(data)

    return getInfo