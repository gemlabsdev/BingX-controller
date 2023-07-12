from flask import Blueprint

bp = Blueprint('trade_bp', __name__)

from . import routes
