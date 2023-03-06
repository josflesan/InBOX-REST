"""Web Server Gateway Interface"""

######################
# FOR PRODUCTION
######################
from src.app import app, socketio

if __name__ == "__main__":
    ##################
    # FOR DEVELOPMENT
    ##################
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, certfile='joflesan-ubuntu.local.pem', keyfile='joflesan-ubuntu.local-key.pem')