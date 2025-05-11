from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os

from app.database import create_users
from app.database import create_friendships
from app.database import create_friend_requests

from app.routes import register_routes

socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    create_users()
    create_friendships()
    create_friend_requests()

    load_dotenv()

    app = Flask(__name__)
    socketio.init_app(app)

    register_routes(app)
    return app
