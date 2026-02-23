import json
from flask import Flask
from .const import *
import os


def load_config(app: Flask) -> None | tuple[int, str]:
    '''
    加载配置文件。
    Arguments:
        app: Flask 当前的Flask应用实例。
    Returns:
        None 无返回值，设置成功
        Tuple[int, str] 加载失败时返回错误代码和错误信息。
    '''
    # 获取ENVIRONMENT环境变量
    env = os.getenv("ENVIRONMENT", "development").lower()

    # 加载默认配置
    try:
        with open(DEFAULT_CONFIG_PATH, encoding=DEFAULT_ENCODING, mode='r') as f:
            config = json.load(f)
    except FileNotFoundError:
        return (101, "Default configuration file not found.")
    except json.JSONDecodeError:
        return (102, "Default configuration file is not a valid JSON file.")

    # 加载生产环境配置
    try:
        if env == "production":
            with open(PRODUCTION_CONFIG_PATH, encoding=DEFAULT_ENCODING, mode='r') as f:
                prod_config = json.load(f)
                config.update(prod_config)
    except FileNotFoundError:
        return (103, "Production configuration file not found.")

    # 加载实例配置
    try:
        with open(INSTANCE_CONFIG_PATH, encoding=DEFAULT_ENCODING, mode='r') as f:
            instance_config = json.load(f)
            config.update(instance_config)
    except FileNotFoundError:
        return (104, "Instance configuration file not found.")
    except json.JSONDecodeError:
        return (105, "Instance configuration file is not a valid JSON file.")


    # 初始化基本配置
    ## 设置env=环境变量
    config["env"] = env

    ## 设置debug=环境变量
    config["DEBUG"] = config["server"]["debug"] 

    app.config.update(config)

