from fastapi import APIRouter, Body
from services.ai_service import ai, summarize_text, answer_question
from db.mongo import notes_collection   # <-- added for notes route

router = APIRouter()

# 1️⃣ Explain any topic
@router.post("/explain")
async def explain_topic(payload: dict = Body(...)):
    topic = payload.get("topic", "")
    prompt = f"Explain the following topic in very simple and easy words:\n\n{topic}"
    return {"explanation": ai(prompt)}

# 2️⃣ Make notes
@router.post("/make-notes")
async def make_notes(payload: dict = Body(...)):
    text = payload.get("text", "")
    prompt = f"Convert the following text into clear bullet-point notes:\n\n{text}"
    return {"notes": ai(prompt)}

# 3️⃣ Make MCQs
@router.post("/make-mcq")
async def make_mcq(payload: dict = Body(...)):
    text = payload.get("text", "")
    prompt = f"Create 5 MCQs from the following text. Each MCQ must have 4 options and the correct answer:\n\n{text}"
    return {"mcqs": ai(prompt)}

# 4️⃣ Summarize general text (not PDF)
@router.post("/summarize-text")
async def summarize_any_text(payload: dict = Body(...)):
    text = payload.get("text", "")
    return {"summary": summarize_text(text)}

# 5️⃣ QnA from PDF
@router.post("/qna")
async def qna(payload: dict = Body(...)):
    text = payload.get("text", "")
    question = payload.get("question", "")
    return {"answer": answer_question(text, question)}

# 6️⃣ Fetch notes history (NEW ROUTE)
@router.get("/notes")
def get_notes():
    notes = list(notes_collection.find().sort("_id", -1))
    for n in notes:
        n["_id"] = str(n["_id"])  # Convert ObjectId to string
    return notes
