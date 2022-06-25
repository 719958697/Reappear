# coding:utf-8
from app import db,models
from app.api.cms.check import CheckUser
from flask import request
from flask import Blueprint
from app.util.code_message import RET
from flask import current_app, jsonify, g
from app.models import User,UserLog
from sqlalchemy.exc import IntegrityError
from app.util.log import CheckLog
from app.util.verification.token_JMT import Token
from app.util.decorator import Check_token_user
import requests
import re


user_api = Blueprint("user", __name__)

# 用户注册
@user_api.route("/register", methods=['POST'])
def register():
    # 获取数据
    data = request.get_json()
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
            db.session.close()
        except IntegrityError as e:
            # 数据库操作错误后回滚
            db.session.rollback()
            return jsonify(code=RET.DATAEXIST, message="用户名已存在注册失败")
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(code=RET.DBERR, message="查询数据异常")
        # 返回结果
        return jsonify(code=RET.OK,message="注册成功")


# 用户登录
@user_api.route("/login", methods=['POST'])
def login():
    # 获取参数
    data = request.get_json()

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
            "username":user_login.username
        }
        # 创建token
        token = Token.user_id(user)
        # 日志写入数据库
        # CheckLog.check_log(name,"POST","/cms/user/login",None,None,user_login.id)
        return jsonify(code=RET.OK, message="登录成功",token=token)

# 获取用户信息
@user_api.route("/getInfo", methods=['GET'])
@Check_token_user
def getInfo():
    user_id = g.user_id['user']['username']
    # user = User.query.filter_by(username=user_id).first()
    # print(user.to_dict())
    try:
        user = User.query.filter_by(username=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, message="获取用户信息失败")

    data={
            "name":user.username,
            "roles":[User.if_roles(user.roles)],
            "state":user.state,
            "email":user.email,
            "avatar":user.avatar_url
        }
    #     # 日志写入数据库
    CheckLog.check_log(user_id,"POST","/cms/user/getInfo",None,None)
    return jsonify(code=RET.OK, message="请求成功",data=data)

# 用户退出
@user_api.route("/logout", methods=['POST'])
@Check_token_user
def logout():

    return jsonify(code=RET.OK, message="退出成功")

# dy单条去水印
@user_api.route("/dy", methods=['POST'])
@Check_token_user
def dy_single():
    data = request.get_json()
    dyurl = data.get("url")
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
        d = []
        video = list0['video']
        play_addr = video['play_addr']
        uri = play_addr['uri']
        uril = 'https://aweme.snssdk.com/aweme/v1/play/?video_id=%s&ratio=720p&line=0' % (uri)
        data = {
            "type":'视频',
            "author":nicknames,
            "share_title":share_title,
            "url":uril + ".mp4",
            "quantity":1
            }
        d.append(data)
        # # 日志写入数据库
        # CheckLog.check_log(payload_token['user']['username'],"POST","/cms/user/dy",urls,None)
        return jsonify(code=RET.OK, message="请求成功",data=d)
    else:
        s = []
        d = []
        num = 0
        awemenum = len(list0['images'])
        music = list0['video']['play_addr']['uri']
        for j in range(awemenum):
            uril = list0['images'][j]['url_list'][0]
            s.append(uril)
        
        data = {
            "id":num,
            "type":'图片',
            "cover":list0['images'][0]['url_list'][0],
            "background_music":music,
            "quantity":awemenum,
            "author":nicknames,
            "share_title":share_title,
            "urls": s
        }
            
        d.append(data)
        # 日志写入数据库
        # CheckLog.check_log(payload_token['user']['username'],"POST","/cms/user/dy",urls,None)
        print(data)
            
        return jsonify(code=RET.OK, message="请求成功",data=d)
