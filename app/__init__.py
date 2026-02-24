from flask import Flask, current_app, request, redirect
import os
from .const import *
import json
from .config import load_config
from .log import setup_logger
from .crash import handle_crash_report
from .database import init_test_data, reset_db
import sqlite3
import importlib
from .auth import check_login

def init_files():
    '''
    检查必要的文件和目录是否存在，如果不存在则创建它们。
    
    Arguments:
        None
    Returns:
        None
    '''

    
    
    os.makedirs('user', exist_ok=True)
    os.makedirs(LOG_PATH, exist_ok=True)

    # 判断实例配置文件是否存在，如果不存在则创建它
    if not os.path.exists(INSTANCE_CONFIG_PATH):
        with open(INSTANCE_CONFIG_PATH, 'w') as f:
            json.dump({}, f, indent=4)

    
    os.makedirs(CRASH_REPORT_PATH, exist_ok=True)
        
def init_databse():
    '''
    初始化数据库。
    '''
    # 连接数据库
    conn = sqlite3.connect(current_app.config['database']["file"])
    cursor = conn.cursor()

    # 执行SQL脚本初始化数据库
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding=DEFAULT_ENCODING) as f:
        schema = f.read()

    # 执行SQL脚本
    cursor.executescript(schema)
    conn.commit()

    # 关闭数据库连接
    conn.close()


def create_app():
    '''
    应用工厂函数，创建并配置Flask应用实例。
    可能抛出的异常：
        Runtime Error: 配置文件加载失败时抛出
    Arguments:
        None
    Returns:
        Flask: 配置好的Flask应用实例。
    '''
    # 初始化必要的文件和目录
    init_files()

    # 创建flask应用实例
    app = Flask(__name__, template_folder="templates")

    # 加载配置
    result = load_config(app)
    if result: # 若加载失败，则返回非None
        code, message = result
        handle_crash_report(code, message)
        raise RuntimeError(f"({code}){message}")
    
    # 初始化数据库
    with app.app_context():
        init_databse()

    # 设置日志记录器
    setup_logger(app)

    # 注册CLI命令
    @app.cli.command("init-test-data")
    def init_test_data_cli():
        init_test_data()
    
    @app.cli.command("reset-db")
    def reset_db_cli():
        reset_db()

    # 注册蓝图
    blueprints = [
        "basic",
        "auth"
    ]

    # 设置session 的secret_key
    app.config['SECRET_KEY'] = os.urandom(24)  # 生成随机密钥

    # before_request 检查登录
    @app.before_request
    def before_request():

        if not check_login(request.path):
            return redirect("/login")
        

    for blueprint_name in blueprints:
        blueprint_module = importlib.import_module(f".{blueprint_name}", __name__)
        app.register_blueprint(blueprint_module.bp)
        app.logger.info(f"Blueprint {blueprint_name} registered.")


    return app


