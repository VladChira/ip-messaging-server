from . import socketio


from flask import request
from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import decode_token
from app import socketio
from app.database import chats
from typing import Any, Dict

# Track online users: sid -> user_id
online_users: Dict[str, str] = {}

@socketio.on("connect")
def handle_connect(auth: Dict[str, Any]):
    """
    Handshake: authenticate JWT from auth, track online status,
    and broadcast presence update.
    """

    # token = auth.get("token")
    # if not token:
    #     return False  # reject
    
    # print(token)

    # try:
    #     decoded = decode_token(token)
    #     user_id = str(decoded["sub"])
    # except Exception:
    #     return False  # invalid token

    user_id = auth.get('userId')
    sid = request.sid
    online_users[sid] = user_id

    print(f'Client connected with id {user_id} and session id f{sid}')

    # Notify everyone that this user is online
    emit(
        "presence_update",
        {"userId": user_id, "status": "online"},
        broadcast=True,
    )


@socketio.on("disconnect")
def handle_disconnect():
    """
    Remove from online map and broadcast offline presence.
    """
    sid = request.sid
    user_id = online_users.pop(sid, None)
    if user_id:
        emit(
            "presence_update",
            {"userId": user_id, "status": "offline"},
            broadcast=True,
        )


@socketio.on("join_chat")
def handle_join_chat(data: Dict[str, Any]):
    """
    Client asks to join real-time updates for a chat room.
    """
    chat_id = data.get("chatId")
    sid = request.sid
    user_id = online_users.get(sid)
    chat = chats.get(chat_id)

    if not chat or not any(m.user_id == user_id for m in chat.members):
        emit("error", {"message": "Invalid chat or not a member"})
        return

    join_room(chat_id)


@socketio.on("leave_chat")
def handle_leave_chat(data: Dict[str, Any]):
    """
    Client leaves a chat room.
    """
    chat_id = data.get("chatId")
    leave_room(chat_id)


@socketio.on("started_typing")
def handle_started_typing(data: Dict[str, Any]):
    """
    Client signals typing start; broadcast to others in the room.
    """
    chat_id = data.get("chatId")
    sid = request.sid
    user_id = online_users.get(sid)
    if chat_id in chats:
        emit(
            "typing",
            {"chatId": chat_id, "userId": user_id, "typing": True},
            room=chat_id,
            include_self=False,
        )


@socketio.on("stopped_typing")
def handle_stopped_typing(data: Dict[str, Any]):
    """
    Client signals typing stop; broadcast to others in the room.
    """
    chat_id = data.get("chatId")
    sid = request.sid
    user_id = online_users.get(sid)
    if chat_id in chats:
        emit(
            "typing",
            {"chatId": chat_id, "userId": user_id, "typing": False},
            room=chat_id,
            include_self=False,
        )


@socketio.on("send_message")
def handle_send_message(data: Dict[str, Any]):
    """
    Receive a new message, persist it to in-memory store, then broadcast.
    Payload may include an optional tempId for client-side optimistic UI.
    """
    chat_id = data.get("chatId")
    text = data.get("text")
    temp_id = data.get("tempId")
    sid = request.sid
    user_id = online_users.get(sid)
    chat = chats.get(chat_id)

    if not user_id:
        emit("error", {"message": "Not authenticated"})
        return

    if not chat:
        emit("error", {"message": "Chat not found"})
        return

    if not any(m.user_id == user_id for m in chat.members):
        emit("error", {"message": "Not a member of chat"})
        return

    # Persist message
    msg = chat.add_message(user_id, text)
    payload = msg.to_dict()
    if temp_id is not None:
        payload["tempId"] = temp_id

    # Broadcast to all in the room
    emit("message", payload, room=chat_id)

