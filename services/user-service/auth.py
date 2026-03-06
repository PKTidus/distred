from datetime import datetime, timedelta, timezone
import os
from typing import Optional

from jwt import encode, decode
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from config import SessionLocal
from db import TokenBlacklist

# Generate with: openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY", "peter")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    return encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    # first - make sure the token hasn’t been revoked
    db = SessionLocal()
    try:
        if db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first():
            return None
    finally:
        db.close()

    # then perform the normal JWT decode/expiry check
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            return None
        return username
    except InvalidTokenError:
        return None
