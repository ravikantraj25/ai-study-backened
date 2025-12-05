from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
from ai_model import ai   # <-- your AI wrapper

router = APIRouter()

# ---- Request Schema ----
class MCQRequest(BaseModel):
    text: str
    count: int = 5


# ---- MCQ Route ----
@router.post("/make-mcq")
async def make_mcq(request: MCQRequest):
    """
    Returns clean JSON MCQs usable directly by frontend.
    """

    try:
        # ---- AI Prompt ----
        prompt = f"""
Generate {request.count} MCQs from the following text.

Each MCQ MUST follow this JSON format:

[
  {{
    "question": "Question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "Correct option text"
  }}
]

Rules:
- Return ONLY valid JSON.
- Do NOT include explanations.
- Do NOT include markdown like ```json.

Text:
{request.text}
"""

        ai_response = ai(prompt).strip()

        # ---- Clean AI Output (remove unwanted formatting) ----
        cleaned = (
            ai_response.replace("```json", "")
                       .replace("```", "")
                       .strip()
        )

        # ---- Parse JSON ----
        try:
            mcqs = json.loads(cleaned)
        except Exception as parse_error:
            raise HTTPException(
                status_code=500,
                detail=f"JSON parsing failed. Raw AI output: {cleaned}"
            )

        # ---- Validate JSON ----
        if not isinstance(mcqs, list):
            raise HTTPException(
                status_code=500,
                detail="MCQ output must be a list."
            )

        for q in mcqs:
            if not all(k in q for k in ("question", "options", "answer")):
                raise HTTPException(
                    status_code=500,
                    detail="Each MCQ must contain question, options, answer."
                )

        return {"mcqs": mcqs}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCQ error: {str(e)}")
