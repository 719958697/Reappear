# coding:utf-8
import redis


class Config(object):
    """配置信息"""

    SECRET_KEY = "LUOFENGCHENG"

    # 数据库
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost:3306/luo_flask"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://luo_flask_test:luo0520@175.178.223.108:3306/luo_flask_test"

    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis
    REDIS_HOST = "175.178.223.108"
    REDIS_PORT = 6379
    CACHE_REDIS_PASSWORD = 'luo0520'
    # CACHE_REDIS_DB = 0

    # flask-session配置
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=CACHE_REDIS_PASSWORD)
    SESSION_USE_SIGNER = True  # 对cookie中session_id进行隐藏处理
    PERMANENT_SESSION_LIFETIME = 865400  # session数据的有效期，单位秒


class DevelopmentConfig(Config):
    """开发模式的配置信息"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置信息"""
    pass


config_map = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig
}
