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

def list_for_user(user_id):
    return [
        chat
        for chat in chats.values()
        if any(member.user_id == user_id for member in chat.members)
    ]

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

    # auto-join every room the user belongs to:
    user_chats = list_for_user(user_id)
    for chat in user_chats:
        join_room(chat.chat_id)


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

    # Mark all existing messages in that chat as seen by this user:
    newly_seen = chat.mark_all_as_seen(user_id)

    # Broadcast a `mark_as_read` event to everyone in that chat:
    for msg in newly_seen:
        payload = {
          "chatId":   chat_id,
          "messageId": msg.message_id,
          "userId":    user_id,
        }
        socketio.emit("mark_as_read", payload, room=chat_id)


@socketio.on("leave_chat")
def handle_leave_chat(data: Dict[str, Any]):
    """
    Client leaves a chat room.
    """
    chat_id = data.get("chatId")
    leave_room(chat_id)


@socketio.on("mark_as_read")
def handle_mark_as_read(data):
    chat_id    = data["chatId"]
    message_id = data["messageId"]
    user_id    = online_users.get(request.sid)
    chat       = chats.get(chat_id)

    if not chat or user_id not in {m.user_id for m in chat.members}:
        return emit("error", {"message": "Invalid chat or not a member"})

    msg = chat.get_message_by_id(message_id)
    if user_id not in msg.seen_by:
        msg.seen_by.append(user_id)

        payload = {
        "chatId":    chat_id,
        "messageId": message_id,
        "userId":    user_id,
        }
        # broadcast to the entire chat room:
        socketio.emit("mark_as_read", payload, room=chat_id)



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


@socketio.on("force_refresh")
def handle_force_refresh(data: Dict[str, Any]):
    """
    Receives a force_refresh event and re-emits it to all online members of the specified chat.
    The client is expected to send a payload containing `chatId`.
    Example payload: {"chatId": "some_chat_id"}
    """

    print("Got a refresh event")

    chat_id = data.get("chatId")
    sid = request.sid
    user_id_str = online_users.get(sid)  # user_id from online_users is str

    # Authentication check: user must be connected and in online_users
    if not user_id_str:
        emit("error", {"message": "Not authenticated"})
        return

    # Validate that chatId is provided in the payload
    if not chat_id:
        emit("error", {"message": "chatId is required in payload"})
        return

    chat: Chat = chats.get(chat_id)
    
    # Validate chat existence
    if not chat:
        emit("error", {"message": "Chat not found"})
        return
    
    member_ids = {m.user_id for m in chat.members}
    for sid, uid in online_users.items():
        print(member_ids)
        if uid in member_ids:
            # “room=sid” targets exactly that socket
            socketio.emit("force_refresh", {"chatId": chat.chat_id}, room=sid)
    
    # Validate membership of the sender in the chat.
    # Assuming chat.members store user_id as int, based on int(user_id)
    # casts in other handlers (e.g., chat.mark_all_as_seen(int(user_id))).
    # try:
    #     user_id_int = int(user_id_str)
    # except ValueError:
    #     # This should ideally not happen if user IDs in online_users are always integer-like strings
    #     emit("error", {"message": "Invalid user ID format for sender"})
    #     print(f"Error: User {user_id_str} (sid: {sid}) has an invalid user ID format.")
    #     return
        
    # if not any(member.user_id == user_id_int for member in chat.members):
    #     emit("error", {"message": "Not a member of this chat"})
    #     return

    # # The payload to re-emit. "Re-emits it" suggests using the original data.
    # payload_to_emit = data 

    # # Identify all online members of this specific chat.
    # # Chat member IDs are assumed to be integers.
    # chat_member_ids_int = {member.user_id for member in chat.members}

    # # Iterate through all globally online users.
    # for other_sid, other_user_id_str in online_users.items():
    #     try:
    #         # Convert the string user ID from online_users to int for comparison
    #         other_user_id_int = int(other_user_id_str)
    #     except ValueError:
    #         # Log and skip if an online user has an invalid ID format
    #         print(f"Warning: Invalid user ID format '{other_user_id_str}' for SID {other_sid} in online_users. Skipping for force_refresh.")
    #         continue

    #     # Check if this online user is a member of the target chat
    #     if other_user_id_int in chat_member_ids_int:
    #         # Emit the event to this specific online member of the chat.
    #         # This targets the specific socket connection (sid) of the user.
    #         # The original sender will also receive this event if they are an online member.
    #         socketio.emit("force_refresh", payload_to_emit, room=other_sid)
    
    print(f"User {user_id_str} (sid: {sid}) initiated force_refresh for chat {chat_id}. Event re-emitted to relevant online members.")