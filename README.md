# luo_flask_Reappear
以学习为主的自主编写flask后端系统开发

环境安装:
1---安装Python环境(3.6+)

起步:
1---安装依赖包输入:pip install -r requirements.txt
    在项目的根目录调用环境中的 pip 来安装依赖包

数据库基础配置安装：
2---配置基础数据库模型输入:
    1.python starter.py db init
    2.python starter.py db migrate -m 'init tables'
    3.python starter.py db upgrade
    (注意:如果要重新输入命令需要把 migrations 文件夹 + 数据库表中的 alembic_version 表删除，重新初始化数据库并更新；(可以保存原来的数据库表中的数据))
    
初始化：
如果您是第一次使用，需要初始化数据库。
请先进入项目根目录，然后执行：python starter.py sql init,用来添加超级管理员 admin(默认密码 123456), 以及新建其他必要的分组

启动程序:
1---启动命令输入:python starter.py runserver
2---多线程启动命令：python starter.py runserver --threaded

项目结构:
|app---------------------项目总目录
|   |api-----------------业务逻辑总模块t
|   |   |cms-------------业务逻辑
|   |   |   |__init__----路由蓝图
|   |   |   |user.py-----设计蓝图
|   |lib-----------------扩展第三方包目录
|   |util----------------工具目录
|   |__init__------------位置文件
|   |logs----------------日志文件
|config------------------配置文件
|starter.py--------------启动页面

测试上传git
