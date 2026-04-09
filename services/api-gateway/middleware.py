from functools import wraps
from typing import Optional

from flask import g, redirect, request, url_for, session

from clients.user_client import validate_token, get_current_user
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
            result = validate_token(token)
            if result.get("valid"):
                cache.cache_token(token, result)

        if not result or not result.get("valid"):
            return redirect(url_for("auth.login_form", next=request.url))

        g.username = result["username"]
        g.token = token
        
        from clients.user_client import get_current_user
        user_resp = get_current_user(token)
        if not user_resp.error:
            g.user_id = user_resp.id
        else:
            g.user_id = 0
            
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
                result = validate_token(token)
                if result.get("valid"):
                    cache.cache_token(token, result)
            
            if result and result.get("valid"):
                g.username = result["username"]
                g.token = token
                # We might need user_id too
                user_resp = get_current_user(token)
                if not user_resp.error:
                    g.user_id = user_resp.id

        return f(*args, **kwargs)
    return decorated


def evict_token(token: str) -> None:
    cache.evict_cache(token)
