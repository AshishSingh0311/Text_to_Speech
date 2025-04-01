import os
import logging

from flask import Flask

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Import routes after app creation to avoid circular imports
from routes import register_routes

# Register routes with the app
register_routes(app)

# Create upload directory for audio files if it doesn't exist
upload_dir = os.path.join(app.root_path, 'static', 'audio')
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)
