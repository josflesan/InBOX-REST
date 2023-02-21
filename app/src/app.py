"""Flask Application"""

# Load libraries
from flask import Flask, jsonify
import sys

# Load modules
from src.endpoints.blueprint_deliveries import blueprint_deliveries

# Initialize Flask app
app = Flask(__name__)

# Register blueprints, ensuring paths are versioned
app.register_blueprint(blueprint_deliveries, url_prefix="/api/v1/deliveries")