"""
WSGI Entry Point for the Flask Application.
Run this file to start the development server.
"""

import os
import firebase_admin
from firebase_admin import credentials
import logging
import json  # Import the json library
from app import create_app

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- NEW APPROACH FOR FIREBASE INITIALIZATION ---
firebase_config_json = os.getenv("FIREBASE_CONFIG")
logger.info(
    "FIREBASE_CONFIG environment variable value: %s",
    "<SET>" if firebase_config_json else "<NOT SET>",
)

if firebase_config_json and not firebase_admin._apps:
    try:
        # Parse the JSON string from the environment variable
        service_account_info = json.loads(firebase_config_json)
        # Initialize Firebase using the parsed dictionary
        cred = credentials.Certificate(service_account_info)
        db_url = os.getenv("FIREBASE_DATABASE_URL")
        if db_url:
            firebase_admin.initialize_app(cred, {"databaseURL": db_url})
            logger.info(
                "Firebase initialized successfully using environment variable content with databaseURL."
            )
        else:
            logger.warning(
                "FIREBASE_DATABASE_URL not set. Deferring Firebase initialization to app factory (firebase_service)."
            )
    except json.JSONDecodeError as e:
        logger.error(
            f"ERROR: Could not decode Firebase service account JSON from environment variable: {e}",
            exc_info=True,
        )
    except Exception as e:
        logger.error(
            f"ERROR initializing Firebase from environment variable: {e}", exc_info=True
        )
elif firebase_admin._apps:
    logger.info("Firebase already initialized. Skipping run.py initialization.")
else:
    logger.error(
        "FIREBASE_CONFIG environment variable is NOT SET. Firebase will not be initialized."
    )
# --- END NEW APPROACH ---

# Create the Flask app instance using the factory
app = create_app()

if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))

    # Run the development server
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))
