from fastapi import APIRouter
from pydantic import BaseModel
from routes.study_assistant import ai

router = APIRouter()


class MCQRequest(BaseModel):
    text: str
    count: int = 5


def parse_mcq_output(raw_text: str):
    mcqs = []
    blocks = raw_text.strip().split("\n\n")

    current = {"question": "", "options": [], "answer": ""}

    for block in blocks:
        lines = block.strip().split("\n")

        # Detect question
        if lines[0].lstrip()[0].isdigit():
            if current["question"]:
                mcqs.append(current)

            current = {"question": "", "options": [], "answer": ""}
            current["question"] = lines[0].split(".", 1)[1].strip()

        # Options
        for line in lines:
            if line.startswith(("A)", "B)", "C)", "D)")):
                current["options"].append(line[3:].strip())

            # Answer
            if "Correct answer" in line:
                ans = line.split(":", 1)[1].strip()
                if ")" in ans:
                    ans = ans.split(")", 1)[1].strip()
                current["answer"] = ans

    if current["question"]:
        mcqs.append(current)

    return mcqs


@router.post("/make-mcq")
async def make_mcq(request: MCQRequest):
    try:
        prompt = f"""
Generate {request.count} MCQs from this text.

Format EXACTLY like this:

1. Question text  
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
        return {"error": str(e)}
