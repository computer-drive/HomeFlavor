from flask import Blueprint, request, jsonify, session

bp = Blueprint('user', __name__, url_prefix="/api/user")

@bp.route("/current")
def get_current_user():
    if 'id' in session:
        return jsonify({
            "type": "success",
            "data": dict(session)
        })
    else:
        return jsonify({
            "type": "unauthorized",
            "message": "User not logged in."
        })