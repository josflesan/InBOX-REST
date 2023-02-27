"""Flask Application"""

# Load libraries
from datetime import timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

# Load modules
from src.endpoints.blueprint_deliveries import blueprint_deliveries
from src.endpoints.blueprint_register import blueprint_register

# Initialize Flask app
app = Flask(__name__)
cors = CORS(app)
app.config["SECRET_KEY"] = "secret!"  #TODO: Change this
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)
app.config["JWT_SECRET_KEY"] = "super-secret"  #TODO: Change this
jwt = JWTManager(app)
socketio = SocketIO(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Register blueprints, ensuring paths are versioned
app.register_blueprint(blueprint_deliveries, url_prefix="/api/v1/deliveries")
app.register_blueprint(blueprint_register, url_prefix="/api/v1/")