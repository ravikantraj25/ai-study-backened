from groq import Groq
import os
from dotenv import load_dotenv
import re
import json

load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY")

# Initialize AI client
client = Groq(api_key=GROQ_KEY)


# -------------------------------------------------------------
# 🌟 UNIVERSAL AI CALLER (clean + safe + consistent)
# -------------------------------------------------------------
def ai(prompt: str, model="llama-3.3-70b-versatile", temperature=0.2):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


# -------------------------------------------------------------
# 🌟 FIX MARKDOWN TABLES
# -------------------------------------------------------------
def fix_markdown_tables(markdown: str) -> str:
    lines = markdown.split("\n")
    cleaned_lines = []
    table_rows = []
    inside_table = False

    def flush_table(rows):
        if not rows:
            return []
        split_rows = []
        for row in rows:
            parts = [c.strip() for c in row.split("|") if c.strip()]
            split_rows.append(parts)

        max_cols = max(len(r) for r in split_rows)

        for r in split_rows:
            while len(r) < max_cols:
                r.append("")

        separator = ["--------"] * max_cols

        output = []
        output.append("| " + " | ".join(split_rows[0]) + " |")
        output.append("| " + " | ".join(separator) + " |")

        for r in split_rows[1:]:
            output.append("| " + " | ".join(r) + " |")

        return output

    for line in lines:
        if "|" in line and not line.startswith("#") and not line.startswith("```"):
            inside_table = True
            table_rows.append(line)
        else:
            if inside_table:
                cleaned_lines.extend(flush_table(table_rows))
                table_rows = []
                inside_table = False
            cleaned_lines.append(line)

    if inside_table:
        cleaned_lines.extend(flush_table(table_rows))

    return "\n".join(cleaned_lines)


# -------------------------------------------------------------
# 🌟 FIX BROKEN HEADINGS
# -------------------------------------------------------------
def fix_headings(md: str) -> str:
    md = re.sub(r"#####", "####", md)
    md = re.sub(r"####", "###", md)
    md = re.sub(r"###", "##", md)
    return md


# -------------------------------------------------------------
# 🌟 FIX BROKEN BULLETS
# -------------------------------------------------------------
def fix_bullets(md: str) -> str:
    md = re.sub(r"^\*", "- ", md, flags=re.MULTILINE)
    md = re.sub(r"– ", "- ", md)
    md = re.sub(r"— ", "- ", md)
    return md


# -------------------------------------------------------------
# 🌟 PREMIUM EXPLANATION ENGINE (BEST IN THE WORLD)
# -------------------------------------------------------------
def explain_topic_ai(topic: str):
    prompt = f"""
You are a world-class education AI for students.

Explain the topic below in the MOST structured, clean, high-quality way possible.

🎯 **OUTPUT MUST BE EXACT JSON LIST**:
[
  {{
    "title": "Section Title",
    "paragraph": "Short, simple explanation",
    "bullets": ["point 1", "point 2"]
  }}
]

📌 **RULES**
- Break topic into meaningful sections (3–6 sections)
- Each section must contain:
  - A clear short title
  - A simple paragraph
  - 2–6 bullet points
- NO long paragraphs
- NO repeated points
- NO generic sections
- JSON must be valid and parsable
- Make explanation suitable for students of any level

📘 Topic:
{topic}
    """

    response = ai(prompt)
    print("RAW EXPLANATION RAW:", response)

    # Ensure valid JSON
    try:
        parsed = json.loads(response)
        return parsed
    except:
        # Fix common bad JSON issues
        cleaned = (
            response.replace("```json", "")
            .replace("```", "")
            .replace("\n", "")
        )
        try:
            return json.loads(cleaned)
        except:
            return [{"title": "Explanation", "paragraph": response, "bullets": []}]


# -------------------------------------------------------------
# 🌟 PREMIUM SUMMARY GENERATOR
# -------------------------------------------------------------
def summarize_text(text: str):
    prompt = f"""
Create a clean, highly structured academic summary of the following text.

📌 **Rules**
- Derive headings ONLY from the text (NO generic headings)
- Use bullet points where helpful
- Keep summary clean, short, deep, and meaningful
- No unnecessary info
- No fluff

Text:
{text}
"""
    raw = ai(prompt)

    # Clean the response
    cleaned = fix_markdown_tables(raw)
    cleaned = fix_headings(cleaned)
    cleaned = fix_bullets(cleaned)
    return cleaned.strip()


# -------------------------------------------------------------
# 🌟 PREMIUM QUESTION ANSWERING
# -------------------------------------------------------------
def answer_question(text: str, question: str):
    prompt = f"""
Answer the question **ONLY based on the provided text**.

📌 RULES
- If answer is present → give a clean, short markdown answer
- Use bullets for clarity
- Highlight important words in **bold**
- If answer not present → reply exactly:
  "Information not available in the provided text."

TEXT:
{text}

QUESTION:
{question}

Now provide the answer:
"""
    return ai(prompt)
