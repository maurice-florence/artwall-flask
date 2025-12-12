import os
from flask import Flask
from config import config_map
from app.extensions import csrf, login_manager


def create_app(config_name=None):
    """
    Application Factory for the Flask App.

    Args:
        config_name (str): The configuration environment name
                           (e.g., 'development', 'production').
                           Defaults to FLASK_ENV env var.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")

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
    login_manager.login_view = "auth.login"  # type: ignore[assignment]
    login_manager.login_message_category = "info"

    # User loader callback
    @login_manager.request_loader
    def load_user_from_request(request):
        """
        Load user from Firebase session cookie.
        """
        from firebase_admin import auth
        from app.models.user import User

        # Get the session cookie
        session_cookie = request.cookies.get("session")
        if not session_cookie:
            return None

        try:
            # Verify the session cookie
            # check_revoked=True ensures that if the user's session was revoked,
            # the cookie is considered invalid.
            decoded_claims = auth.verify_session_cookie(
                session_cookie, check_revoked=True
            )

            # Create User object
            uid = decoded_claims.get("uid")
            email = decoded_claims.get("email")
            # Firebase session cookies might not have display_name,
            # but we can try to get it if needed, or just use email/uid
            return User(uid=uid, email=email)

        except auth.InvalidSessionCookieError:
            # Session cookie is invalid, expired or revoked
            return None
        except Exception as e:
            app.logger.error(f"Error verifying session cookie: {e}")
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
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(projects_bp, url_prefix="/projects")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(ingest_bp, url_prefix="/ingest")

    # Endpoint registration debug removed to avoid terminal noise


def register_error_handlers(app):
    """
    Registers error handlers for common HTTP errors.
    """
    from flask import render_template

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500


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
        # Makes version info available in every template
        from app.utils.version_helper import get_git_info

        info = get_git_info()
        return dict(
            version=info["version"],
            commit_hash=info["commit_hash"],
            last_updated=info["last_updated"],
        )

    @app.context_processor
    def inject_firebase_config():
        return {
            "firebase_config": {
                "apiKey": os.environ.get("FIREBASE_API_KEY"),
                "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
                "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
                "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
                "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
                "appId": os.environ.get("FIREBASE_APP_ID"),
            }
        }

    # Register custom template filters
    from app.template_filters import register_filters

    register_filters(app)
