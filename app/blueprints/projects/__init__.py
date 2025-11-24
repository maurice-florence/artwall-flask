"""
Projects Blueprint.
Handles project-related routes and CRUD operations.
"""
from flask import Blueprint

projects_bp = Blueprint('projects', __name__)

from app.blueprints.projects import routes
