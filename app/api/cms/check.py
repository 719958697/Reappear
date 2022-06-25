# coding:utf-8
from app.models import User,UserLog
from app import db,models
from flask import current_app, jsonify
from app.util.code_message import RET
from sqlalchemy.exc import IntegrityError
from app.util.verification.token_JMT import Token
from app.util.log import CheckLog
from app.util import *

import re
import json
import time
import requests

class CheckUser():
    # 校验用户注册
    def check_register(data):
        if data == None:
            return jsonify(code=RET.NO, message="参数错误")
        else:
            name = data.get("username")
            pwd = data.get("password")

            user = User(
                username=name,
                roles="editor",
                state = "0",
                generate_password = pwd,
                avatar_url = "https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif"
                )
            try:
                db.session.add(user)
                db.session.commit()
            except IntegrityError as e:
                # 数据库操作错误后回滚
                db.session.rollback()
                return jsonify(code=RET.DATAEXIST, message="用户名已存在注册失败")
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(code=RET.DBERR, message="查询数据异常")
            # 返回结果
            return jsonify(code=RET.OK,message="注册成功")
    # 校验用户登录
    def check_login(data):
        if data == None:
            return jsonify(code=RET.NO, message="参数错误")
        else:
            name = data.get("username")
            pwd = data.get("password")

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
                    "username":name
                    # "exp": int(time.time()) + 60
                }
                # 创建token
                token = Token.user_id(user)
                # 日志写入数据库
                CheckLog.check_log(name,"POST","/cms/user/login",None,None,user_login.id)
                return jsonify(code=RET.OK, message="登录成功",token=token)
    # 校验用户信息
    def check_getInfo(token):
        if token == None:
            return jsonify(code=RET.NO, message="参数错误")
        else:
            # 判断token是否合法
            if Token.Atoken(token) == True:
                payload = token.split(".")[1]
                payload_token = Token.decode_data(payload)
                user = User.query.filter_by(username=payload_token['user']['username']).first()

                data={
                        "name":payload_token['user']['username'],
                        "roles":[user.roles],
                        "state":user.state,
                        "email":user.email,
                        "avatar":user.avatar_url
                }
                    # 日志写入数据库
                CheckLog.check_log(payload_token['user']['username'],"POST","/cms/user/getInfo",None,None,payload_token['user']['id'])
                return jsonify(code=RET.OK, message="请求成功",data=data)
            else:
                return jsonify(code=RET.ROLEERR, message="身份异常")
    # 获取用户列表   
    def check_userList(data):
        if Token.Atoken(data["token"]) == True:
            currentPage = data["data"]["currentPage"]
            pageSize = data["data"]["pageSize"]
            try:
                data = []
                paginate = User.query.paginate(page=int(currentPage), per_page=int(pageSize), error_out=False) 
                user = paginate.items
                print(user.create_time)
                for v in user: 
                    userlists = {
                        "name":v.username,
                        "roles":v.roles,
                        "state":v.state,
                        "createtime":v.create_time
                        }
                    data.append(userlists)
                return jsonify(code=200,paginate=paginate.page,total=paginate.total, message="获取用户信息成功",data=data)
            except IntegrityError as e:
                # 数据库操作错误后回滚
                db.session.rollback()
                return jsonify(code=RET.DATAEXIST, message="获取失败")
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(code=RET.DBERR, message="查询数据异常")
        else:
            return jsonify(code=RET.ROLEERR, message="身份错误")
    # 校验用户退出
    def check_logout(): 

        return jsonify(code=RET.OK, message="退出成功")
    # dy单条去水印
    def check_dy_single(data):
        if data == None:
           
            return jsonify(code=RET.NO, message="参数错误")
        else:
            dyurl = data.get("url")
            token = data.get("token")
            # token = request.values.get("token")
            # 判断token是否合法
            if Token.load_token(token) == True:
                headers = token.split(".")[1]
                # 判断token时间是否过期
                if Token.token_time(headers) == True:
                    payload = token.split(".")[1]
                    payload_token = Token.decode_data(payload)
                    paa = re.compile('https://v.douyin.com/(.*?)/')
                    # 匹配输入内容是否带抖音链接
                    urls = re.findall(paa, dyurl)
                    # self.video_textEdit.setPlainText(text_info)
                    urls = 'https://v.douyin.com/%s/' % (urls[0])

                    headers = {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_1 like Mac OS X; zh-cn) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/18D61 Quark/5.1.1.1219 Mobile',
                    }
                    b = requests.get(urls, headers, allow_redirects=False)
                    location = b.headers['location']
                    pa = re.compile('video/(.*?)/')
                    # 匹配video
                    fl = re.findall(pa, location)
                    # 获取分享链接中返回的location链接
                    url = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=' + \
                        str(fl[0])
                    f = requests.get(url, headers).json()
                    item_list = f['item_list']
                    list0 = item_list[0]

                    author = list0['author']
                    nicknames = author['nickname']
                    share_info = list0['share_info']
                    share_title = share_info['share_title']
                    if list0['images'] == None:
                        # 判断链接类型 图集/视频
                        # print('作品类型：视频')
                        # print('='*40)
                        video = list0['video']
                        play_addr = video['play_addr']
                        uri = play_addr['uri']
                        uril = 'https://aweme.snssdk.com/aweme/v1/play/?video_id=%s&ratio=720p&line=0' % (uri)
                        data = {
                            "type":'视频',
                            "author":nicknames,
                            "share_title":share_title,
                            "url":uril
                         }
                        # 日志写入数据库
                        logdy = UserLog()
                        logdy.name_id = payload_token['username']
                        logdy.request_type = "POST"
                        logdy.request_address = "/cms/user/dy"
                        logdy.request_link = urls
                        logdy.network_card = None
                        db.session.add(logdy)
                        db.session.commit()
                        return jsonify(code=RET.OK, message="请求成功",data=data)
                    else:
                        s = []
                        num = 0
                        awemenum = len(list0['images'])
                        music = list0['video']['play_addr']['uri']
                        for j in range(awemenum):
                            num += 1
                            uril = list0['images'][j]['url_list'][0]
                            s.append(uril)
                        data = {
                        "type":'图片',
                        "background_music":music,
                        "quantity":awemenum,
                        "author":nicknames,
                        "share_title":share_title,
                        "url":s
                        }
                        # 日志写入数据库
                        logdy = UserLog()
                        logdy.name_id = payload_token['username']
                        logdy.request_type = "POST"
                        logdy.request_address = "/cms/user/dy"
                        logdy.request_link = urls
                        logdy.network_card = None
                        db.session.add(logdy)
                        db.session.commit()
                            
                        return jsonify(code=RET.OK, message="请求成功",data=data)
                   
                else:
                   return jsonify(code=RET.NO, message="token过期") 
            else:
                return jsonify(code=RET.NO, message="token不正确")