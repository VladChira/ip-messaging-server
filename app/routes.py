from flask import jsonify, request, abort
from flask_jwt_extended import (
    create_access_token, 
    jwt_required, 
    get_jwt_identity,
    get_jwt
)
import datetime
import functools

# Import data lists and classes
from app.database import users, friendships, friendrequests
from app.user import User, Role
from app.friendship import Friendship
from app.friendrequest import FriendRequest, RequestStatus

"""
    Warning! All routes must be under the same subpath of your
    choosing, i.e.: /messaging-api/some-route, /messaging-api/other-route.
    This is needed because of how the upstream nginx reverse proxy will redirect
    traffic to the backend. Ask Vlad for more info.
"""

# --- Helper Functions ---

def find_user_by_id(user_id: int) -> User | None:
    """Finds a user in the global 'users' list by their ID."""
    return next((user for user in users if user.userId == user_id), None)

def find_user_by_username(username: str) -> User | None:
    """Finds a user by username (case-insensitive check)."""
    return next((user for user in users if user.username.lower() == username.lower()), None)

def find_user_by_email(email: str) -> User | None:
    """Finds a user by email (case-insensitive check)."""
    return next((user for user in users if user.email.lower() == email.lower()), None)

def find_friend_request_by_id(request_id: int) -> FriendRequest | None:
    """Finds a friend request by its ID."""
    return next((req for req in friendrequests if req.requestId == request_id), None)

def find_pending_request(user1_id: int, user2_id: int) -> FriendRequest | None:
    """Finds a PENDING request between two users, regardless of direction."""
    for req in friendrequests:
        if req.status == RequestStatus.PENDING:
            if (req.senderId == user1_id and req.receiverId == user2_id) or \
               (req.senderId == user2_id and req.receiverId == user1_id):
                return req
    return None

def find_friendship(user1_id: int, user2_id: int) -> Friendship | None:
    """Finds an existing friendship between two users."""
    # Ensure consistent order for lookup, matching the Friendship class logic
    u1 = min(user1_id, user2_id)
    u2 = max(user1_id, user2_id)
    return next((f for f in friendships if f.user1Id == u1 and f.user2Id == u2), None)

def get_next_id(data_list: list, id_field_name: str) -> int:
    """Generates the next available ID for a list of objects."""
    if not data_list:
        return 1
    return max(getattr(item, id_field_name) for item in data_list) + 1

# --- JWT Auth Middleware ---
def jwt_auth_required(fn):
    """
    Custom decorator that combines jwt_required with additional checks.
    This will ensure all routes are protected by JWT authentication.
    """
    @functools.wraps(fn)
    @jwt_required()  # Require JWT for all routes using this decorator
    def wrapper(*args, **kwargs):
        # Get the current user ID from the JWT token
        current_user_id = get_jwt_identity()
        
        # Check if the user exists in the database
        user = find_user_by_id(current_user_id)
        if not user:
            return jsonify({"error": "Unauthorized: User not found"}), 401
            
        # Check if the user is active
        if user.status != "active":
            return jsonify({"error": "Account is not active"}), 403
            
        # Call the original function
        return fn(*args, **kwargs)
    return wrapper

