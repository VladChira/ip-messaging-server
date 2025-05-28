import datetime
from enum import Enum
import uuid
from app.chat_member import ChatMember
from app.message import Message
from typing import List, Optional

class ChatType(Enum):
    ONE_ON_ONE = "one_on_one"
    GROUP = "group"

class Chat:
    def __init__(self, chat_type, name=None):
        self.chat_id = str(uuid.uuid4())
        self.name = name if chat_type == ChatType.GROUP else None
        self.chat_type = chat_type
        self.created_at = datetime.datetime.now(datetime.UTC)
        self.members = []
        self.messages = []

    def add_member(self, user_id):
        if user_id not in [m.user_id for m in self.members]:
            member = ChatMember(user_id, self.chat_id)
            self.members.append(member)

    def add_message(self, sender_id, text):
        msg = Message(self.chat_id, sender_id, text)
        self.messages.append(msg)
        return msg

    def get_member(self, user_id: str) -> Optional[ChatMember]:
        """Get a specific member by user ID"""
        return next((m for m in self.members if m.user_id == user_id), None)

    def mark_message_seen(self, user_id: str, message: Message):
        """
        Mark a single message as seen by user.
        Returns True if newly marked, False if already present.
        """
        if user_id == message.sender_id:
            return False  # sender doesn't count
        if user_id not in message.seen_by:
            message.seen_by.append(int(user_id))
            return True
        return False
    
    def mark_all_as_seen(self, user_id: str):
        """
        Mark all current messages in chat as seen by this user.
        Returns list of messages newly marked.
        """
        newly_seen = []
        for msg in self.messages:
            if self.mark_message_seen(user_id, msg):
                newly_seen.append(msg)
        return newly_seen

    def get_unread_count(self, user_id: str) -> int:
        """
        Count how many messages in this chat:
          - were not sent by `user_id`, and
          - have not yet been seen by `user_id`.
        """
        count = 0
        for msg in self.messages:
            # skip messages I sent
            if msg.sender_id == int(user_id):
                continue
            # if my ID is not yet in seen_by, it’s unread
            if int(user_id) not in msg.seen_by and str(user_id) not in msg.seen_by:
                count += 1
        return count

    def get_last_message(self) -> Optional[Message]:
        """Get the last message in the chat"""
        return self.messages[-1] if self.messages else None

    def get_members(self):
        return [m.to_dict() for m in self.members]

    def get_messages(self):
        return [m.to_dict() for m in self.messages]
    
    def get_message_by_id(self, messageId):
        for msg in self.messages:
            if msg.message_id == messageId:
                return msg

    def to_dict(self, user_id: str = None):
        """Convert to dict with optional unread count for specific user"""
        base_dict = {
            "chatId": self.chat_id,
            "name": self.name,
            "chatType": self.chat_type.value,
            "createdAt": self.created_at.isoformat()
        }
        
        if user_id:
            base_dict["unreadCount"] = self.get_unread_count(user_id)
            last_message = self.get_last_message()
            if last_message:
                base_dict["lastMessage"] = last_message.to_dict()
        
        return base_dict
