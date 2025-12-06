from fastapi import APIRouter, BackgroundTasks, Request
from pydantic import BaseModel
from services.ai_service import (
    ai,
    summarize_text,
    generate_notes,
    explain_topic,
    answer_question,
    generate_mindmap,
    generate_flashcards
)
from services.history_service import save_history
from auth_utils import get_current_user_optional
# Removed unused import: notes_collection 
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
    num_questions: int = 5

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
        print(f"Error in /explain: {e}") # Log error to terminal
        return {"error": f"Explain error: {str(e)}"}


# 2️⃣ Make Notes
@router.post("/make-notes")
async def make_notes(request: NoteRequest, req: Request, background_tasks: BackgroundTasks):
    try:
        # 1. Generate Notes (Returns Dict)
        notes_data = generate_notes(request.text)

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

        return {"notes_data": notes_data}

    except Exception as e:
        print(f"Error in /make-notes: {e}")
        return {"error": f"Notes error: {str(e)}"}


# 3️⃣ Make MCQs
@router.post("/make-mcq")
async def make_mcq(request: MCQRequest, req: Request, background_tasks: BackgroundTasks):
    try:
        # 1. Validation: Limit the number to avoid timeout/token errors
        count = max(1, min(request.num_questions, 20))

        # 2. The Professional Prompt
        prompt = (
            f"You are a strict educational API that outputs only raw JSON.\n"
            f"Task: Create exactly {count} professional multiple-choice questions "
            f"based on the text provided below.\n\n"
            
            f"Constraints:\n"
            f"1. Output MUST be a valid JSON array.\n"
            f"2. Do NOT write 'Here are the questions' or any introductory text.\n"
            f"3. Do NOT use Markdown formatting (no ```json code blocks).\n"
            f"4. Each question must have 4 distinct options.\n"
            f"5. The 'correctAnswer' must match one of the options exactly.\n\n"
            
            f"Required JSON Structure:\n"
            f"[\n"
            f"  {{\n"
            f"    \"question\": \"Question text...\",\n"
            f"    \"options\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\"],\n"
            f"    \"correctAnswer\": \"Option A\",\n"
            f"    \"explanation\": \"Brief explanation of why this is correct.\"\n"
            f"  }}\n"
            f"]\n\n"
            
            f"Text to process:\n"
            f"\"\"\"{request.text}\"\"\""
        )

        # 3. Call your AI function
        raw_response = ai(prompt)
        
        # 4. Cleaning Step (Safety Net)
        try:
            # Find the first '[' and last ']' to ignore any extra text
            start_index = raw_response.find('[')
            end_index = raw_response.rfind(']') + 1
            
            if start_index != -1 and end_index != -1:
                clean_json = raw_response[start_index:end_index]
                mcqs = json.loads(clean_json)
            else:
                print("Error: No JSON brackets found in AI response")
                mcqs = [] # Fallback if AI fails completely
        except json.JSONDecodeError:
            print(f"Error: JSON Decode failed. Raw response: {raw_response}")
            return {"error": "Failed to parse AI response into JSON."}

        # 5. Get User & Save History
        user = await get_current_user_optional(req)

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
        print(f"Error in /make-mcq: {e}")
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
        print(f"Error in /summarize-text: {e}")
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
        print(f"Error in /qna: {e}")
        return {"error": f"QnA error: {str(e)}"}


# 6️⃣ AI Mind Map
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
        print(f"Error in /make-mindmap: {e}")
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
        print(f"Error in /make-flashcards: {e}")
        return {"error": f"Flashcard error: {str(e)}"}