import logging
from flask import Flask
from .const import *
from datetime import datetime
import os

def setup_logger(app: Flask):
    '''
    设置日志记录器。
    Arguments:
        app: Flask 当前的Flask应用实例。
    Returns:
        Logger: 配置好的日志记录器实例。
    '''
    # 设置日志记录器
    logger = logging.getLogger(__name__)

    # 设置日志级别
    level = logging.DEBUG if app.config["DEBUG"] else logging.INFO
    logger.setLevel(level)

    # 设置日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )

    # 设置控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 设置文件处理器
    ## 获取当前日期
    date = datetime.now().strftime('%Y-%m-%d')
    
    file_handler = logging.FileHandler(os.path.join(LOG_PATH, f'{date}.log'), encoding=DEFAULT_ENCODING)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    app.logger = logger

    return logger
