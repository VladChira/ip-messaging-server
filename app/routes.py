from flask import jsonify

def register_routes(app):
    @app.route("/")
    def index():
        return jsonify({"status": "Backend API running"})