# coding:utf-8
# coding:utf-8
from app.models import User
from app import db,models
from flask import current_app,jsonify 
from app.util.code_message import RET
from sqlalchemy.exc import IntegrityError
from app.util.verification.token_JMT import Token
from app.util.log import CheckLog

import re
import time

class CheckUser():
    # 校验用户登录
    def check_dylogin(data):
        if data == None:
            return jsonify(code=RET.NO, message="参数错误")
        else:
            name = data.get("username")
            pwd = data.get("password")
            network = data.get("network")

            try:
                user_login = User.query.filter_by(username=name).first()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(code=RET.DBERR, message="获取用户信息失败")

            # 用数据库的密码与用户填写的密码进行对比验证
            if user_login is None  or not user_login.check_password(pwd):
                return jsonify(code=RET.DBERR,message="用户名或密码错误")
            else:
                user = {
                    "id":user_login.id,
                    "username":name,
                    "exp": int(time.time()) + 60
                }
                # 创建token
                token = Token.create_token(user)
                # 日志写入数据库
                CheckLog.check_log(name,"POST","/cms/user/login",None,network,user_login.id)
                return jsonify(code=RET.OK, message="登录成功",token=token)
     # 校验dy用户信息    
    def check_dygetInfo(token):
        access_token = token["access_token"]
        if token == None:
            return jsonify(code=RET.NO, message="参数错误")
        else:
            # 判断token是否合法
            if Token.load_token(access_token) == True:
                payload = access_token.split(".")[1]
                # 判断token时间是否过期
                if Token.token_time(payload) == True:
                    payload_token = Token.decode_data(payload)
                    user = User.query.filter_by(username=payload_token['username']).first()

                    data={
                        "name":payload_token['username'],
                        "roles":[user.roles],
                        "state":user.state,
                        "email":user.email,
                        "avatar":user.avatar_url
                    }
                    # 日志写入数据库
                    CheckLog.check_log(payload_token['username'],"POST","/cms/user/dygetInfo",None,None,payload_token['id'])
                    return jsonify(code=RET.OK, message="请求成功",data=data)
                else:
                    return jsonify(code=414, message="token过期")
            else:
                return jsonify(code=408, message="token不正确")
    # dy单条去水印
    def check_dy_single_video(data):
        name = data["name"]
        url = data["url"]
        network = data["network"]
        try:
            user_login = User.query.filter_by(username=name).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(code=RET.DBERR, message="获取用户信息失败")

        CheckLog.check_log(user_login.username,"POST","/cms/user/single",url,network,user_login.id)
        return jsonify(code=RET.OK, message="请求成功")
    # dy多条去水印
    def check_dy_many_video(data):
        name = data["name"]
        url = data["url"]
        network = data["network"]
        try:
            user_login = User.query.filter_by(username=name).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(code=RET.DBERR, message="获取用户信息失败")

        CheckLog.check_log(user_login.username,"POST","/cms/user/single",url,network,user_login.id)
        return jsonify(code=RET.OK, message="请求成功") 
