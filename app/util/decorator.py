from flask import request
from app.util.verification.token_JMT import Token
from app.util.code_message import RET
from flask import current_app, jsonify, g
from app.models import User
import functools
import json

def Check_token_admin(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 1. 获取用户请求头中的 用户名 信息
        token = request.headers.get("token")
        user_UA = request.headers.get("User-Agent")
        if not all([token, user_UA]):
            return jsonify(code=5000, message="参数不完整")
        if Token.load_token(token) == True:
            payload = token.split(".")[1]
            payload_token = Token.decode_data(payload)
            try:
                user = User.query.filter_by(username=payload_token['user']['username']).first()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(code=RET.DBERR, message="获取用户权限失败")

            if Token.token_time(payload) == True:
                if user.roles == 0 or user.roles == 1:
                    g.user_id = payload_token
                    return func(*args, **kwargs)
                else:
                    return jsonify(code=RET.ROLEERR, message="权限不足")
            else:
                return jsonify(code=RET.TOO, message="身份过期")    
        else:
            return jsonify(code=RET.ROLEERR, message="身份错误")
    return wrapper

def Check_token_user(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 1. 获取用户请求头中的 用户名 信息
        token = request.headers.get("token")
        # token = json.loads(data)
        payload = token.split(".")[1]
        # return print(data)
        if Token.load_token(token) == True:
            payload_token = Token.decode_data(payload)
            try:
                user = User.query.filter_by(username=payload_token['user']['username']).first()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(code=RET.DBERR, message="获取用户权限失败")
            if Token.token_time(payload) == True:
                if user.state == 1:
                    return jsonify(code=RET.NO, message="账户不可用")
                elif user.is_delete == 1:
                    return jsonify(code=RET.NO, message="账户已被删除")
                else:
                    g.user_id = payload_token
                    return func(*args, **kwargs)
            else:
                return jsonify(code=RET.TOO, message="身份过期")
        else:
            return jsonify(code=RET.ROLEERR, message="身份错误")

    return wrapper

# def Check_Token_Refresh_token(token):
#     refresh = token["refresh_token"]
#     # 判断token是否合法
#     if Token.load_token(refresh) == True:
#         headers = refresh.split(".")[0]
#         payload = refresh.split(".")[1]
#         payload = Token.decode_data(payload)
#         if Token.token_time(headers) == True:
#             access_token = Token.user_id1(payload["user"])
#             token = {
#                 "access_token":access_token,
#                 "refresh_token":refresh
#                 }
#             return jsonify(code=RET.SXTK, token=token, message="刷新令牌")
#         else:
#             return jsonify(code=RET.TOO, message="身份过期")  
#     else:
#         return jsonify(code=RET.ROLEERR, message="身份错误")
