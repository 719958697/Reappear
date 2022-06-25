import time
import json
import base64
import hashlib
import hmac


# 设置密钥
salt = "Lfc#5520@?"
# 设置过期时间戳
# exp = 30

headers_access_token  = {
    "typ": "lfc",
    # "exp": int(time.time()) + 15
}
headers_refresh_token  = {
    "typ": "lfc",
    # "exp": int(time.time()) + 60
}
payload_refresh_token = {
    "exp": int(time.time()) + 180,
    "hai":"你好,别这样!"
}
class Token:
    # 首次编写信息体
    def user_id(load):
        exp = {
            "user":load,
            "exp": int(time.time()) + 180
        }
        access_token = Token.access_token(exp)
        # refresh_token = Token.refresh_token(exp)
        # token = {
        #     "access_token":access_token,
        #     "refresh_token":refresh_token
        # }
        return access_token

    # 编写信息体
    # def user_id1(load):
    #     exp = {
    #         "user":load,
    #         "exp": int(time.time())
    #     }
    #     access_token = Token.access_token(exp)
    #     return access_token

    # 生成access_token
    def access_token(payload):
        # 生产header
        first_access_token = base64.urlsafe_b64encode(json.dumps(headers_access_token, separators=(',', ':')).encode('utf-8').replace(b'=', b'')).decode('utf-8').replace('=', '')
        # 生成payload
        second_access_token = base64.urlsafe_b64encode(json.dumps(payload, separators=(',', ':')).encode('utf-8').replace(b'=', b'')).decode('utf-8').replace('=', '')

        first_access_token_second = f"{first_access_token}.{second_access_token}"
        # 生成签名
        third_access_token = base64.urlsafe_b64encode(
            hmac.new(salt.encode('utf-8'), first_access_token_second.encode('utf-8'), hashlib.sha256).digest()).decode('utf-8').replace('=','')

        access_token = ".".join([first_access_token, second_access_token, third_access_token])

        return access_token

        # 生成refresh_token
    def refresh_token(payload):
        # 生产header
        first_refresh_token = base64.urlsafe_b64encode(json.dumps(headers_refresh_token, separators=(',', ':')).encode('utf-8').replace(b'=', b'')).decode('utf-8').replace('=', '')
        # 生成payload
        second_refresh_token = base64.urlsafe_b64encode(json.dumps(payload, separators=(',', ':')).encode('utf-8').replace(b'=', b'')).decode('utf-8').replace('=', '')

        first_refresh_token_second = f"{first_refresh_token}.{second_refresh_token}"
        # 生成签名
        third_refresh_token = base64.urlsafe_b64encode(
            hmac.new(salt.encode('utf-8'), first_refresh_token_second.encode('utf-8'), hashlib.sha256).digest()).decode('utf-8').replace('=','')

        refresh_token = ".".join([first_refresh_token, second_refresh_token, third_refresh_token])
        
        return refresh_token

    # 验证token
    def load_token(token):
        # 解析token
        headers = token.split(".")[0]
        payload = token.split(".")[1]
        signs = token.split(".")[2]

        # 对数据签名、判断token上对签名是否是合规对
        headers_payload = f"{headers}.{payload}"
        new_sign = base64.urlsafe_b64encode(
            hmac.new(salt.encode('utf-8'), headers_payload.encode('utf-8'), hashlib.sha256).digest()).decode('utf-8').replace('=','')
        if new_sign == signs:
            return True
        else:
            return False
    # 解码   
    def decode_data(data):
        if isinstance(data, str):
            data = data.encode('ascii')
        rem = len(data) % 4
        if rem > 0:
            data += b'=' * (4 - rem)
        # 上面这一部分是解密的部分数据补全格式
        data = base64.urlsafe_b64decode(data)  # 解码
        data = json.loads(data)
        return data

    # 解析token时间
    def token_time(data):
        token_time = Token.decode_data(data)
        if token_time['exp'] >= int(time.time()):
            return True 
        else:
            return False
    
    # # 设置双token验证
    # def Atoken(token):
    #     access = token
    #     print(access)
    #     # 判断token是否合法
    #     if Token.load_token(access) == True:
    #         payload = access.split(".")[0]
    #         s = Token.decode_data(payload)
    #         ss = s['exp'] - int(time.time())
    #         print(payload)
    #         print(s)
    #         print(ss)
    #         # 判断token时间是否过期
    #         if Token.token_time(payload) == True:
    #             return True
    #         else:
    #             return print("1")
    #     else:
    #         return print("2")

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
    #             return token
    #         else:
    #             return False
    #     else:
    #         return False