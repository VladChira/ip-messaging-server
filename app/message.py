import datetime
import uuid

class Message:
    def _init_(self, chat_id, sender_id, text):
        self.message_id = str(uuid.uuid4())
        self.chat_id = chat_id
        self.sender_id = sender_id
        self.text = text
        self.sent_at = datetime.datetime.now(datetime.UTC)
        self.is_read = False  # New field to track read status
    
    def mark_as_read(self):
        """Mark this message as read"""
        self.is_read = True
    
    def to_dict(self):
        return {
            "messageId": self.message_id,
            "chatId": self.chat_id,
            "senderId": self.sender_id,
            "text": self.text,
            "sentAt": self.sent_at.isoformat(),
            "isRead": self.is_read  # Include read status in the response
        }