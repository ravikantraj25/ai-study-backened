from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.summarize import router as summarize_router
from routes.study_assistant import router as study_router
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


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
app = FastAPI()


# ------------------------------------------------------------
# FIXED: CORS applied BEFORE routers
# ------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # allow all origins
    allow_credentials=True,
    allow_methods=["*"],          # VERY IMPORTANT (allows OPTIONS)
    allow_headers=["*"],          # allow all headers
)


# ------------------------------------------------------------
# Add upload size middleware BEFORE routers
# ------------------------------------------------------------
app.add_middleware(LimitUploadSizeMiddleware)


# ------------------------------------------------------------
# Routers
# ------------------------------------------------------------
app.include_router(summarize_router)
app.include_router(study_router)


# ------------------------------------------------------------
# Test Routes
# ------------------------------------------------------------
@app.get("/")
def home():
    return {"message": "AI Study Assistant Backend is Running!"}
