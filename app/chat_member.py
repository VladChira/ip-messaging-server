import datetime
from typing import Optional

class ChatMember:
    def __init__(self, user_id, chat_id):
        self.user_id = user_id
        self.chat_id = chat_id
        self.joined_at = datetime.datetime.now(datetime.UTC)
        self.last_read_message_id: Optional[str] = None
        self.last_read_at: Optional[datetime.datetime] = None

    def mark_as_read(self, message_id: str):
        """Mark messages as read up to the given message ID"""
        self.last_read_message_id = message_id
        self.last_read_at = datetime.datetime.now(datetime.UTC)

    def to_dict(self):
        return {
            "userId": self.user_id,
            "chatId": self.chat_id,
            "joinedAt": self.joined_at.isoformat(),
            "lastReadMessageId": self.last_read_message_id,
            "lastReadAt": self.last_read_at.isoformat() if self.last_read_at else None
        }