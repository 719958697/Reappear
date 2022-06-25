# coding:utf-8
from flask import Flask
from config import config_map
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler
from sqlalchemy.orm import scoped_session
from flask_cors import CORS

import redis
import logging

# 数据库
db =  SQLAlchemy()

# 创建redis连接对象
redis_store = None

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG) # 调试debug级
# 创建日志记录器，指名日志保存的路径，每个日志文件的最大大小，保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log",maxBytes=1024*1024*100,backupCount=10)
# 创建日志记录的格式
formatter = logging.Formatter("%(levelname)s %(filename)s:%(lineno)d%(message)s")
# 为刚创建的日志记录器设置日志格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日记录器
logging.getLogger().addHandler(file_log_handler)


# def register_blueprints(app):
#     from app.api.cms import create_cms
#     # from app.api.v1 import create_v1

#     create_cms(app)
#     # create_v1(app)

# 工厂模式
def create_app(config_name):
    """
    创建flask的应用对象 config_name: str 配置模式的模式名字 {"develop","product"}
    """
    app = Flask(__name__)

    # 根据配置模式的名字获取配置参数的类
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)

    # 使用app初始化db
    db.init_app(app)

    # 解决跨域的问题
    CORS(app)

    # 初始化redis工具
    global redis_store
    redis_store = redis.StrictRedis(
        host=config_class.REDIS_HOST, port=config_class.REDIS_PORT, password=config_class.CACHE_REDIS_PASSWORD)

    # 利用flask-session, 将session数据保存到redis中

    # Session(app)
    
    # 设置线程安全session
    scoped_session(app)

    #为flask补充csrf防护
    # CSRFProtect(app)

    # 注册蓝图
    # register_blueprints(app)
    from app.api.cms import create_cms
    from app.api.v1 import create_v1
    create_cms(app)
    create_v1(app)


    return app
