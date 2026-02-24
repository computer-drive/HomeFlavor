from flask import Blueprint, render_template, current_app

bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    return render_template('index.html',
                           title=current_app.config["title"])

@bp.route('/login')
def login():
    return render_template('login.html',
                           title=current_app.config["title"])