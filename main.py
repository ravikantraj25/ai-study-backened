from fastapi import FastAPI
from services.ai_service import ai
from routes.summarize import router as summarize_router
from routes.study_assistant import router as study_router

app = FastAPI()

app.include_router(summarize_router)
app.include_router(study_router)

@app.get("/")
def home():
    return {"message": "AI Study Assistant Backend is Running!"}

@app.get("/test-ai")
def test_ai():
    return {"response": ai("Explain gravity in simple words")}
