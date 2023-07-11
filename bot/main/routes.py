from flask import current_app

from ..main import bp


@bp.route('/')
def index():
    return current_app.send_static_file('index.html')
