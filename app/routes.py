from flask import jsonify

"""
    Warning! All routes must be under the same subpath of your
    choosing, i.e.: /messaging-api/some-route, /messaging-api/other-route.
    This is needed because of how the upstream nginx reverse proxy will redirect
    traffic to the backend. Ask Vlad for more info.
"""

def register_routes(app):
    @app.route("/messaging-api")
    def index():
        return jsonify({"status": "Backend API running"})