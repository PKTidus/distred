from functools import wraps

from flask import g, jsonify, request

from clients.user_client import validate_token
import redis_cache as cache


def extract_bearer_token() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[len("Bearer ") :]
    return None


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = extract_bearer_token()
        if not token:
            return jsonify({"error": "Missing Authorization header"}), 401

        # check cache
        result = cache.get_cached_result(token)
        if result is None:
            # if not cached, check via rpc and cache
            result = validate_token(token)
            cache.cache_token(token, result)

        if not result.get("valid"):
            return jsonify({"error": result.get("error", "Unauthorized")}), 401

        g.username = result["username"]
        return f(*args, **kwargs)

    return decorated


def evict_token(token: str) -> None:
    cache.evict_cache(token)
