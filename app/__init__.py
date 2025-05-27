import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from dotenv import load_dotenv
import os

from app.database import create_users
from app.database import create_friendships
from app.database import create_friend_requests
from app.database import create_chats


from app.routes import register_routes

application = Flask(__name__)
CORS(application, origins="*")

 # Configurare JWT
application.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-in-production")
application.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=5)

socketio = SocketIO(application, cors_allowed_origins="*", async_mode='eventlet', path='/messaging-api/socket.io')
jwt = JWTManager(application)

def create_app():
    create_users()
    create_friendships()
    create_friend_requests()
    # create_chats()

    load_dotenv()

    # ensure our socket handlers get registered
    import app.socket_events  

    register_routes(application)