# services/n8n.py
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

N8N_WELCOME_WEBHOOK = os.getenv("N8N_WELCOME_WEBHOOK")

async def trigger_welcome_webhook(name: str, email: str):
    """Send webhook to n8n asynchronously."""
    if not N8N_WELCOME_WEBHOOK:
        print("❌ ERROR: N8N_WELCOME_WEBHOOK missing from .env")
        return

    payload = {"name": name, "email": email}
    print(f"📨 Triggering Welcome Email for: {email}")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # We don't await the response to keep it fast, 
            # or you can await if you want to be sure it sent.
            await client.post(N8N_WELCOME_WEBHOOK, json=payload)
            print("✅ Email signal sent to n8n")
    except Exception as e:
        print("❌ Webhook Error:", e)