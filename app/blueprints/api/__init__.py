"""
API Blueprint.
Handles HTMX fragment requests for dynamic content loading.
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

from app.blueprints.api import routes
