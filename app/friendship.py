import datetime
from typing import Optional, Dict, Any

class Friendship:
    """
    Represents a friendship link between two users.
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
            createdAt (datetime.datetime, optional): The date and time the friendship was created.
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
        self.user1Id: int = user1Id
        self.user2Id: int = user2Id
        self.createdAt: datetime.datetime = createdAt if createdAt else datetime.datetime.now()

    def __str__(self) -> str:
        """User-friendly string representation."""
        return (f"Friendship(id={self.friendshipId}, "
                f"users=({self.user1Id}, {self.user2Id}), "
                f"created='{self.createdAt.strftime('%Y-%m-%d %H:%M:%S')}')")

    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return (f"Friendship(friendshipId={self.friendshipId!r}, "
                f"user1Id={self.user1Id!r}, user2Id={self.user2Id!r}, "
                f"createdAt={self.createdAt!r})")

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
        Creates a Friendship instance from a dictionary (e.g., from a database or API).
        """
        if not all(key in data for key in ['friendshipId', 'user1Id', 'user2Id']):
            raise ValueError("Missing required keys in data dictionary for Friendship.")

        created_at_val = data.get('createdAt')
        created_at = None
        if created_at_val:
            if isinstance(created_at_val, str):
                created_at = datetime.datetime.fromisoformat(created_at_val)
            elif isinstance(created_at_val, datetime.datetime):
                created_at = created_at_val
            else:
                raise TypeError("createdAt must be an ISO format string or datetime object.")

        return cls(
            friendshipId=data['friendshipId'],
            user1Id=data['user1Id'],
            user2Id=data['user2Id'],
            createdAt=created_at
        )

    def get_other_user_id(self, current_user_id: int) -> Optional[int]:
        """
        Given one user ID in the friendship, returns the ID of the other user.
        Returns None if the provided current_user_id is not part of this friendship.
        """
        if self.user1Id == current_user_id:
            return self.user2Id
        elif self.user2Id == current_user_id:
            return self.user1Id
        return None # current_user_id is not part of this friendship
    
