import logging
from flask import Flask
from .const import *
from datetime import datetime
import os

def setup_logger(app: Flask):
    '''
    设置日志记录器。
    可能的问题：
        LOG_PATH 不存在可能抛出异常，但在实际使用时，会在调用该函数前运行 init_files 函数，确保 LOG_PATH 存在。
    Arguments:
        app: Flask 当前的Flask应用实例。
    Returns:
        Logger: 配置好的日志记录器实例。
    '''
    # 设置日志记录器

    logger = app.logger
    
    # 清除默认的处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

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
    
    app.logger = logger # type: ignore  

    return logger
