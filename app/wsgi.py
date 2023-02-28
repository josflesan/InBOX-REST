"""Web Server Gateway Interface"""

######################
# FOR PRODUCTION
######################
from src.app import app, socketio

if __name__ == "__main__":
    ##################
    # FOR DEVELOPMENT
    ##################
    socketio.run(app, debug=True)