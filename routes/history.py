from fastapi import APIRouter, HTTPException, Depends
from db.mongo import history_collection
from security import get_current_user  # ✅ Use the new Security file
# We don't need 'Request' or 'ObjectId' for the query logic anymore

router = APIRouter()

@router.get("/history")
def get_user_history(user_id: str = Depends(get_current_user)): 
    # 1. Auth: user_id is now injected directly by Clerk/Security
    # It will look like "user_2xyz..."
    
    # 2. Fetch History using the Clerk ID
    # Note: We use 'def' instead of 'async def' because PyMongo is synchronous. 
    # FastAPI handles this better in a thread pool.
    items = list(history_collection.find({"user_id": user_id}).sort("created_at", -1))

    # 3. Clean up ObjectId for JSON response
    for i in items:
        i["_id"] = str(i["_id"])
        if "created_at" in i:
            i["created_at"] = i["created_at"].isoformat()

    return {"history": items}