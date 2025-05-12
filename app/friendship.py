# app/friendship.py
import datetime
from typing import Optional, Dict, Any

class Friendship:
    """
    Represents an established friendship between two users.
    """

    def __init__(self,
                 friendshipId: int,
                 user1Id: int,
                 user2Id: int,
                 createdAt: Optional[datetime.datetime] = None):
        """
        Initializes a new Friendship object.

        Args:
            friendshipId (int): Unique identifier for the friendship.
            user1Id (int): The ID of the first user in the friendship.
            user2Id (int): The ID of the second user in the friendship.
            createdAt (datetime.datetime, optional): The date and time the friendship was established.
                                                     Defaults to the current datetime if None.
        """
        if not isinstance(friendshipId, int) or friendshipId <= 0:
            raise ValueError("friendshipId must be a positive integer.")
        if not isinstance(user1Id, int) or user1Id <= 0:
            raise ValueError("user1Id must be a positive integer.")
        if not isinstance(user2Id, int) or user2Id <= 0:
            raise ValueError("user2Id must be a positive integer.")
        if user1Id == user2Id:
            raise ValueError("user1Id and user2Id cannot be the same. A user cannot be friends with themselves.")

        self.friendshipId: int = friendshipId
        # Ensure consistent order for easier querying if needed, though not strictly necessary here
        self.user1Id: int = min(user1Id, user2Id)
        self.user2Id: int = max(user1Id, user2Id)
        self.createdAt: datetime.datetime = createdAt if createdAt else datetime.datetime.now()

    def __str__(self) -> str:
        """User-friendly string representation."""
        return (f"Friendship(id={self.friendshipId}, user1={self.user1Id}, user2={self.user2Id}, "
                f"created='{self.createdAt.strftime('%Y-%m-%d %H:%M:%S')}')")

    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return (f"Friendship(friendshipId={self.friendshipId!r}, user1Id={self.user1Id!r}, "
                f"user2Id={self.user2Id!r}, createdAt={self.createdAt!r})")

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dictionary representation of the friendship."""
        return {
            "friendshipId": self.friendshipId,
            "user1Id": self.user1Id,
            "user2Id": self.user2Id,
            "createdAt": self.createdAt.isoformat() # ISO format for easy serialization
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Friendship':
        """
        Creates a Friendship instance from a dictionary.
        """
        required_keys = ['friendshipId', 'user1Id', 'user2Id']
        if not all(key in data for key in required_keys):
            missing_keys = [key for key in required_keys if key not in data]
            raise ValueError(f"Missing required keys in data dictionary for Friendship: {', '.join(missing_keys)}")

        created_at_val = data.get('createdAt')
        created_at = None
        if created_at_val:
            if isinstance(created_at_val, str):
                try:
                    created_at = datetime.datetime.fromisoformat(created_at_val)
                except ValueError:
                     # Attempt to parse common date format if ISO fails (optional)
                    try:
                        created_at = datetime.datetime.strptime(created_at_val, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        raise ValueError(f"createdAt string '{created_at_val}' is not a valid ISO format or YYYY-MM-DD HH:MM:SS.")
            elif isinstance(created_at_val, datetime.datetime):
                created_at = created_at_val
            else:
                raise TypeError("createdAt must be an ISO format string, YYYY-MM-DD HH:MM:SS string, or datetime object.")

        return cls(
            friendshipId=data['friendshipId'],
            user1Id=data['user1Id'],
            user2Id=data['user2Id'],
            createdAt=created_at
        )

    def involves_user(self, user_id: int) -> bool:
        """Checks if the given user ID is part of this friendship."""
        return self.user1Id == int(user_id) or self.user2Id == int(user_id)

    def get_other_user(self, user_id: int) -> Optional[int]:
        """
        If the given user_id is part of the friendship, returns the ID of the other user.
        Otherwise, returns None.
        """
        # Ensure user_id is an integer
        user_id_int = int(user_id)
        if self.user1Id == user_id_int:
            return self.user2Id
        elif self.user2Id == user_id_int:
            return self.user1Id
        else:
            return None

