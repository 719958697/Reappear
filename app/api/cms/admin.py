# coding:utf-8
from http.client import OK
from app import db,models
from flask import request
from flask import Blueprint
from app.util.code_message import RET
from flask import current_app, jsonify, g
from app.models import User,UserLog
from sqlalchemy.exc import IntegrityError
from app.util.log import CheckLog
from app.util.verification.token_JMT import Token
from app.util.decorator import Check_token_admin
from datetime import datetime

admin_api = Blueprint("admin", __name__)

# admin新曾用户接口--------------------------------------------------------------------------
@admin_api.route("/admin_register", methods=['POST'])
@Check_token_admin
def admin_register():
    data = request.get_json()
    name = data.get("username")
    pwd = data.get("password")
    roles = data.get("roles")
    email = data.get("email")
    if not all([name, pwd, roles]):
        return jsonify(code=5000, message="参数不完整")
    # 获取数据
    user = User(
        username=name,
        roles= roles,
        state = 0,
        is_delete = 0,
        delete_tiem = "0000-00-00 00:00:00",
        email = email,
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
# 获取多用户列表
@admin_api.route("/admin_userList", methods=['POST'])
@Check_token_admin
def userList():
    data = request.get_json()
    currentPage = data["currentPage"]
    pageSize = data["pageSize"]
    if not all([currentPage,pageSize]):
        return jsonify(code=RET.NO, message="参数不完整")
    try:
        data = []
        paginate = User.query.filter(User.is_delete == 0).paginate(page=int(currentPage), per_page=int(pageSize), error_out=False, max_per_page=None) 
        user = paginate.items
        mun = 0
        for v in user:
            mun += 1
            userlists = {
                "id":mun,
                "name":v.username,
                "roles":v.roles,
                "state":v.state,
                "isdelete":v.is_delete,
                "password":v.password,
                "createtime":v.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            data.append(userlists)
        print(data)
        return jsonify(code=RET.OK,paginate=paginate.page,total=paginate.total, message="获取用户信息成功",data=data)
    except IntegrityError as e:
        # 数据库操作错误后回滚
        db.session.rollback()
        return jsonify(code=RET.DATAEXIST, message="获取失败")
    except Exception as e:
        current_app.logger.error(e)
    return jsonify(code=RET.DBERR, message="查询数据异常")
# 用户的状态按钮
@admin_api.route("/admin_userstateBtn", methods=['POST'])
@Check_token_admin
def admin_userstateBtn():
    data = request.get_json()
    name = data["name"]
    state = data["state"]
    try:
        admin = User.query.filter_by(username=name).first()
        if admin.roles == 0:
            return jsonify(code=RET.NO, message="操作失败")
        else:
            db.session.query(User).filter_by(id=admin.id).update({"state":state})
            db.session.commit()
            db.session.close()
            return jsonify(code=RET.OK, message="操作成功")
            
    except IntegrityError as e:
        # 数据库操作错误后回滚
        db.session.rollback()
        return jsonify(code=RET.DATAEXIST, message="获取失败")
    except Exception as e:
        current_app.logger.error(e)
    return jsonify(code=RET.DBERR, message="查询数据异常")
# 模糊搜索获取单用户列表
@admin_api.route("/admin_userSingleVague", methods=['POST'])
@Check_token_admin
def userSingleVague():
    data = request.get_json()
    user = data["username"]
    if not all([user]):
        return jsonify(code=RET.NO, message="参数不完整")
    try:
        paginate = User.query.filter(User.username.like(user + '%')).all()
        data = []
        for v in paginate: 
            userlists = {
                "id":v.id,
                "name":v.username,
                "roles":v.roles,
                "state":v.state,
                "createtime":v.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            data.append(userlists)
        return jsonify(code=RET.OK,message="获取用户信息成功",data=data)
    except IntegrityError as e:
        # 数据库操作错误后回滚
        db.session.rollback()
        return jsonify(code=RET.DATAEXIST, message="获取失败")
    except Exception as e:
        current_app.logger.error(e)
    return jsonify(code=RET.DBERR, message="查询数据异常")
# 单个查询用户-------------------------------------------------------------------------------
@admin_api.route("/admin_userSingle", methods=['POST'])
@Check_token_admin
def userSingle():
    from werkzeug.security import check_password_hash
    data = request.get_json()
    name = data["name"]
    if not all([name]):
        return jsonify(code=RET.NO, message="参数不完整")
    try:
        admin = User.query.filter_by(username=name).first()
        print(admin)
        userlists = {
            "id":admin.id,
            "name":admin.username,
            "roles":admin.roles,
            "state":admin.state,
            "email":admin.email,
            # "password":check_password_hash(admin.password),
            "avatar_url":admin.avatar_url,
            "createtime":admin.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        return jsonify(code=200,message="获取用户信息成功",data=userlists)
    except IntegrityError as e:
        # 数据库操作错误后回滚
        db.session.rollback()
        return jsonify(code=RET.DATAEXIST, message="获取失败")
    except Exception as e:
        current_app.logger.error(e)
    return jsonify(code=RET.DBERR, message="查询数据异常")
# 编辑用户
@admin_api.route("/admin_userEdit", methods=['PUT'])
@Check_token_admin
def userEdit():
    from werkzeug.security import generate_password_hash
    data = request.get_json()
    # id = g.user_id['user']['username']
    # print(id)
    username = data["name"]
    roles = data["roles"]
    state = data["state"]
    email = data["email"]
    password = data["password"]
    avatar_url = data["avatar_url"]
    if password == '':
        try:
            db.session.query(User).filter_by(username=username).update({"username":username, "state":state, "roles":roles,"email":email,"avatar_url":avatar_url})
            db.session.commit()
            db.session.close()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(code=RET.DBERR, message="获取用户信息失败")
        return jsonify(code=RET.OK, message="用户编辑成功",data=data)
    else:
        try:
            db.session.query(User).filter_by(username=username).update({"username":username,"password":generate_password_hash(password), "state":state, "roles":roles,"email":email,"avatar_url":avatar_url})
            db.session.commit()
            db.session.close()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(code=RET.DBERR, message="获取用户信息失败")
        return jsonify(code=RET.OK, message="用户编辑成功",data=data)
# 删除用户-----------------------------------------------------------------------------------
@admin_api.route("/admin_userDelete", methods=['DELETE'])
@Check_token_admin
def userDelete():
    data = request.get_json()
    id=data["id"]
    if not all([id]):
        return jsonify(code=RET.NO, message="参数不完整")
    try:
        admin = User.query.filter_by(id=id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, message="获取用户信息失败")
    if admin.roles == 0:
        return jsonify(code=RET.NO, message="无法删除",data=data)
    else:
        if admin.state == 2:
            return jsonify(code=RET.NO, message="无法删除",data=data)  
        else:
            try:
                db.session.query(User).filter_by(id=data["id"]).update({"is_delete":1, "delete_tiem":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                db.session.commit()
                db.session.close()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(code=RET.DBERR, message="删除失败")
            return jsonify(code=RET.OK, message="用户删除成功",data=data)
# 日志列表-----------------------------------------------------------------------------------
@admin_api.route("/admin_userJournal", methods=["POST"])
@Check_token_admin
def userJournal():
    data = request.get_json()
    currentPage = data["currentPage"]
    pageSize = data["pageSize"]
    try:
        # 反排序
        paginate = UserLog.query.filter().order_by(UserLog.create_time.desc()).paginate(int(currentPage), int(pageSize), False)
        # 正排序
        # paginate = UserLog.query.paginate(page=int(currentPage), per_page=int(pageSize), error_out=False, max_per_page=None)
        data = []
        for v in paginate.items: 
            userlists = {
                "id":v.id,
                "name_id":v.name_id,
                "request_type":v.request_type,
                "request_address":v.request_address,
                "request_link":v.request_link,
                "createtime":v.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            data.append(userlists)
        return jsonify(code=200,paginate=paginate.page,total=paginate.total, message="获取用户日志成功",data=data)
    except IntegrityError as e:
        # 数据库操作错误后回滚
        db.session.rollback()
        return jsonify(code=RET.DATAEXIST, message="获取失败")
    except Exception as e:
        current_app.logger.error(e)
    return jsonify(code=RET.DBERR, message="查询数据异常")
# 模糊搜索获取单用户日志列表
@admin_api.route("/admin_userJournalVague", methods=['POST'])
@Check_token_admin
# 首页用户数据--------------------------------------------------------------------------------
def userJournalVague():
    data = request.get_json()
    user = data["username"]
    if not all([user]):
        return jsonify(code=RET.NO, message="参数不完整")
    try:
        paginate = UserLog.query.filter(UserLog.name_id.like(user + '%')).all()
        data = []
        for v in paginate: 
            userlists = {
                "id":v.id,
                "name_id":v.name_id,
                "request_type":v.request_type,
                "request_address":v.request_address,
                "request_link":v.request_link,
                "createtime":v.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            data.append(userlists)
        return jsonify(code=RET.OK,message="获取用户信息成功",data=data)
    except IntegrityError as e:
        # 数据库操作错误后回滚
        db.session.rollback()
        return jsonify(code=RET.DATAEXIST, message="获取失败")
    except Exception as e:
        current_app.logger.error(e)
    return jsonify(code=RET.DBERR, message="查询数据异常")
@admin_api.route("/admin_userHomePage", methods=['GET'])
def userHomePage():
    # data = request.get_json()
    # user = data["username"]
    # if not all([user]):
    #     return jsonify(code=RET.NO, message="参数不完整")
    try:
        user = User.query.filter(User.is_delete == 0).all()
        log = UserLog.query.filter().all()
        data =  {
            "user":len(user),
            "information":0,
            "post":0,
            "views":len(log)
        }
        return jsonify(code=RET.OK,message="获取用户信息成功",data=data)
    except IntegrityError as e:
        # 数据库操作错误后回滚
        db.session.rollback()
        return jsonify(code=RET.DATAEXIST, message="获取失败")
    except Exception as e:
        current_app.logger.error(e)
    return jsonify(code=RET.DBERR, message="查询数据异常")
