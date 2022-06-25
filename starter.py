# coding:utf-8

from app import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app.sqldb import DBManager

# 创建flask的应用对象 记得调式
app = create_app("develop")

manager = Manager(app)
Migrate(app, db)
manager.add_command("db", MigrateCommand)
manager.add_command('sql',DBManager)

if __name__ == "__main__":
    manager.run()