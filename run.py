from app import create_app, socketio
from app import application

if __name__ == "__main__":
    create_app()

    socketio.run(application, host='0.0.0.0', port=5000)
