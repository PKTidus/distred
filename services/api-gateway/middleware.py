from functools import wraps
from typing import Optional

from flask import g, redirect, request, url_for, session

from clients.user_client import get_current_user
import redis_cache as cache


def extract_bearer_token() -> Optional[str]:
    # Check Cookie first for HTML flow
    token = request.cookies.get("access_token")
    if token:
        return token
        
    # Fallback to Header for potential API calls
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[len("Bearer ") :]
    return None


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = extract_bearer_token()
        if not token:
            return redirect(url_for("auth.login_form", next=request.url))

        # check cache
        result = cache.get_cached_result(token)
        if result is None:
            # if not cached, check via rpc and cache
            # get_current_user also validates the token
            user_resp = get_current_user(token)
            if not user_resp or user_resp.error:
                return redirect(url_for("auth.login_form", next=request.url))
            
            result = {
                "valid": True,
                "username": user_resp.username,
                "user_id": user_resp.id
            }
            cache.cache_token(token, result)

        if not result or not result.get("valid"):
            return redirect(url_for("auth.login_form", next=request.url))

        g.username = result["username"]
        g.user_id = result["user_id"]
        g.token = token
        
        return f(*args, **kwargs)

    return decorated

def optional_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = extract_bearer_token()
        g.username = None
        g.token = None
        g.user_id = 0
        
        if token:
            result = cache.get_cached_result(token)
            if result is None:
                user_resp = get_current_user(token)
                if user_resp and not user_resp.error:
                    result = {
                        "valid": True,
                        "username": user_resp.username,
                        "user_id": user_resp.id
                    }
                    cache.cache_token(token, result)
            
            if result and result.get("valid"):
                g.username = result["username"]
                g.user_id = result["user_id"]
                g.token = token

        return f(*args, **kwargs)
    return decorated


def evict_token(token: str) -> None:
    cache.evict_cache(token)
