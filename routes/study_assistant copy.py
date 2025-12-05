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
async def make_notes(request: NotesRequest):
    try:
        raw = generate_notes(request.text)      # AI returns JSON string
        data = json.loads(raw)                  # Convert string → dict
        return data                             
    except Exception as e:
        return {"error": f"Notes error: {str(e)}"}


# 3️⃣ Make MCQs
@router.post("/make-mcq")
async def make_mcq(request: MCQRequest):
    try:
        prompt = (
            "Create 5 MCQs from the following text.\n"
            "Return ONLY valid JSON in this exact format:\n\n"
            "{\n"
            "  \"mcqs\": [\n"
            "    {\n"
            "      \"question\": \"...\",\n"
            "      \"options\": [\"A...\", \"B...\", \"C...\", \"D...\"],\n"
            "      \"answer\": \"B\"\n"
            "    }\n"
            "  ]\n"
            "}\n\n"
            f"Text:\n{request.text}"
        )

        ai_response = ai(prompt)

        import json
        # Ensure the AI response parses as JSON
        data = json.loads(ai_response)

        return data
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
