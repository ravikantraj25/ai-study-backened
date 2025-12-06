# -------------------------------
# Load environment variables
# -------------------------------
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# 📌 IMPORTS (Updated to match your "routes" folder structure)
from routes.summarize import router as summarize_router   # Matches summarize.py
from routes.study_assistant import router as study_router # Matches study_assistant.py
from routes.history import router as history_router       # Matches history.py
from routes.webhooks import router as webhooks_router     # Matches webhooks.py

# ------------------------------------------------------------
# Middleware: Allow large PDF uploads (20 MB)
# ------------------------------------------------------------
class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20MB limit
        content_length = request.headers.get("content-length")

        if content_length and int(content_length) > MAX_UPLOAD_SIZE:
            return Response(
                content="File too large. Max allowed is 20 MB",
                status_code=413
            )

        return await call_next(request)


# ------------------------------------------------------------
# Create FastAPI app
# ------------------------------------------------------------
app = FastAPI(
    title="AI Study Assistant API",
    description="Backend for PDF Summarizer, Notes, MCQs, and Mind Maps",
    version="2.0"
)


# ------------------------------------------------------------
# MIDDLEWARE (Order is critical!)
# ------------------------------------------------------------
# 1. Add Upload Limit Middleware (Inner layer)
app.add_middleware(LimitUploadSizeMiddleware)

# 2. Add CORS Middleware (Outer layer - Runs first on incoming requests)
# This ensures that even if a file is too large, the frontend gets the correct CORS headers to read the error.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_credentials=True,
    allow_methods=["*"],         
    allow_headers=["*"],          
)


# ------------------------------------------------------------
# Routers (Grouped with prefixes)
# ------------------------------------------------------------

# 1. PDF Tools -> http://localhost:8000/api/pdf/summarize
app.include_router(summarize_router, prefix="/api/pdf", tags=["PDF Tools"])

# 2. AI Study Tools -> http://localhost:8000/api/study/explain
app.include_router(study_router, prefix="/api/study", tags=["AI Study Tools"])

# 3. Webhooks -> http://localhost:8000/api/webhooks/clerk
app.include_router(webhooks_router, prefix="/api/webhooks", tags=["Webhooks"])

# 4. User History -> http://localhost:8000/api/history/get
app.include_router(history_router, prefix="/api/history", tags=["History"]) 


# ------------------------------------------------------------
# Test Route
# ------------------------------------------------------------
@app.get("/")
def home():
    return {"message": "AI Study Assistant Backend is Running!"}