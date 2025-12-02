from fastapi import APIRouter, Request, HTTPException
from db.mongo import history_collection
from auth_utils import get_user_from_token

router = APIRouter(prefix="/history", tags=["history"])

@router.get("")
def get_history(request: Request):
    auth = request.headers.get("authorization")
    if not auth:
        raise HTTPException(status_code=401, detail="Not logged in")

    token = auth.split()[1]
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    items = list(history_collection.find({"user_id": str(user["_id"])}).sort("created_at", -1))

    for i in items:
        i["_id"] = str(i["_id"])
        i["created_at"] = i["created_at"].isoformat()

    return {"history": items}
