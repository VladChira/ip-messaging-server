import datetime

class ChatMember:
    def __init__(self, user_id, chat_id):
        self.user_id = user_id
        self.chat_id = chat_id
        self.joined_at = datetime.datetime.now(datetime.UTC)

    def to_dict(self):
        return {
            "userId": self.user_id,
            "chatId": self.chat_id,
            "joinedAt": self.joined_at.isoformat()
        }
