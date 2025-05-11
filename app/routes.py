from flask import jsonify
from app.database import users

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
