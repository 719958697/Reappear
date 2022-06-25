from flask import Blueprint


def create_cms(app):
    # 导入蓝图的视图
    from app.api.cms.user import user_api
    from app.api.cms.admin import admin_api

    app.register_blueprint(user_api, url_prefix="/cms/user")
    app.register_blueprint(admin_api, url_prefix="/cms/admin")
    
    return app

