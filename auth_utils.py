# backend/auth_utils.py
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Request
from passlib.context import CryptContext
import jwt
from db.mongo import users_collection
from bson import ObjectId

JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-change-me")
JWT_ALGO = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hash_: str) -> bool:
    return pwd_context.verify(password, hash_)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGO)
    return token


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_user_from_token(token: str):
    """Return user dict or None (raises if token invalid)."""
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        return None
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user["_id"] = str(user["_id"])
    return user


async def get_current_user_optional(request: Request):
    """Try to get user from Authorization header. Return user dict or None."""
    auth = request.headers.get("authorization")
    if not auth:
        return None
    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1]
    try:
        return get_user_from_token(token)
    except HTTPException:
        return None
