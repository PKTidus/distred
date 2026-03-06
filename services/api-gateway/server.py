#!/usr/bin/python
from flask import Flask, g, jsonify, request
from user_client import grpc_get_current_user, grpc_login, grpc_register, grpc_logout
from middleware import require_auth

app = Flask(__name__)


@app.post("/register")
def register():
    data = request.get_json(force=True)
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not all([username, password]):
        return jsonify({"error": "username and password are required"}), 400

    result = grpc_register(username=username, password=password)
    if "error" in result:
        return jsonify(result), 400

    return jsonify({"message": "User registered successfully"}), 201


@app.post("/login")
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

    result = grpc_login(username=username, password=password)
    if "error" in result:
        return jsonify(result), 401

    return jsonify(result), 200


@app.post("/logout")
@require_auth
def logout():
    """Invalidate the current token by adding it to the blacklist."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    result = grpc_logout(token=token)
    if "error" in result:
        return jsonify(result), 400
    return jsonify({"message": "Logged out successfully"}), 200

# ------------------------------------------------------------------
# Protected routes
# ------------------------------------------------------------------


@app.get("/users/me")
@require_auth
def get_me():
    """Return the currently authenticated user's profile."""
    result = grpc_get_current_user(
        token=request.headers.get("Authorization", "").replace("Bearer ", "")
    )
    if "error" in result:
        return jsonify(result), 401
    return jsonify(result), 200



if __name__ == "__main__":
    print("API Gateway listening on port 8000...")
    app.run(host="0.0.0.0", port=8000, debug=True)
