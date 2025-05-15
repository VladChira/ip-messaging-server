import datetime
import uuid

class Message:
    def __init__(self, chat_id, sender_id, text):
        self.message_id = str(uuid.uuid4())
        self.chat_id = chat_id
        self.sender_id = sender_id
        self.text = text
        self.sent_at = datetime.utcnow()

    def to_dict(self):
        return {
            "messageId": self.message_id,
            "chatId": self.chat_id,
            "senderId": self.sender_id,
            "text": self.text,
            "sentAt": self.sent_at.isoformat()
        }
