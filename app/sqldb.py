from app import db,models
from flask_script import Manager
from app.models import User
from sqlalchemy.exc import IntegrityError

DBManager = Manager()

@DBManager.command
def init():
    user = User(
        username="admin",
        roles = 0,
        state = 0,
        is_delete = 0,
        delete_tiem = "0000-00-00 00:00:00",
        generate_password = "123456",
        avatar_url = "https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif"
        )
    try:
        db.session.add(user)
        db.session.commit()
        db.session.close()
    except IntegrityError as e:
        # 数据库操作错误后回滚
        db.session.rollback()
        return print('数据库初始化失败')
    except Exception as e:
        return print('数据库异常')
    # 返回结果
    return print('数据库初始化完成')
    

@DBManager.command
def migrate():
    print ('数据表迁移成功')