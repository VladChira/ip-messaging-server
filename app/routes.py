from flask import jsonify
from app.database import users
from app.database import friendships
from app.database import friendrequests

"""
    Warning! All routes must be under the same subpath of your
    choosing, i.e.: /messaging-api/some-route, /messaging-api/other-route.
    This is needed because of how the upstream nginx reverse proxy will redirect
    traffic to the backend. Ask Vlad for more info.
"""

def register_routes(app):
    @app.route("/messaging-api", strict_slashes=False)
    def index():
        return jsonify({"status": "Backend API running"})
    
    @app.route("/messaging-api/users", methods=["GET"], strict_slashes=False)
    def get_all_users():
        return jsonify({"users": [user.to_dict() for user in users]})

    @app.route("/messaging-api/send-friend-request", methods=["POST"], strict_slashes=False)
    def send_friend_request():
        # Placeholder for sending a friend request
        return jsonify({"status": "Friend request sent"}), 200

    @app.route("/messaging-api/accept-friend-request", methods=["POST"], strict_slashes=False)
    def accept_friend_request():
        # Placeholder for accepting a friend request
        return jsonify({"status": "Friend request accepted"}), 200
    
    @app.route("/messaging-api/reject-friend-request", methods=["POST"], strict_slashes=False)
    def reject_friend_request():
        # Placeholder for rejecting a friend request
        return jsonify({"status": "Friend request rejected"}), 200    
    
    @app.route("/messaging-api/get-friends-by-user-id", methods=["GET"], strict_slashes=False)
    def get_friends_by_user_id():
        return jsonify({"friends": [friendship for friendship in friendships]})