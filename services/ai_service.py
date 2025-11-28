# ================================================================
#  AI SERVICES (WORLD-BEST EDUCATION EDITION) – PRODUCTION READY
# ================================================================

from groq import Groq
import os
from dotenv import load_dotenv
import re

load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY")

# Initialize AI client
client = Groq(api_key=GROQ_KEY)

# ================================================================
#  UNIVERSAL AI CALLER (Llama 3.3 70B Versatile)
# ================================================================
def ai(prompt: str):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content


# ================================================================
#  CLEANUP UTILITIES (Markdown tables + bullets + headings)
# ================================================================
def fix_markdown_tables(markdown: str) -> str:
    lines = markdown.split("\n")
    cleaned_lines = []
    current_table = []
    inside_table = False

    def flush_table(table_rows):
        if not table_rows:
            return []

        split_rows = []
        for row in table_rows:
            parts = [c.strip() for c in row.split("|") if c.strip() != ""]
            split_rows.append(parts)

        max_cols = max(len(r) for r in split_rows)
        normalized = []

        for r in split_rows:
            while len(r) < max_cols:
                r.append("")
            normalized.append(r)

        separator = ["-" * 8] * max_cols
        output = []
        output.append("| " + " | ".join(normalized[0]) + " |")
        output.append("| " + " | ".join(separator) + " |")

        for r in normalized[1:]:
            output.append("| " + " | ".join(r) + " |")

        return output

    for line in lines:
        if "|" in line and not line.strip().startswith("#") and not line.strip().startswith("```"):
            inside_table = True
            current_table.append(line)
        else:
            if inside_table:
                cleaned_lines.extend(flush_table(current_table))
                current_table = []
                inside_table = False
            cleaned_lines.append(line)

    if inside_table:
        cleaned_lines.extend(flush_table(current_table))

    return "\n".join(cleaned_lines)


def fix_headings(markdown: str) -> str:
    markdown = re.sub(r"####+", "####", markdown)
    markdown = re.sub(r"###", "###", markdown)
    markdown = re.sub(r"##", "##", markdown)
    return markdown


def fix_bullets(markdown: str) -> str:
    markdown = re.sub(r"^\* ", "- ", markdown, flags=re.MULTILINE)
    markdown = re.sub(r"– ", "- ", markdown)
    markdown = re.sub(r"− ", "- ", markdown)
    return markdown


# ================================================================
#  EXPLAIN TOPIC — WORLD’S BEST EDUCATIONAL OUTPUT
# ================================================================
def explain_topic(topic: str):
    prompt = f"""
You are the world's best educator. Explain the topic so clearly that a student
never needs YouTube or Google after reading your answer.

⚡ ALWAYS return in this EXACT JSON format ⚡:

[
  {{
    "title": "Section Title",
    "paragraph": "Short, simple, teaching-style paragraph.",
    "bullets": ["point 1", "point 2", "point 3"],
    "examples": ["example 1", "example 2"],
    "faqs": [
        {{"q": "question?", "a": "short clear answer"}}
    ],
    "important_terms": ["term 1", "term 2"]
  }}
]

📌 RULES:
- Create 3–7 sections.
- Paragraphs must be 2–4 lines maximum.
- Use simple language for school/college students.
- Bullets should be crisp.
- Give 1–2 real-life examples in each section.
- Provide important glossary terms.
- Provide 1–2 FAQs students actually ask.
- Output must be factual, complete, and extremely clear.
- No filler or generic content.

Now explain:

Topic: {topic}
"""
    return ai(prompt)


# ================================================================
#  PREMIUM SUMMARY GENERATOR — STRUCTURED + CLEAN
# ================================================================
def summarize_text(text: str):
    prompt = f"""
Create the world’s best structured summary of the text.

RULES:
- Identify REAL sections from the content.
- Use meaningful headings.
- Use short, clear explanatory bullets.
- Avoid fluff.
- Do NOT invent topics not present in the content.
- Keep formatting clean and study-friendly.

TEXT:
{text}
"""
    return ai(prompt)


# ================================================================
#  PREMIUM NOTES GENERATOR — CLEAN BULLET NOTES
# ================================================================
def generate_notes(text: str):
    prompt = f"""
Convert the text into perfect bullet-style revision notes.

RULES:
- Use section-wise structure.
- Use crisp bullet points only.
- Remove unnecessary explanations.
- Make points short and exam-friendly.
- Keep language simple.
- Do not invent new information.

TEXT:
{text}
"""
    return ai(prompt)


# ================================================================
#  STRICT QNA SYSTEM — NO HALLUCINATION
# ================================================================
def answer_question(text: str, question: str):
    prompt = f"""
Answer the question **strictly using the provided text only**.

⚠ RULES:
- If answer is missing, reply EXACTLY:
  "Information not available in the provided text."
- Keep answer short, clear, and factual.
- Use **bold** for key terms.
- Use bullets if helpful.

TEXT:
{text}

QUESTION:
{question}

Provide the answer now:
"""
    return ai(prompt)
