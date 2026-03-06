from flask import Blueprint, jsonify, request
from clients import user_client
from middleware import require_auth

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json(force=True)
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not all([username, password]):
        return jsonify({"error": "username and password are required"}), 400

    result = user_client.register(username=username, password=password)
    if "error" in result:
        return jsonify(result), 400

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.post("/login")
def login():
    if request.content_type and "application/json" in request.content_type:
        data = request.get_json(force=True)
        username = data.get("username", "")
        password = data.get("password", "")
    else:
        username = request.form.get("username", "")
        password = request.form.get("password", "")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    result = user_client.login(username=username, password=password)
    if "error" in result:
        return jsonify(result), 401

    return jsonify(result), 200


@auth_bp.post("/logout")
@require_auth
def logout():
    """Invalidate the current token by adding it to the blacklist."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")

    result = user_client.logout(token=token)
    if "error" in result:
        return jsonify(result), 400
    return jsonify({"message": "Logged out successfully"}), 200


# ------------------------------------------------------------------
# Protected routes
# ------------------------------------------------------------------


@auth_bp.get("/me")
@require_auth
def get_me():
    """Return the currently authenticated user's profile."""
    result = user_client.get_current_user(
        token=request.headers.get("Authorization", "").replace("Bearer ", "")
    )
    if "error" in result:
        return jsonify(result), 401
    return jsonify(result), 200
