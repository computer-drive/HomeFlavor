from flask import Flask
import os
from .const import *
import json
from .config import load_config
from .log import setup_logger
from .crash import handle_crash_report

def init_files():
    '''
    检查必要的文件和目录是否存在，如果不存在则创建它们。
    Arguments:
        None
    Returns:
        None
    '''
    # 检查user目录是否存在
    if not os.path.exists('user'):
        os.makedirs('user')

    # 检查日志目录是否存在
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)

    # 判断实例配置文件是否存在，如果不存在则创建一个空的配置文件
    if not os.path.exists(INSTANCE_CONFIG_PATH):
        with open(INSTANCE_CONFIG_PATH, 'w') as f:
            json.dump({}, f, indent=4)

    # 判断崩溃报告目录是否存在，如果不存在则创建它
    if not os.path.exists(CRASH_REPORT_PATH):
        os.makedirs(CRASH_REPORT_PATH)
        
    
def create_app():
    '''
    应用工厂函数，创建并配置Flask应用实例。
    Arguments:
        None
    Returns:
        Flask: 配置好的Flask应用实例。
    '''
    # 初始化必要的文件和目录
    init_files()

    # 创建flask应用实例
    app = Flask(__name__)

    # 加载配置
    result = load_config(app)
    if result: # 若加载失败，则返回非None
        code, message = result
        handle_crash_report(code, message)
        exit(int(code))

    # 设置日志记录器
    setup_logger(app)

    # 注册蓝图
    ## TODO

    return app


