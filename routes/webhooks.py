# routes/webhooks.py
import os
import json
from fastapi import APIRouter, Request, HTTPException
from svix.webhooks import Webhook, WebhookVerificationError
from services.n8n import trigger_welcome_webhook # Import your saved function

router = APIRouter(tags=["webhooks"])

# You get this from Clerk Dashboard later
CLERK_WEBHOOK_SECRET = os.getenv("CLERK_WEBHOOK_SECRET")

@router.post("/clerk")
async def clerk_webhook(request: Request):
    """
    Listens for 'user.created' events from Clerk 
    and triggers the n8n welcome email.
    """
    if not CLERK_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Clerk Webhook Secret not set")

    # 1. Get Headers
    headers = request.headers
    svix_id = headers.get("svix-id")
    svix_timestamp = headers.get("svix-timestamp")
    svix_signature = headers.get("svix-signature")

    if not svix_id or not svix_timestamp or not svix_signature:
        raise HTTPException(status_code=400, detail="Missing svix headers")

    # 2. Get the Body
    payload = await request.body()
    body_text = payload.decode("utf-8")

    # 3. Verify Signature (Security)
    wh = Webhook(CLERK_WEBHOOK_SECRET)
    try:
        evt = wh.verify(body_text, headers)
    except WebhookVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 4. Handle the Event
    event_type = evt["type"]
    data = evt["data"]

    if event_type == "user.created":
        # Extract email and name from Clerk's data
        email_addresses = data.get("email_addresses", [])
        email = email_addresses[0]["email_address"] if email_addresses else None
        
        # Combine First + Last name
        first_name = data.get("first_name") or ""
        last_name = data.get("last_name") or ""
        full_name = f"{first_name} {last_name}".strip() or "User"

        if email:
            # CALL YOUR N8N FUNCTION HERE
            await trigger_welcome_webhook(full_name, email)

    return {"status": "ok"}