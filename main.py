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

# 📌 IMPORTS
from routes.summarize import router as summarize_router  # PDF Summary
from routes.study_assistant import router as study_router # Notes, MCQ, QnA, MindMap, Explain
from routes.auth import router as auth_router             # Login, Register
from routes.history import router as history_router       # History

# ------------------------------------------------------------
# Middleware: Allow large PDF uploads (20 MB)
# ------------------------------------------------------------
class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20MB
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
# CORS (IMPORTANT: must be before routes)
# ------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_credentials=True,
    allow_methods=["*"],         
    allow_headers=["*"],          
)


# ------------------------------------------------------------
# Add upload size middleware BEFORE routers
# ------------------------------------------------------------
app.add_middleware(LimitUploadSizeMiddleware)


# ------------------------------------------------------------
# Routers
# ------------------------------------------------------------
# 1. PDF Tools
app.include_router(summarize_router, tags=["PDF Tools"])

# 2. AI Study Tools (Notes, MCQ, QnA, Explain, Mind Map)
app.include_router(study_router, tags=["AI Study Tools"])

# 3. Authentication
app.include_router(auth_router, tags=["Authentication"])

# 4. User History
app.include_router(history_router, prefix="/api", tags=["History"]) 
# Note: I added prefix="/api" here because in your history route file you defined the route as "/history"
# If you want the URL to be /history, remove prefix. If you want /api/history, keep it. 
# Based on your frontend code (API + "/history"), you likely DON'T need the prefix here unless you change frontend.
# Let's keep it simple:
# app.include_router(history_router, tags=["History"])


# ------------------------------------------------------------
# Test Routes
# ------------------------------------------------------------
@app.get("/")
def home():
    return {"message": "AI Study Assistant Backend is Running!"}