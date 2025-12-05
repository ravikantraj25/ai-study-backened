from fastapi import APIRouter
from pydantic import BaseModel
from routes.study_assistant import ai   # <-- Use your existing AI wrapper

router = APIRouter()


# -----------------------------
# Request Model
# -----------------------------
class MCQRequest(BaseModel):
    text: str
    count: int = 5


# -----------------------------
# Convert AI raw text into structured MCQs
# -----------------------------
def parse_mcq_output(raw_text: str):
    """
    Converts AI text into structured MCQ objects.
    Expected AI output example:

    1. Question text
    A) Option 1
    B) Option 2
    C) Option 3
    D) Option 4
    Correct answer: B) Option 2
    """

    mcqs = []
    blocks = raw_text.strip().split("\n\n")

    current = {"question": "", "options": [], "answer": ""}

    for block in blocks:
        lines = block.strip().split("\n")

        # New MCQ question
        if lines[0].lstrip()[0].isdigit():  
            if current["question"]:
                mcqs.append(current)
            current = {"question": "", "options": [], "answer": ""}

            # Remove numbering like "1. " or "2)"
            q_text = lines[0].split(".", 1)[-1].strip()
            current["question"] = q_text

        # Options A,B,C,D
        for line in lines:
            if line.startswith(("A)", "B)", "C)", "D)")):
                current["options"].append(line[3:].strip())  # Keep only text

            # Correct answer
            if "Correct answer" in line:
                ans = line.split(":", 1)[1].strip()
                # Remove A), B)
                if ")" in ans:
                    ans = ans.split(")", 1)[1].strip()
                current["answer"] = ans

    if current["question"]:
        mcqs.append(current)

    return mcqs


# -----------------------------
# API Endpoint
# -----------------------------
@router.post("/make-mcq")
async def make_mcq(request: MCQRequest):
    try:
        prompt = f"""
Create {request.count} MCQs from the following text.
Each MCQ must follow this format strictly:

1. The question text
A) Option 1
B) Option 2
C) Option 3
D) Option 4
Correct answer: B) Option 2

Text:
{request.text}
        """

        raw_output = ai(prompt)

        parsed = parse_mcq_output(raw_output)

        return {"mcqs": parsed}

    except Exception as e:
        return {"error": f"MCQ error: {str(e)}"}
