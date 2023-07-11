from flask import Blueprint

bp = Blueprint('credentials_bp', __name__)

from . import routes