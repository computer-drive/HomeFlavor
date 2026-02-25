from flask import Blueprint, request, jsonify, session

bp = Blueprint('stats', __name__, url_prefix="/api/stats")

@bp.route("/today")
def get_today_stats():
    return jsonify({
        "order_count": 0,
        "total_sales": 0,
    })
