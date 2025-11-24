import os
import sys
from pathlib import Path
from flask import Flask
from config import config_map
from app.extensions import db, auth, csrf, login_manager

# Add project root to path for version import
sys.path.insert(0, str(Path(__file__).parent.parent))
from version import get_version_string

def create_app(config_name=None):
    """
    Application Factory for the Flask App.
    
    Args:
        config_name (str): The configuration environment name 
                           (e.g., 'development', 'production').
                           Defaults to FLASK_ENV env var.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    
    # Load Configuration
    if config_name not in config_map:
        raise ValueError(f"Invalid config name: {config_name}")
    app.config.from_object(config_map[config_name])

    # Initialize Extensions
    # Note: We initialize them here with the 'app' instance
    initialize_extensions(app)

    # Register Blueprints
    register_blueprints(app)

    # Register Error Handlers
    register_error_handlers(app)

    # Register Context Processors
    register_context_processors(app)

    return app

def initialize_extensions(app):
    """
    Initializes Flask extensions and Firebase Admin SDK.
    """
    # CSRF Protection for all POST requests
    csrf.init_app(app)
    
    # Login Manager for Session Management
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # type: ignore[assignment]
    login_manager.login_message_category = 'info'
    
    # User loader callback
    @login_manager.user_loader
    def load_user(user_id):
        # TODO: Implement user loading from Firebase
        # For now, return None until User model is implemented
        return None
    
    # Firebase Initialization
    # We use a helper in extensions.py to handle the singleton nature of Firebase
    from app.services.firebase_service import init_firebase
    init_firebase(app)

def register_blueprints(app):
    """
    Registers the modular blueprints (routes).
    """
    from app.blueprints.main import main_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.projects import projects_bp
    from app.blueprints.api import api_bp
    from app.blueprints.ingest import ingest_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(ingest_bp, url_prefix='/ingest')

def register_error_handlers(app):
    """
    Registers error handlers for common HTTP errors.
    """
    from flask import render_template
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

def register_context_processors(app):
    """
    Injects global variables into all Jinja templates.
    """
    @app.context_processor
    def inject_user():
        # Makes 'current_user' available in every template
        from flask_login import current_user
        return dict(current_user=current_user)
    
    @app.context_processor
    def inject_version():
        # Makes 'version' available in every template
        return dict(version=get_version_string())
    
    # Register custom template filters
    from app.template_filters import register_filters
    register_filters(app)