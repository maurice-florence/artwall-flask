"""
Ingest Blueprint.
Handles ENEX file uploads and data ingestion.
"""
from flask import Blueprint

ingest_bp = Blueprint('ingest', __name__)

from app.blueprints.ingest import routes
