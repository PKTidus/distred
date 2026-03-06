from functools import wraps

from flask import g, jsonify

from user_client import grpc_validate_token
import redis_cache as cache

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = cache.extract_bearer_token()
        if not token:
            return jsonify({"error": "Missing Authorization header"}), 401

        # check cache
        result = cache.get_cached_result(token)
        if result is None:
            # if not cached, check via rpc and cache
            result = grpc_validate_token(token)
            cache.cache_token(token, result)

        if not result.get("valid"):
            return jsonify({"error": result.get("error", "Unauthorized")}), 401

        g.username = result["username"]
        return f(*args, **kwargs)

    return decorated

def evict_token(token: str) -> None:
    cache.evict_cache(token)
