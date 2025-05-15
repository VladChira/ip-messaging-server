import datetime
from enum import Enum
import uuid
from app.chat_member import ChatMember
from app.message import Message

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

    def get_members(self):
        return [m.to_dict() for m in self.members]

    def get_messages(self):
        return [m.to_dict() for m in self.messages]

    def to_dict(self):
        return {
            "chatId": self.chat_id,
            "name": self.name,
            "chatType": self.chat_type.value,
            "createdAt": self.created_at.isoformat()
        }