# --- Route Registration ---
def register_routes(app):

    @app.route("/messaging-api", strict_slashes=False)
    def index():
        return jsonify({"status": "Backend API running"})

    # === Login Route ===
    @app.route("/messaging-api/login", methods=["POST"], strict_slashes=False)
    def login():
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
            
        # Verify if username or email is provided
        if not ("username" in data or "email" in data) or "password" not in data:
            return jsonify({"error": "Missing login credentials"}), 400
            
        # Check if username or email exists
        user = None
        if "username" in data:
            user = find_user_by_username(data["username"])
        elif "email" in data:
            user = find_user_by_email(data["email"])
            
        # If user not found or password doesn't match
        if not user or not user.check_password(data["password"]):
            return jsonify({"error": "Invalid credentials"}), 401
            
        # Verify if the user is active
        if user.status != "active":
            return jsonify({"error": "Account is not active"}), 403
            
        # Generare token JWT
        access_token = create_access_token(
            identity=user.userId,
            additional_claims={
                "username": user.username,
                "role": user.role.value
            }
        )
        
        # Return user data and token
        return jsonify({
            "user": user.to_dict(),
            "token": access_token
        }), 200
        
    # === Protected Routes ===
    @app.route("/messaging-api/users", methods=["GET"], strict_slashes=False)
    @jwt_auth_required
    def get_all_users():
        return jsonify({"users": [user.to_dict() for user in users]})

    # === User Registration ===
    @app.route("/messaging-api/register", methods=["POST"], strict_slashes=False)
    def register_user():
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400

        required_fields = ["name", "email", "username", "password"]
        if not all(field in data for field in required_fields):
            missing = [field for field in required_fields if field not in data]
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        # Basic validation
        if not data["name"] or not data["username"] or not data["email"] or "@" not in data["email"]:
             return jsonify({"error": "Invalid name, username, or email format"}), 400
        if len(data["password"]) < 6:
             return jsonify({"error": "Password must be at least 6 characters long"}), 400

        # Check for existing username or email
        if find_user_by_username(data["username"]):
            return jsonify({"error": f"Username '{data['username']}' already exists"}), 409 # 409 Conflict
        if find_user_by_email(data["email"]):
            return jsonify({"error": f"Email '{data['email']}' already registered"}), 409

        try:
            new_user_id = get_next_id(users, "userId")
            new_user = User(
                userId=new_user_id,
                name=data["name"],
                email=data["email"],
                username=data["username"],
                password=data["password"], # Hashing happens in User.__init__
                role=Role.USER, # Default role
                status="active" # Default status
            )
            users.append(new_user)
            return jsonify(new_user.to_dict()), 201 # 201 Created
        except (ValueError, TypeError) as e:
             # Catch potential errors from User class validation
             return jsonify({"error": str(e)}), 400

    # === Friend Request Management ===
    @app.route("/messaging-api/send-friend-request", methods=["POST"], strict_slashes=False)
    @jwt_auth_required
    def send_friend_request():
        data = request.get_json()
        if not data or "senderId" not in data or "receiverId" not in data:
            return jsonify({"error": "Missing senderId or receiverId in request body"}), 400

        # Verify if senderId is the same as the authenticated user
        current_user_id = get_jwt_identity()
        if int(data["senderId"]) != current_user_id:
            return jsonify({"error": "Unauthorized: senderId must match authenticated user"}), 403

        sender_id = data["senderId"]
        receiver_id = data["receiverId"]

        # Validate IDs
        if not isinstance(sender_id, int) or not isinstance(receiver_id, int) or sender_id <= 0 or receiver_id <= 0:
             return jsonify({"error": "senderId and receiverId must be positive integers"}), 400
        if sender_id == receiver_id:
            return jsonify({"error": "Cannot send friend request to yourself"}), 400

        # Check if users exist
        sender = find_user_by_id(sender_id)
        receiver = find_user_by_id(receiver_id)
        if not sender:
            return jsonify({"error": f"Sender user with ID {sender_id} not found"}), 404
        if not receiver:
            return jsonify({"error": f"Receiver user with ID {receiver_id} not found"}), 404

        # Check if already friends
        if find_friendship(sender_id, receiver_id):
            return jsonify({"error": "Users are already friends"}), 409

        # Check if a pending request already exists
        if find_pending_request(sender_id, receiver_id):
            return jsonify({"error": "A pending friend request already exists between these users"}), 409

        try:
            new_request_id = get_next_id(friendrequests, "requestId")
            new_request = FriendRequest(
                requestId=new_request_id,
                senderId=sender_id,
                receiverId=receiver_id
                # Status defaults to PENDING
            )
            friendrequests.append(new_request)
            return jsonify(new_request.to_dict()), 201
        except (ValueError, TypeError) as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/messaging-api/accept-friend-request", methods=["POST"], strict_slashes=False)
    @jwt_auth_required
    def accept_friend_request():
        data = request.get_json()
        if not data or "requestId" not in data or "accepterId" not in data:
             return jsonify({"error": "Missing requestId or accepterId in request body"}), 400

        # Verify if accepterId is the same as the authenticated user
        current_user_id = get_jwt_identity()
        if int(data["accepterId"]) != current_user_id:
            return jsonify({"error": "Unauthorized: accepterId must match authenticated user"}), 403

        request_id = data["requestId"]
        accepter_id = data["accepterId"]

        if not isinstance(request_id, int) or not isinstance(accepter_id, int):
             return jsonify({"error": "requestId and accepterId must be integers"}), 400

        # Find the request
        friend_request = find_friend_request_by_id(request_id)
        if not friend_request:
            return jsonify({"error": f"Friend request with ID {request_id} not found"}), 404

        # Verify the accepter is the intended receiver
        if friend_request.receiverId != accepter_id:
            return jsonify({"error": "You are not authorized to accept this request"}), 403 # Forbidden

        # Check if request is pending and accept it
        if friend_request.status != RequestStatus.PENDING:
             return jsonify({"error": f"Request is not pending (status: {friend_request.status.value})"}), 409

        if friend_request.accept():
            # Create the friendship
            try:
                new_friendship_id = get_next_id(friendships, "friendshipId")
                new_friendship = Friendship(
                    friendshipId=new_friendship_id,
                    user1Id=friend_request.senderId,
                    user2Id=friend_request.receiverId
                )
                friendships.append(new_friendship)
                # Return both the updated request and the new friendship
                return jsonify({
                    "message": "Friend request accepted",
                    "request": friend_request.to_dict(),
                    "friendship": new_friendship.to_dict()
                }), 200
            except (ValueError, TypeError) as e:
                 # Should ideally not happen if request was valid, but good practice
                 # Rollback status change? (More complex, maybe not needed for in-memory)
                 friend_request.status = RequestStatus.PENDING # Attempt rollback
                 return jsonify({"error": f"Failed to create friendship: {str(e)}"}), 500 # Internal Server Error
        else:
            # Should not happen if status was PENDING, but handle defensively
            return jsonify({"error": "Failed to accept friend request"}), 500

    # Add Reject Friend Request for completeness (similar logic to accept)
    @app.route("/messaging-api/reject-friend-request", methods=["POST"], strict_slashes=False)
    @jwt_auth_required
    def reject_friend_request():
        data = request.get_json()
        if not data or "requestId" not in data or "rejecterId" not in data:
             return jsonify({"error": "Missing requestId or rejecterId in request body"}), 400

        # Verify if rejecterId is the same as the authenticated user
        current_user_id = get_jwt_identity()
        if int(data["rejecterId"]) != current_user_id:
            return jsonify({"error": "Unauthorized: rejecterId must match authenticated user"}), 403

        request_id = data["requestId"]
        rejecter_id = data["rejecterId"] # The user rejecting

        if not isinstance(request_id, int) or not isinstance(rejecter_id, int):
             return jsonify({"error": "requestId and rejecterId must be integers"}), 400

        friend_request = find_friend_request_by_id(request_id)
        if not friend_request:
            return jsonify({"error": f"Friend request with ID {request_id} not found"}), 404

        # Verify the rejecter is the intended receiver OR the sender (sender can cancel)
        is_receiver = friend_request.receiverId == rejecter_id
        is_sender = friend_request.senderId == rejecter_id

        if not is_receiver and not is_sender:
             return jsonify({"error": "You are not authorized to modify this request"}), 403

        if friend_request.status != RequestStatus.PENDING:
             return jsonify({"error": f"Request is not pending (status: {friend_request.status.value})"}), 409

        action_taken = False
        if is_receiver:
            action_taken = friend_request.reject()
            message = "Friend request rejected"
        elif is_sender:
            action_taken = friend_request.cancel() # Sender cancels
            message = "Friend request cancelled"

        if action_taken:
            return jsonify({
                "message": message,
                "request": friend_request.to_dict()
            }), 200
        else:
            return jsonify({"error": f"Failed to {message.lower()}"}), 500


    # === Friendship Management ===
    @app.route("/messaging-api/get-friends-by-user-id/<int:user_id>", methods=["GET"], strict_slashes=False)
    @jwt_auth_required
    def get_friends_by_user_id(user_id):
        # This implementation should already be correct from previous steps
        target_user = find_user_by_id(user_id)
        if not target_user:
            return jsonify({"error": f"User with ID {user_id} not found."}), 404

        user_friend_ids = set()
        for friendship in friendships:
            if friendship.involves_user(user_id):
                other_user_id = friendship.get_other_user(user_id)
                if other_user_id:
                    user_friend_ids.add(other_user_id)

        friend_users = []
        for friend_id in user_friend_ids:
            friend_user = find_user_by_id(friend_id)
            if friend_user:
                friend_users.append(friend_user.to_dict())

        return jsonify({"friends": friend_users})

    @app.route("/messaging-api/remove-friend", methods=["POST"], strict_slashes=False) # Using POST for action
    @jwt_auth_required
    def remove_friend():
        data = request.get_json()
        if not data or "userId" not in data or "friendId" not in data:
             return jsonify({"error": "Missing userId or friendId in request body"}), 400

        # Verify if userId is the same as the authenticated user
        current_user_id = get_jwt_identity()
        if int(data["userId"]) != current_user_id:
            return jsonify({"error": "Unauthorized: userId must match authenticated user"}), 403

        user_id = data["userId"]
        friend_id = data["friendId"]

        if not isinstance(user_id, int) or not isinstance(friend_id, int) or user_id <= 0 or friend_id <= 0:
             return jsonify({"error": "userId and friendId must be positive integers"}), 400
        if user_id == friend_id:
             return jsonify({"error": "Cannot remove yourself as a friend"}), 400

        # Check if users exist
        if not find_user_by_id(user_id):
            return jsonify({"error": f"User with ID {user_id} not found"}), 404
        if not find_user_by_id(friend_id):
            return jsonify({"error": f"User with ID {friend_id} not found"}), 404

        # Find the friendship
        friendship_to_remove = find_friendship(user_id, friend_id)
        if not friendship_to_remove:
            return jsonify({"error": "These users are not friends"}), 404

        # Remove the friendship
        friendships.remove(friendship_to_remove)
        return jsonify({"message": f"Friendship between user {user_id} and user {friend_id} removed"}), 200

    # === User Account Management ===
    @app.route("/messaging-api/delete-user/<int:user_id>", methods=["DELETE"], strict_slashes=False)
    @jwt_auth_required
    def delete_user(user_id):
        global users, friendships, friendrequests # Declare modification of globals

        # Verify if userId is the same as the authenticated user or admin
        current_user_id = get_jwt_identity()
        current_user = find_user_by_id(current_user_id)
        
        # Only allow admin or the user themselves to delete the account
        if current_user.role != Role.ADMIN and current_user_id != user_id:
            return jsonify({"error": "Unauthorized: You can only delete your own account unless you're an admin"}), 403

        user_to_delete = find_user_by_id(user_id)
        if not user_to_delete:
            return jsonify({"error": f"User with ID {user_id} not found"}), 404

        # Remove the user
        users.remove(user_to_delete)

        # Remove associated friendships
        # Iterate over a copy of the list when removing items
        friendships_to_keep = [f for f in friendships if not f.involves_user(user_id)]
        friendships[:] = friendships_to_keep # Modify list in place

        # Remove associated friend requests (sent or received)
        requests_to_keep = [
            req for req in friendrequests
            if req.senderId != user_id and req.receiverId != user_id
        ]
        friendrequests[:] = requests_to_keep # Modify list in place

        return jsonify({"message": f"User {user_id} and associated data deleted successfully"}), 200

    @app.route("/messaging-api/change-name/<int:user_id>", methods=["PATCH"], strict_slashes=False)
    @jwt_auth_required
    def change_name(user_id):
        # Verify if userId is the same as the authenticated user
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({"error": "Unauthorized: You can only change your own name"}), 403
            
        user = find_user_by_id(user_id)
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found"}), 404

        data = request.get_json()
        if not data or "newName" not in data or not data["newName"]:
            return jsonify({"error": "Missing or empty 'newName' in request body"}), 400

        new_name = data["newName"]
        if not isinstance(new_name, str):
             return jsonify({"error": "'newName' must be a string"}), 400

        user.name = new_name
        return jsonify(user.to_dict()), 200

    @app.route("/messaging-api/change-password/<int:user_id>", methods=["PATCH"], strict_slashes=False)
    @jwt_auth_required
    def change_password(user_id):
        # Verify if userId is the same as the authenticated user
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({"error": "Unauthorized: You can only change your own password"}), 403
            
        user = find_user_by_id(user_id)
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found"}), 404

        data = request.get_json()
        if not data or "newPassword" not in data:
            return jsonify({"error": "Missing 'newPassword' in request body"}), 400

        new_password = data["newPassword"]
        if not isinstance(new_password, str) or len(new_password) < 6:
             return jsonify({"error": "Password must be a string and at least 6 characters long"}), 400

        try:
            user.password = new_password # Uses the setter, which hashes
            return jsonify({"message": "Password updated successfully"}), 200
        except ValueError as e: # Catch validation errors from the setter
            return jsonify({"error": str(e)}), 400


    @app.route("/messaging-api/change-status/<int:user_id>", methods=["PATCH"], strict_slashes=False)
    @jwt_auth_required
    def change_status(user_id):
        # Verify if userId is the same as the authenticated user
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({"error": "Unauthorized: You can only change your own status"}), 403
            
        user = find_user_by_id(user_id)
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found"}), 404

        data = request.get_json()
        if not data or "newStatus" not in data:
            return jsonify({"error": "Missing 'newStatus' in request body"}), 400

        new_status = data["newStatus"]
        # Optional: Add validation for allowed statuses
        allowed_statuses = ["active", "inactive", "away", "busy"] # Example
        if not isinstance(new_status, str) or new_status not in allowed_statuses:
             return jsonify({"error": f"Invalid status. Must be one of: {', '.join(allowed_statuses)}"}), 400

        user.status = new_status
        return jsonify(user.to_dict()), 200

    # --- (Optional) Add a route to view friend requests for a user ---
    @app.route("/messaging-api/get-friend-requests/<int:user_id>", methods=["GET"], strict_slashes=False)
    @jwt_auth_required
    def get_friend_requests_for_user(user_id):
        # Verify if userId is the same as the authenticated user or admin
        current_user_id = get_jwt_identity()
        current_user = find_user_by_id(current_user_id)
        
        if current_user_id != user_id and current_user.role != Role.ADMIN:
            return jsonify({"error": "Unauthorized: You can only view your own friend requests"}), 403
            
        target_user = find_user_by_id(user_id)
        if not target_user:
            return jsonify({"error": f"User with ID {user_id} not found."}), 404

        # Find requests where the user is the receiver (incoming)
        incoming_requests = [
            req.to_dict() for req in friendrequests
            if req.receiverId == user_id and req.status == RequestStatus.PENDING
        ]

        # Find requests where the user is the sender (outgoing)
        outgoing_requests = [
            req.to_dict() for req in friendrequests
            if req.senderId == user_id and req.status == RequestStatus.PENDING
        ]

        # Optionally include non-pending requests too
        # accepted_requests = [...]
        # rejected_requests = [...]

        return jsonify({
            "incoming_pending": incoming_requests,
            "outgoing_pending": outgoing_requests
        })