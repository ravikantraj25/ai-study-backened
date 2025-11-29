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
You are the world's best educator. Create a beautifully structured explanation for the topic.

⚡ VERY IMPORTANT — OUTPUT RULES ⚡
You MUST return ONLY valid JSON.
No markdown. No ```json. No notes. No text outside JSON.
If you cannot follow JSON, output an empty JSON array [].

📌 EXACT JSON FORMAT YOU MUST RETURN:
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

📌 CONTENT RULES:
- Create 3–6 well-organized sections.
- Each section MUST include:
  • title  
  • paragraph  
  • bullets  
  • examples  
  • faqs  
  • important_terms
- Paragraph must be 2–4 simple lines.
- Bullets must be crisp and factual.
- Examples must be real & relatable.
- FAQs must be 1–2 short Q&A per section.
- Terms must be meaningful & relevant.
- DO NOT add anything outside JSON.
- DO NOT use markdown formatting.

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
You are an expert academic note-maker. Convert the given content into exceptionally clean,
professionally structured bullet notes.

💎 OUTPUT FORMAT (STRICT):
Return ONLY valid JSON in the following structure:

{{
  "success": true,
  "style": "premium_bullet_notes",
  "notes": [
      "bullet 1",
      "bullet 2",
      "bullet 3"
  ]
}}

💎 OUTPUT RULES:
- Do NOT include hyphens, numbers, bullets, emojis, or special symbols inside note items.
- Do NOT return paragraphs.
- Do NOT write long sentences.
- Do NOT add extra or invented information.
- Do NOT repeat ideas.
- Merge related ideas into one clean bullet.
- Keep language simple and exam-friendly.
- Every bullet must be crisp, premium, and high-quality.

🎨 STYLE:
- Modern
- Minimal
- Elegant
- Highly readable
- World-class academic formatting

📘 INPUT TEXT:
{text}

Now generate the JSON output exactly in the above structure.
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
