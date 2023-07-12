from flask import Blueprint

bp = Blueprint('logs_bp', __name__)

from . import routes
