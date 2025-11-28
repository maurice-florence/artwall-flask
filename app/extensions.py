"""
Flask Extensions Initialization.
Extensions are initialized here but bound to the app in __init__.py
"""

from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

# CSRF Protection
csrf = CSRFProtect()

# Login Manager for session-based authentication
login_manager = LoginManager()

# Placeholder for database (not used with Firebase, but kept for future flexibility)
db = None
auth = None
