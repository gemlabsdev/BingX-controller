from flask import current_app

from ..main import bp


@bp.route('/')
def index():
    return current_app.send_static_file('index.html')


@bp.route('/assets/<path:path>')
def send_assets(path):
    return current_app.send_static_file(f'assets/{path}')
