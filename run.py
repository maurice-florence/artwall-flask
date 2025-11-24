"""
WSGI Entry Point for the Flask Application.
Run this file to start the development server.
"""
import os
from app import create_app

# Create the Flask app instance using the factory
app = create_app()

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the development server
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config.get('DEBUG', False)
    )
