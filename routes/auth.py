# backend/routes/auth.py

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from bson import ObjectId
import os
import httpx
from dotenv import load_dotenv

from auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    get_user_from_token
)

from db.mongo import users_collection

# Load .env (IMPORTANT)
load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])

# ENV variables
N8N_WELCOME_WEBHOOK = os.getenv("N8N_WELCOME_WEBHOOK")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

print("🔗 Loaded N8N Webhook URL:", N8N_WELCOME_WEBHOOK)


# ===============================
# Pydantic Models
# ===============================

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    mobile: str = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UpdateProfileRequest(BaseModel):
    name: str = None
    mobile: str = None


# ===============================
# ASYNC WEBHOOK CALLER (Correct)
# ===============================

async def trigger_welcome_webhook(name: str, email: str):
    """Send webhook to n8n asynchronously."""

    if not N8N_WELCOME_WEBHOOK:
        print("❌ ERROR: N8N_WELCOME_WEBHOOK missing from .env")
        return

    payload = {"name": name, "email": email}
    print("📨 Sending webhook to n8n:", payload)

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(N8N_WELCOME_WEBHOOK, json=payload)
            print("✅ Webhook Status:", resp.status_code)
            print("📩 Webhook Response:", resp.text)

    except Exception as e:
        print("❌ Webhook Error:", e)


# ===============================
# REGISTER (Fixed + Clean)
# ===============================

@router.post("/register")
async def register(req: RegisterRequest, background_tasks: BackgroundTasks):

    # Check existing
    if users_collection.find_one({"email": req.email.lower()}):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed = hash_password(req.password)

    # Create user
    user_doc = {
        "name": req.name,
        "email": req.email.lower(),
        "password_hash": hashed,
        "mobile": req.mobile,
        "created_at": __import__("datetime").datetime.utcnow()
    }

    result = users_collection.insert_one(user_doc)
    user_id = str(result.inserted_id)

    # Create JWT
    token = create_access_token(
        {"user_id": user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # 🚀 Trigger webhook properly (NO asyncio.run)
    background_tasks.add_task(trigger_welcome_webhook, req.name, req.email)

    print("🎉 New user registered:", req.email)

    return {
        "access_token": token,
        "user": {
            "id": user_id,
            "name": req.name,
            "email": req.email
        }
    }


# ===============================
# LOGIN
# ===============================

@router.post("/login")
async def login(req: LoginRequest):
    user = users_collection.find_one({"email": req.email.lower()})
    if not user:
        raise HTTPException(400, "Invalid credentials")

    if not verify_password(req.password, user.get("password_hash", "")):
        raise HTTPException(400, "Invalid credentials")

    token = create_access_token(
        {"user_id": str(user["_id"])},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": token, "user": {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "mobile": user.get("mobile")
    }}


# ===============================
# GET PROFILE
# ===============================

@router.get("/me")
async def me(request: Request):
    auth = request.headers.get("authorization")
    if not auth:
        raise HTTPException(401, "Missing Authorization")

    token = auth.split()[1]
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(401, "Invalid token")

    user.pop("password_hash", None)
    return {"user": user}


# ===============================
# UPDATE PROFILE
# ===============================

@router.put("/me")
async def update_profile(request: Request, body: UpdateProfileRequest):
    auth = request.headers.get("authorization")
    if not auth:
        raise HTTPException(401, "Missing Authorization")

    token = auth.split()[1]
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(401, "Invalid token")

    update_data = {}
    if body.name:
        update_data["name"] = body.name
    if body.mobile:
        update_data["mobile"] = body.mobile

    if update_data:
        users_collection.update_one(
            {"_id": ObjectId(user["_id"])},
            {"$set": update_data}
        )

    updated = users_collection.find_one({"_id": ObjectId(user["_id"])})
    updated.pop("password_hash", None)
    updated["_id"] = str(updated["_id"])

    return {"user": updated}


# ===============================
# DELETE ACCOUNT
# ===============================

@router.delete("/me")
async def delete_account(request: Request):
    auth = request.headers.get("authorization")
    if not auth:
        raise HTTPException(401, "Missing Authorization")

    token = auth.split()[1]
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(401, "Invalid token")

    from db.mongo import notes_collection, history_collection

    uid = ObjectId(user["_id"])
    notes_collection.delete_many({"user_id": str(uid)})
    history_collection.delete_many({"user_id": str(uid)})
    users_collection.delete_one({"_id": uid})

    return {"message": "Account and user data deleted"}
