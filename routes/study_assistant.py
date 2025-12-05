from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_service import (
    ai,
    summarize_text,
    generate_notes,
    explain_topic,
    answer_question,
)
from db.mongo import notes_collection
import json

router = APIRouter()

# ----------------------------
# 📌 Request Models
# ----------------------------

class ExplainRequest(BaseModel):
    topic: str

class NoteRequest(BaseModel):
    text: str

class MCQRequest(BaseModel):
    text: str

class SummarizeTextRequest(BaseModel):
    text: str

class QnARequest(BaseModel):
    text: str
    question: str


# ----------------------------
# 📌 ROUTES
# ----------------------------

# 1️⃣ Explain topic
@router.post("/explain")
async def explain_topic_route(request: ExplainRequest):
    try:
        explanation = explain_topic(request.topic)
        return {"explanation": explanation}
    except Exception as e:
        return {"error": f"Explain error: {str(e)}"}


# 2️⃣ Make Notes — UPDATED FOR PREMIUM JSON
@router.post("/make-notes")
async def make_notes(request: NoteRequest):
    try:
        # 1. generate_notes NOW returns a Dictionary (thanks to force_json)
        notes_data = generate_notes(request.text)

        # 🚨 DELETE THIS LINE if you have it:
        # data = json.loads(notes_data) 

        # 2. Use notes_data directly
        return {
            "notes_data": notes_data 
        }

    except Exception as e:
        return {"error": f"Notes error: {str(e)}"}


# 3️⃣ Make MCQs
@router.post("/make-mcq")
async def make_mcq(request: MCQRequest):
    try:
        prompt = (
            f"Create 5 MCQs from the following text. "
            f"Each MCQ must have 4 options and the correct answer:\n\n{request.text}"
        )
        mcqs = ai(prompt)
        return {"mcqs": mcqs}
    except Exception as e:
        return {"error": f"MCQ error: {str(e)}"}


# 4️⃣ Summarize text
@router.post("/summarize-text")
async def summarize_any_text(request: SummarizeTextRequest):
    try:
        summary = summarize_text(request.text)
        return {"summary": summary}
    except Exception as e:
        return {"error": f"Summary error: {str(e)}"}


# 5️⃣ PDF QnA
@router.post("/qna")
async def qna(request: QnARequest):
    try:
        answer = answer_question(request.text, request.question)
        return {"answer": answer}
    except Exception as e:
        return {"error": f"QnA error: {str(e)}"}


# 6️⃣ Fetch saved notes
@router.get("/notes")
def get_notes():
    notes = list(notes_collection.find().sort("_id", -1))
    for n in notes:
        n["_id"] = str(n["_id"])
    return notes
