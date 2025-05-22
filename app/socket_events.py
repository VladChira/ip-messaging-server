from app.chat import Chat
from . import socketio

from flask import request
from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import decode_token
from app import socketio
from app.database import chats
from typing import Any, Dict
import datetime

def get_socketio():
    from app import socketio
    return socketio

# Track online users: sid -> user_id
online_users: Dict[str, str] = {}

@socketio.on("connect")
def handle_connect(auth: Dict[str, Any]):
    """
    Handshake: authenticate JWT from auth, track online status,
    and broadcast presence update.
    """

    user_id = auth.get('userId')
    sid = request.sid
    online_users[sid] = user_id

    print(f'Client connected with id {user_id} and session id {sid}')

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
    print('Client joined chat')
    chat_id = data.get("chatId")
    sid = request.sid
    user_id = online_users.get(sid)
    chat = chats.get(chat_id)

    if not chat or not any(m.user_id == user_id for m in chat.members):
        emit("error", {"message": "Invalid chat or not a member"})
        return

    join_room(chat_id)
    
    # Client joined a chat, mark all current messages in the chat as seen by
    # this user
    newly_seen = chat.mark_all_as_seen(int(user_id))

    # If a message has been seen by all members of a group (or the other person in the one-on-one chat) 
    # AND it was not marked as seen before,
    # mark it now and emit the socket event that says the message has been seen
    for msg in newly_seen:
        emit(
            "mark_as_read",
            {"chatId": chat_id, "messageId": msg.message_id, "userId": user_id},
            room=chat_id
        )


@socketio.on("leave_chat")
def handle_leave_chat(data: Dict[str, Any]):
    """
    Client leaves a chat room.
    """
    chat_id = data.get("chatId")
    leave_room(chat_id)


@socketio.on("mark_as_read")
def handle_mark_as_read(data: Dict[str, Any]):
    print('Got a mark as read')
    chat_id = data.get("chatId")
    message_id = data.get("messageId")
    sid = request.sid
    user_id = online_users.get(sid)
    
    if not user_id:
        emit("error", {"message": "Not authenticated"})
        return
    
    chat: Chat = chats.get(chat_id)
    if not chat:
        emit("error", {"message": "Chat not found"})
        return
    
    if not any(m.user_id == user_id for m in chat.members):
        emit("error", {"message": "Not a member of chat"})
        return

    # 1. Mark it as read in in-memory store
    msg = chat.get_message_by_id(message_id)
    if user_id not in msg.seen_by:
        msg.seen_by.append(int(user_id))

    # 2. Broadcast a “message_read” event to all online members
    payload = {"chatId": chat_id, "messageId": message_id, "userId": user_id}
    for other_sid, uid in online_users.items():
        if any(m.user_id == uid for m in chat.members):
            socketio.emit("mark_as_read", payload, room=other_sid)


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
    print('Client sent a message')
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

    # Automatically mark the message as read for the sender
    msg.seen_by.append(int(user_id))

    # Emit to every connected sid whose user is in that set
    member_ids = {m.user_id for m in chat.members}
    for sid, uid in online_users.items():
        if uid in member_ids:
            # “room=sid” targets exactly that socket
            socketio.emit("message", payload, room=sid)
