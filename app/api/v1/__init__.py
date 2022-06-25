from flask import Blueprint


def create_v1(app):
    # 导入蓝图的视图
    from app.api.v1.user import dy_api

    app.register_blueprint(dy_api, url_prefix="/v1/user")
    
    return app

