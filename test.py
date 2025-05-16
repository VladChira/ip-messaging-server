from typing import Any, Dict
import eventlet
eventlet.monkey_patch()

from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', path="/messaging-api")

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Welcome!'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')

@socketio.on('send_message')
def handle_disconnect(data: Dict[str, Any]):
    print(f'Client sent message')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
