import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base Configuration"""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-prod"
    SESSION_COOKIE_NAME = "flask_firebase_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Firebase Config
    FIREBASE_CREDENTIALS_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    FIREBASE_DATABASE_URL = os.environ.get("FIREBASE_DATABASE_URL")
    FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET")

    # Client-side Firebase Config
    FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")
    FIREBASE_AUTH_DOMAIN = os.environ.get("FIREBASE_AUTH_DOMAIN")
    FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID")
    FIREBASE_MESSAGING_SENDER_ID = os.environ.get("FIREBASE_MESSAGING_SENDER_ID")
    FIREBASE_APP_ID = os.environ.get("FIREBASE_APP_ID")

    # Upload limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP for localhost
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    # In production, we might enforce stricter cookie policies


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False  # Disable CSRF for easier API testing


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
