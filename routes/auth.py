# backend/routes/auth.py
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from auth_utils import hash_password, verify_password, create_access_token, get_user_from_token
from db.mongo import users_collection
from bson import ObjectId
import os
import asyncio
import httpx

router = APIRouter(prefix="/auth", tags=["auth"])

# ------------------------------
# Environment
# ------------------------------
N8N_WELCOME_WEBHOOK = os.getenv("N8N_WELCOME_WEBHOOK")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

print("🔗 Loaded N8N Webhook URL:", N8N_WELCOME_WEBHOOK)  # Debugging


# ------------------------------
# Request Models
# ------------------------------
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


# ------------------------------
# Async Webhook Sender (Fixed)
# ------------------------------
async def trigger_welcome_webhook(name: str, email: str):
    if not N8N_WELCOME_WEBHOOK:
        print("❌ ERROR: N8N_WELCOME_WEBHOOK not set in environment!")
        return

    payload = {"name": name, "email": email}
    print("📨 Sending data to N8N webhook:", payload)

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.post(N8N_WELCOME_WEBHOOK, json=payload)
            print("✅ Webhook Response:", res.status_code, res.text)
    except Exception as e:
        print("❌ Webhook Error:", e)


# ------------------------------
# REGISTER ROUTE (Updated)
# ------------------------------
@router.post("/register")
async def register(req: RegisterRequest, background_tasks: BackgroundTasks):

    # Check existing account
    if users_collection.find_one({"email": req.email.lower()}):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed = hash_password(req.password)

    # Create user document
    doc = {
        "name": req.name,
        "email": req.email.lower(),
        "password_hash": hashed,
        "mobile": req.mobile,
        "created_at": __import__("datetime").datetime.utcnow()
    }

    # Insert into DB
    res = users_collection.insert_one(doc)
    user_id = str(res.inserted_id)

    # Create JWT token
    token = create_access_token(
        {"user_id": user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Trigger welcome email (async)
    background_tasks.add_task(
        lambda: asyncio.run(trigger_welcome_webhook(req.name, req.email))
    )

    print("🎉 User registered:", req.email)

    # Return response
    return {
        "access_token": token,
        "user": {"id": user_id, "name": req.name, "email": req.email}
    }


# ------------------------------
# LOGIN
# ------------------------------
@router.post("/login")
async def login(req: LoginRequest):
    user = users_collection.find_one({"email": req.email.lower()})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(req.password, user.get("password_hash", "")):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    user_id = str(user["_id"])

    token = create_access_token(
        {"user_id": user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": token,
        "user": {
            "id": user_id,
            "name": user.get("name"),
            "email": user.get("email"),
            "mobile": user.get("mobile")
        }
    }


# ------------------------------
# GET PROFILE
# ------------------------------
@router.get("/me")
async def me(request: Request):
    auth = request.headers.get("authorization")
    if not auth:
        raise HTTPException(status_code=401, detail="Missing Authorization")

    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = parts[1]
    user = get_user_from_token(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    user.pop("password_hash", None)
    return {"user": user}


# ------------------------------
# UPDATE PROFILE
# ------------------------------
@router.put("/me")
async def update_profile(request: Request, body: UpdateProfileRequest):
    auth = request.headers.get("authorization")
    if not auth:
        raise HTTPException(status_code=401, detail="Missing Authorization")

    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = parts[1]
    user = get_user_from_token(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    update = {}
    if body.name:
        update["name"] = body.name
    if body.mobile:
        update["mobile"] = body.mobile

    if update:
        users_collection.update_one({"_id": ObjectId(user["_id"])}, {"$set": update})

    user = users_collection.find_one({"_id": ObjectId(user["_id"])})
    user.pop("password_hash", None)
    user["_id"] = str(user["_id"])

    return {"user": user}


# ------------------------------
# DELETE ACCOUNT
# ------------------------------
@router.delete("/me")
async def delete_account(request: Request):
    auth = request.headers.get("authorization")
    if not auth:
        raise HTTPException(status_code=401, detail="Missing Authorization")

    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = parts[1]
    user = get_user_from_token(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    from db.mongo import notes_collection, history_collection

    uid = ObjectId(user["_id"])

    notes_collection.delete_many({"user_id": str(uid)})
    history_collection.delete_many({"user_id": str(uid)})
    users_collection.delete_one({"_id": uid})

    return {"message": "Account and user data deleted"}
