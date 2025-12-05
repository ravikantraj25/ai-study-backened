from fastapi import APIRouter, BackgroundTasks, Request
from pydantic import BaseModel
from services.ai_service import (
    ai,
    summarize_text,
    generate_notes,
    explain_topic,
    answer_question,
    generate_mindmap,  # <--- Ensure this is imported
    generate_flashcards
)
from services.history_service import save_history
from auth_utils import get_current_user_optional
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

class MindMapRequest(BaseModel):
    text: str

class FlashcardRequest(BaseModel):
    text: str
# ----------------------------
# 📌 ROUTES
# ----------------------------

# 1️⃣ Explain topic
@router.post("/explain")
async def explain_topic_route(request: ExplainRequest, req: Request, background_tasks: BackgroundTasks):
    try:
        # 1. Generate Explanation
        explanation = explain_topic(request.topic)
        
        # 2. Get User (Optional)
        user = await get_current_user_optional(req)

        # 3. Save History (if logged in)
        if user:
            background_tasks.add_task(
                save_history,
                user_id=str(user["_id"]),
                action_type="explain",
                input_data={"topic": request.topic},
                result_data=explanation
            )

        return {"explanation": explanation}
    except Exception as e:
        return {"error": f"Explain error: {str(e)}"}


# 2️⃣ Make Notes
@router.post("/make-notes")
async def make_notes(request: NoteRequest, req: Request, background_tasks: BackgroundTasks):
    try:
        # 1. Generate Notes (Returns Dict)
        notes_data = generate_notes(request.text)

        # 🚨 ENSURE THIS LINE IS DELETED OR COMMENTED OUT:
        # data = json.loads(notes_data) 

        # 2. Get User (for history)
        user = await get_current_user_optional(req)

        if user:
            background_tasks.add_task(
                save_history,
                user_id=str(user["_id"]),
                action_type="make_notes",
                input_data={"text": request.text[:200] + "..."}, 
                result_data=notes_data
            )

        # 3. Return notes_data DIRECTLY
        return {"notes_data": notes_data}

    except Exception as e:
        return {"error": f"Notes error: {str(e)}"}


# 3️⃣ Make MCQs
@router.post("/make-mcq")
async def make_mcq(request: MCQRequest, req: Request, background_tasks: BackgroundTasks):
    try:
        # 1. Generate MCQs
        prompt = (
            f"Create 5 MCQs from the following text. "
            f"Each MCQ must have 4 options and the correct answer:\n\n{request.text}"
        )
        mcqs = ai(prompt)

        # 2. Get User
        user = await get_current_user_optional(req)

        # 3. Save History
        if user:
            background_tasks.add_task(
                save_history,
                user_id=str(user["_id"]),
                action_type="make_mcq",
                input_data={"text": request.text[:200] + "..."},
                result_data=mcqs 
            )

        return {"mcqs": mcqs}
    except Exception as e:
        return {"error": f"MCQ error: {str(e)}"}


# 4️⃣ Summarize text
@router.post("/summarize-text")
async def summarize_any_text(request: SummarizeTextRequest, req: Request, background_tasks: BackgroundTasks):
    try:
        # 1. Generate Summary
        summary = summarize_text(request.text)

        # 2. Get User
        user = await get_current_user_optional(req)

        # 3. Save History
        if user:
            background_tasks.add_task(
                save_history,
                user_id=str(user["_id"]),
                action_type="summarize",
                input_data={"text": request.text[:200] + "..."},
                result_data=summary
            )

        return {"summary": summary}
    except Exception as e:
        return {"error": f"Summary error: {str(e)}"}


# 5️⃣ PDF QnA / Ask Question
@router.post("/qna") 
async def qna(request: QnARequest, req: Request, background_tasks: BackgroundTasks):
    try:
        # 1. Generate Answer
        answer_data = answer_question(request.text, request.question)
        
        # 2. Get User
        user = await get_current_user_optional(req)

        # 3. Save History
        if user:
            background_tasks.add_task(
                save_history,
                user_id=str(user["_id"]),
                action_type="qna",
                input_data={"question": request.question, "text": request.text[:100] + "..."},
                result_data=answer_data
            )

        return {"answer_data": answer_data}

    except Exception as e:
        return {"error": f"QnA error: {str(e)}"}


# 6️⃣ AI Mind Map (Corrected Indentation)
@router.post("/make-mindmap")
async def make_mindmap_route(request: MindMapRequest, req: Request, background_tasks: BackgroundTasks):
    try:
        # 1. Generate Code
        mermaid_code = generate_mindmap(request.text)

        # 2. Get User & Save History
        user = await get_current_user_optional(req)
        
        if user:
            background_tasks.add_task(
                save_history,
                user_id=str(user["_id"]),
                action_type="mindmap",
                input_data={"text": request.text[:100] + "..."},
                result_data={"code": mermaid_code}
            )

        return {"mermaid_code": mermaid_code}
    except Exception as e:
        return {"error": f"MindMap error: {str(e)}"}
    
# 7️⃣ Generate Flashcards
@router.post("/make-flashcards")
async def make_flashcards_route(request: FlashcardRequest, req: Request, background_tasks: BackgroundTasks):
    try:
        # Generate
        cards = generate_flashcards(request.text)

        # Save History
        user = await get_current_user_optional(req)
        if user:
            background_tasks.add_task(
                save_history,
                user_id=str(user["_id"]),
                action_type="flashcards",
                input_data={"text": request.text[:100] + "..."},
                result_data=cards
            )

        return {"flashcards": cards}
    except Exception as e:
        return {"error": f"Flashcard error: {str(e)}"}