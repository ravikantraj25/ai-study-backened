from fastapi import APIRouter, Request, HTTPException, Depends
from db.mongo import history_collection
from auth_utils import get_current_user_optional # or your specific auth function
from bson import ObjectId

router = APIRouter()

@router.get("/history")
async def get_user_history(request: Request):
    # 1. Get User from Token
    user = await get_current_user_optional(request)
    
    if not user:
        raise HTTPException(status_code=401, detail="Please login to view history")

    user_id = str(user.get("_id") or user.get("id"))

    # 2. Fetch History for THIS user only
    items = list(history_collection.find({"user_id": user_id}).sort("created_at", -1))

    # 3. Clean up ObjectId for JSON response
    for i in items:
        i["_id"] = str(i["_id"])
        if "created_at" in i:
            i["created_at"] = i["created_at"].isoformat()

    return {"history": items}