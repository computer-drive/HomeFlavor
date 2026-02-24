from flask import Blueprint, current_app, request, jsonify, session
from .database import get_dbconn
from .const import *

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/login', methods=['POST']) # type: ignore
def login():

    # 获取数据
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 判断是否为空
    if not username or not password:
        return jsonify(
            {
                "type": "none_error",
                "message": "username or password is empty"
            }
        )
    
    # 判断此人是否已登录
    if 'id' in session:
        return jsonify(
            {
                "type": "duplicate_error",
                "message": "user is login"
            }
        )
    # 数据库检验
    db = get_dbconn()
    user = db.users.auth(username, password)

    db.close()

    # 判断是否存在
    print("用户：",user)
    if user:
        
        # 存在，判断是否被封禁
        if user['enabled']:
            # 更新session
            session.clear()
            session['id'] = user['id']
            session['username'] = user['username']
            session["is_admin"] = user['is_admin']
            
            return jsonify(
                {
                    "type": "success",
                    "message": "login success"
                }
            )
        else:
            return jsonify(
                {
                    "type": "banned_error",
                    "message": "user is banned"
                }
            )
    else:
        return jsonify(
            {
                "type": "auth_error",
                "message": "username or password is wrong"
            }
        )

@bp.route('/logout', methods=['POST']) # type: ignore
def logout():
    if 'id' in session:
        session.clear()
        return jsonify(
            {
                "type": "success",
                "message": "logout success"
            }
        )
    else:
        return jsonify(
            {
                "type": "none_error",
                "message": "user is not login"
            }
        )
    
def check_login(url):
    # 判断是否在白名单中
    for item in UNLOGIN_WHITELIST:
        if item in url:
            return True
    
    # 判断是否登录
    if 'id' in session:
        return True
    else:
        return False


    


