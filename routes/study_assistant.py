from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_service import ai, summarize_text, answer_question
from db.mongo import notes_collection

router = APIRouter()

# ----------------------------
# 📌 Request Models
# ----------------------------

class ExplainRequest(BaseModel):
    topic: str

class NotesRequest(BaseModel):
    text: str

class MCQRequest(BaseModel):
    text: str

class SummarizeTextRequest(BaseModel):
    text: str

class QnARequest(BaseModel):
    text: str
    question: str


# ----------------------------
# 📌 Routes
# ----------------------------

# 1️⃣ Explain any topic
@router.post("/explain")
async def explain_topic(request: ExplainRequest):
    prompt = f"Explain the following topic in very simple and easy words:\n\n{request.topic}"
    return {"explanation": ai(prompt)}

# 2️⃣ Make notes
@router.post("/make-notes")
async def make_notes(request: NotesRequest):
    prompt = f"Convert the following text into clear bullet-point notes:\n\n{request.text}"
    return {"notes": ai(prompt)}

# 3️⃣ Make MCQs
@router.post("/make-mcq")
async def make_mcq(request: MCQRequest):
    prompt = f"Create 5 MCQs from the following text. Each MCQ must have 4 options and the correct answer:\n\n{request.text}"
    return {"mcqs": ai(prompt)}

# 4️⃣ Summarize text
@router.post("/summarize-text")
async def summarize_any_text(request: SummarizeTextRequest):
    return {"summary": summarize_text(request.text)}

# 5️⃣ QnA from PDF text
@router.post("/qna")
async def qna(request: QnARequest):
    return {"answer": answer_question(request.text, request.question)}

# 6️⃣ Fetch saved notes
@router.get("/notes")
def get_notes():
    notes = list(notes_collection.find().sort("_id", -1))
    for n in notes:
        n["_id"] = str(n["_id"])
    return notes
