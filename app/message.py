import datetime
from typing import List
import uuid

class Message:
    def __init__(self, chat_id, sender_id, text):
        self.message_id = str(uuid.uuid4())
        self.chat_id = chat_id
        self.sender_id = sender_id
        self.text = text
        self.sent_at = datetime.datetime.now(datetime.UTC)
        self.seen_by: List[int] = []

    def to_dict(self):
        return {
            "messageId": self.message_id,
            "chatId": self.chat_id,
            "senderId": self.sender_id,
            "text": self.text,
            "sentAt": self.sent_at.isoformat(),
            "seenBy": self.seen_by,
        }
