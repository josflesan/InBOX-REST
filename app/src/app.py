"""Flask Application"""

# Load libraries
from flask import Flask, jsonify
from flask_cors import CORS
import sys

# Load modules
from src.endpoints.blueprint_deliveries import blueprint_deliveries

# Initialize Flask app
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Register blueprints, ensuring paths are versioned
app.register_blueprint(blueprint_deliveries, url_prefix="/api/v1/deliveries")