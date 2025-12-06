from fastapi import APIRouter, Depends, HTTPException, Request
from db.mongo import history_collection
# 👇 CHANGE THIS: Import from auth_utils, not security
from auth_utils import get_current_user_optional 

router = APIRouter()

@router.get("/get")
async def get_user_history(req: Request):
    """
    Fetch the history for the logged-in user.
    """
    # 1. Get the current user
    user = await get_current_user_optional(req)

    # 2. Security Check: If not logged in, reject access
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # 3. Fetch history from MongoDB
    # We sort by 'created_at' descending (newest first) and limit to 50
    cursor = history_collection.find({"user_id": user["_id"]}).sort("created_at", -1).limit(50)
    
    history_list = []
    for doc in cursor:
        # Convert ObjectId to string for JSON compatibility
        doc["_id"] = str(doc["_id"])
        history_list.append(doc)

    return {"history": history_list}