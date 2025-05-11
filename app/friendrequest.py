import datetime
from enum import Enum
from typing import Optional, Dict, Any

class RequestStatus(Enum):
    """
    Defines the possible statuses for a friend request.
    """
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"  # Common status, added for completeness
    CANCELLED = "cancelled" # If the sender cancels the request

    @classmethod
    def from_string(cls, s: str) -> 'RequestStatus':
        """
        Creates a RequestStatus enum member from a string.
        Tries matching by name (e.g., "PENDING") and then by value (e.g., "pending").
        """
        s_upper = s.upper()
        s_lower = s.lower()
        try:
            return cls[s_upper] # Match by attribute name (e.g., PENDING)
        except KeyError:
            for member in cls: # Match by value (e.g., "pending")
                if member.value == s_lower:
                    return member
            raise ValueError(
                f"'{s}' is not a valid request status. Must be one of "
                f"{', '.join([r.name for r in cls])} (case-insensitive name) or "
                f"{', '.join([r.value for r in cls])} (case-insensitive value)."
            )

class FriendRequest:
    """
    Represents a friend request sent from one user to another.
    """

    def __init__(self,
                 requestId: int,
                 senderId: int,
                 receiverId: int,
                 status: RequestStatus = RequestStatus.PENDING, # Default status
                 createdAt: Optional[datetime.datetime] = None):
        """
        Initializes a new FriendRequest object.

        Args:
            requestId (int): Unique identifier for the friend request.
            senderId (int): The ID of the user who sent the request.
            receiverId (int): The ID of the user who received the request.
            status (RequestStatus or str, optional): The current status of the request.
                                                     Can be a RequestStatus enum member or a string
                                                     (e.g., "pending", "accepted").
                                                     Defaults to RequestStatus.PENDING.
            createdAt (datetime.datetime, optional): The date and time the request was created.
                                                     Defaults to the current datetime if None.
        """
        if not isinstance(requestId, int) or requestId <= 0:
            raise ValueError("requestId must be a positive integer.")
        if not isinstance(senderId, int) or senderId <= 0:
            raise ValueError("senderId must be a positive integer.")
        if not isinstance(receiverId, int) or receiverId <= 0:
            raise ValueError("receiverId must be a positive integer.")
        if senderId == receiverId:
            raise ValueError("senderId and receiverId cannot be the same. A user cannot send a friend request to themselves.")

        self.requestId: int = requestId
        self.senderId: int = senderId
        self.receiverId: int = receiverId

        if isinstance(status, str):
            self.status: RequestStatus = RequestStatus.from_string(status)
        elif isinstance(status, RequestStatus):
            self.status: RequestStatus = status
        else:
            raise TypeError("status must be a RequestStatus enum instance or a valid status string.")

        self.createdAt: datetime.datetime = createdAt if createdAt else datetime.datetime.now()

    def __str__(self) -> str:
        """User-friendly string representation."""
        return (f"FriendRequest(id={self.requestId}, sender={self.senderId}, "
                f"receiver={self.receiverId}, status='{self.status.value}', "
                f"created='{self.createdAt.strftime('%Y-%m-%d %H:%M:%S')}')")

    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return (f"FriendRequest(requestId={self.requestId!r}, senderId={self.senderId!r}, "
                f"receiverId={self.receiverId!r}, status=RequestStatus.{self.status.name}, "
                f"createdAt={self.createdAt!r})")

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dictionary representation of the friend request."""
        return {
            "requestId": self.requestId,
            "senderId": self.senderId,
            "receiverId": self.receiverId,
            "status": self.status.value, # Store the string value of the enum
            "createdAt": self.createdAt.isoformat() # ISO format for easy serialization
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FriendRequest':
        """
        Creates a FriendRequest instance from a dictionary (e.g., from a database or API).
        """
        required_keys = ['requestId', 'senderId', 'receiverId']
        if not all(key in data for key in required_keys):
            missing_keys = [key for key in required_keys if key not in data]
            raise ValueError(f"Missing required keys in data dictionary for FriendRequest: {', '.join(missing_keys)}")

        status_input = data.get('status', RequestStatus.PENDING.value) # Default to 'pending' string value

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
            requestId=data['requestId'],
            senderId=data['senderId'],
            receiverId=data['receiverId'],
            status=status_input, # __init__ will handle conversion from string to Enum
            createdAt=created_at
        )

    # --- Status manipulation methods ---

    def accept(self) -> bool:
        """
        Sets the request status to ACCEPTED if it is currently PENDING.
        Returns True if status was changed, False otherwise.
        """
        if self.status == RequestStatus.PENDING:
            self.status = RequestStatus.ACCEPTED
            # In a real app, you might also set an 'updatedAt' or 'respondedAt' timestamp
            return True
        # print(f"Warning: Cannot accept request {self.requestId} (status: {self.status.value}). It must be PENDING.")
        return False

    def reject(self) -> bool:
        """
        Sets the request status to REJECTED if it is currently PENDING.
        Returns True if status was changed, False otherwise.
        """
        if self.status == RequestStatus.PENDING:
            self.status = RequestStatus.REJECTED
            return True
        # print(f"Warning: Cannot reject request {self.requestId} (status: {self.status.value}). It must be PENDING.")
        return False

    def cancel(self) -> bool:
        """
        Sets the request status to CANCELLED if it is currently PENDING (typically by the sender).
        Returns True if status was changed, False otherwise.
        """
        if self.status == RequestStatus.PENDING:
            self.status = RequestStatus.CANCELLED
            return True
        # print(f"Warning: Cannot cancel request {self.requestId} (status: {self.status.value}). It must be PENDING.")
        return False

# --- Example Usage ---
if __name__ == "__main__":
    # User IDs
    user1_id = 10
    user2_id = 20
    user3_id = 30

    print("--- Creating Friend Requests ---")
    try:
        # Request 1: user1 sends to user2
        req1 = FriendRequest(requestId=1, senderId=user1_id, receiverId=user2_id)
        print(f"Created: {req1}")
        print(f"Repr: {repr(req1)}")

        # Request 2: user2 sends to user3, with specific status and time
        custom_time = datetime.datetime(2023, 10, 26, 10, 0, 0)
        req2 = FriendRequest(requestId=2, senderId=user2_id, receiverId=user3_id,
                             status=RequestStatus.PENDING, createdAt=custom_time)
        print(f"Created: {req2}")

        # Request 3: from string status
        req3 = FriendRequest(requestId=3, senderId=user1_id, receiverId=user3_id, status="pending")
        print(f"Created (from string status 'pending'): {req3}")


        print("\n--- Manipulating Status ---")
        print(f"Initial status of req1: {req1.status.value}")
        if req1.accept():
            print(f"req1 accepted. New status: {req1.status.value}")
        else:
            print(f"Could not accept req1. Status: {req1.status.value}")

        # Try to accept again (should not change)
        if not req1.accept():
            print(f"req1 could not be accepted again. Status: {req1.status.value}")


        print(f"\nInitial status of req3: {req3.status.value}")
        if req3.reject():
            print(f"req3 rejected. New status: {req3.status.value}")
        else:
            print(f"Could not reject req3. Status: {req3.status.value}")


        req4 = FriendRequest(requestId=4, senderId=user2_id, receiverId=user1_id)
        print(f"\nInitial status of req4: {req4.status.value}")
        if req4.cancel():
            print(f"req4 cancelled. New status: {req4.status.value}")
        else:
            print(f"Could not cancel req4. Status: {req4.status.value}")


        print("\n--- to_dict and from_dict ---")
        req1_dict = req1.to_dict()
        print(f"req1 as dict: {req1_dict}")

        req1_from_dict = FriendRequest.from_dict(req1_dict)
        print(f"req1 from dict: {req1_from_dict}")
        assert req1_from_dict.status == RequestStatus.ACCEPTED
        assert req1_from_dict.createdAt == req1.createdAt

        # Example with string date in dict
        dict_with_str_date = {
            "requestId": 5,
            "senderId": 50,
            "receiverId": 60,
            "status": "pending",
            "createdAt": "2023-01-01T12:30:00"
        }
        req_from_str_date_dict = FriendRequest.from_dict(dict_with_str_date)
        print(f"Request from dict with ISO date string: {req_from_str_date_dict}")
        assert req_from_str_date_dict.createdAt == datetime.datetime(2023, 1, 1, 12, 30, 0)

        dict_with_simple_date = {
            "requestId": 6,
            "senderId": 70,
            "receiverId": 80,
            "status": "accepted",
            "createdAt": "2024-03-15 09:45:10" # Non-ISO but common
        }
        req_from_simple_date_dict = FriendRequest.from_dict(dict_with_simple_date)
        print(f"Request from dict with simple date string: {req_from_simple_date_dict}")
        assert req_from_simple_date_dict.createdAt == datetime.datetime(2024, 3, 15, 9, 45, 10)


        print("\n--- Validations ---")
        try:
            FriendRequest(requestId=0, senderId=1, receiverId=2)
        except ValueError as e:
            print(f"Caught expected error: {e}")
        try:
            FriendRequest(requestId=10, senderId=1, receiverId=1)
        except ValueError as e:
            print(f"Caught expected error: {e}")
        try:
            FriendRequest(requestId=11, senderId=1, receiverId=2, status="invalid_status")
        except ValueError as e:
            print(f"Caught expected error: {e}")
        try:
            FriendRequest.from_dict({"requestId": 1, "senderId": 1}) # Missing receiverId
        except ValueError as e:
            print(f"Caught expected error for from_dict: {e}")


    except (ValueError, TypeError) as e:
        print(f"An error occurred: {e}")