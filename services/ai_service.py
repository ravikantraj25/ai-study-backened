# ================================================================
#  AI SERVICES (WORLD-BEST EDUCATION EDITION) – PRODUCTION READY
# ================================================================

import json
import re
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ================================================================
#  UNIVERSAL AI CALLER (Stable)
# ================================================================
def ai(prompt: str):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


# ================================================================
#  SAFE JSON PARSER — FIXES AI OUTPUT
# ================================================================
def force_json(output: str):
    # Try direct JSON
    try:
        return json.loads(output)
    except:
        pass

    # Try extracting inside [...]
    try:
        match = re.search(r"\[.*\]", output, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except:
        pass

    # Final fallback: wrap as single section
    return [
        {
            "title": "Explanation",
            "paragraph": output,
            "bullets": [],
            "examples": [],
            "faqs": [],
            "important_terms": []
        }
    ]


# ================================================================
#  EXPLAIN TOPIC — BEST IN THE WORLD
# ================================================================
def explain_topic(topic: str):
    prompt = f"""
You are the world's best educator. Explain the topic so clearly that a student
never needs YouTube or Google after reading your answer.

⚡ ALWAYS return in THIS EXACT JSON FORMAT (no extra text!) ⚡

[
  {{
    "title": "Section Title",
    "paragraph": "Short simple explanation (2–4 lines).",
    "bullets": ["point 1", "point 2", "point 3"],
    "examples": ["real example 1", "real example 2"],
    "faqs": [
       {{"q": "student-style question?", "a": "short clear answer"}}
    ],
    "important_terms": ["term1", "term2"]
  }}
]

📌 RULES:
- Create 3–7 sections.
- Write like the best school/college teacher.
- Keep paragraphs short and clean.
- Bullets must be crisp and factual.
- Give real-life examples students can understand.
- Provide useful glossary terms.
- Add 1–2 FAQs per section.
- NO filler text.
- NO markdown outside JSON.
- ONLY valid JSON array.

Topic: {topic}
"""

    raw = ai(prompt)
    return force_json(raw)


# ================================================================
#  STRUCTURED SUMMARY GENERATOR
# ================================================================
def summarize_text(text: str):
    prompt = f"""
Summarize the text into a clean, structured study format.

Rules:
- Use headings based ONLY on real content.
- Use short, meaningful bullet points.
- Keep everything exam-friendly.
- No invented content.
- No fluff.

Text:
{text}
"""

    return ai(prompt)


# ================================================================
#  PREMIUM NOTES GENERATOR
# ================================================================
def generate_notes(text: str):
    prompt = f"""
Convert the text into exam-ready bullet notes.

Rules:
- Short bullets only.
- Section-wise grouping.
- No extra explanation.
- No invented info.
- Simple language.

TEXT:
{text}
"""
    return ai(prompt)


# ================================================================
#  STRICT QnA — ZERO HALLUCINATION
# ================================================================
def answer_question(text: str, question: str):
    prompt = f"""
Answer the question **ONLY using the provided text**.

Rules:
- If not found, reply EXACTLY:
  "Information not available in the provided text."
- Keep explanation short.
- Highlight key terms in **bold**.
- Use bullet points if helpful.

TEXT:
{text}

QUESTION:
{question}
"""
    return ai(prompt)
