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
firebase_service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
logger.info(
    "FIREBASE_SERVICE_ACCOUNT_JSON environment variable value: %s",
    "<SET>" if firebase_service_account_json else "<NOT SET>",
)

if firebase_service_account_json:
    try:
        # Parse the JSON string from the environment variable
        service_account_info = json.loads(firebase_service_account_json)
        # Initialize Firebase using the parsed dictionary
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred)
        logger.info(
            "Firebase initialized successfully using environment variable content!"
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
else:
    logger.error(
        "FIREBASE_SERVICE_ACCOUNT_JSON environment variable is NOT SET. Firebase will not be initialized."
    )
# --- END NEW APPROACH ---

# Create the Flask app instance using the factory
app = create_app()

if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))

    # Run the development server
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))
