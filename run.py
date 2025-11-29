"""
WSGI Entry Point for the Flask Application.
Run this file to start the development server.
"""

import os

import firebase_admin
from firebase_admin import credentials
import logging
from app import create_app

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the path from the environment variable
firebase_credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
logger.info(
    f"FIREBASE_CREDENTIALS_PATH environment variable value: {firebase_credentials_path}"
)

if firebase_credentials_path:
    if os.path.exists(firebase_credentials_path):
        logger.info(f"File EXISTS at: {firebase_credentials_path}")
        if os.access(firebase_credentials_path, os.R_OK):
            logger.info(f"File is READABLE at: {firebase_credentials_path}")
            try:
                # Attempt to initialize Firebase
                cred = credentials.Certificate(firebase_credentials_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized successfully!")
            except Exception as e:
                logger.error(f"ERROR initializing Firebase: {e}", exc_info=True)
        else:
            logger.error(
                f"File exists but is NOT READABLE at: {firebase_credentials_path}"
            )
    else:
        logger.error(f"File DOES NOT EXIST at: {firebase_credentials_path}")
else:
    logger.error("FIREBASE_CREDENTIALS_PATH environment variable is NOT SET.")

# Create the Flask app instance using the factory
app = create_app()

if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))

    # Run the development server
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))
