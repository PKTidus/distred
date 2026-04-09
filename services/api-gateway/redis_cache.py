# ---------------------------------------------------------------------------
# Redis client — single connection pool shared across requests
# ---------------------------------------------------------------------------
from time import time
import logging
import hashlib
import os
from typing import Optional
from flask import json

import jwt
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1,
)

CACHE_KEY_PREFIX = "token_valid:"


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _cache_key(token: str) -> str:
    digest = hashlib.sha256(token.encode()).hexdigest()
    return f"{CACHE_KEY_PREFIX}{digest}"


def _token_ttl_seconds(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        exp = payload.get("exp")
        if exp is None:
            return None
        ttl = int(exp - time.time())
        return ttl if ttl > 0 else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Cache read / write
# ---------------------------------------------------------------------------
def evict_cache(token: str) -> None:
    try:
        redis_client.delete(_cache_key(token))
    except redis.RedisError as e:
        logger.warning("Redis delete error, cache may be stale: %s", e)


def get_cached_result(token: str) -> Optional[dict]:
    try:
        raw = redis_client.get(_cache_key(token))
        if raw:
            return json.loads(raw)  # type: ignore
    except redis.RedisError as e:
        # Cache unavailable — fail open and fall through to gRPC
        logger.warning("Redis read error, skipping cache: %s", e)
    return None


def cache_token(token: str, result: dict) -> None:
    if not result.get("valid"):
        return

    ttl = _token_ttl_seconds(token)
    if not ttl:
        return  # Token has no exp or is already expired — don't cache

    try:
        redis_client.setex(_cache_key(token), ttl, json.dumps(result))
    except redis.RedisError as e:
        logger.warning("Redis write error, result not cached: %s", e)
