from flask import request
from . import socketio

@socketio.on('connect')
def handle_connect():
    print(f'Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected')
