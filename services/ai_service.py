from groq import Groq
import os
from dotenv import load_dotenv
import re

load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY")

# Initialize AI client
client = Groq(api_key=GROQ_KEY)


# ---------------------------------------------------------------------
# ⭐ UNIVERSAL AI CALLER
# ---------------------------------------------------------------------
def ai(prompt: str):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content


# ---------------------------------------------------------------------
# ⭐ AUTO-CLEAN MARKDOWN TABLES
# ---------------------------------------------------------------------
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

        separator_row = ["-" * 8] * max_cols

        output = []
        output.append("| " + " | ".join(normalized[0]) + " |")
        output.append("| " + " | ".join(separator_row) + " |")

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


# ---------------------------------------------------------------------
# ⭐ AUTO-CLEAN HEADINGS (### → ## → # etc)
# ---------------------------------------------------------------------
def fix_headings(markdown: str) -> str:
    markdown = re.sub(r'####+', "####", markdown)
    markdown = re.sub(r'###', "###", markdown)
    markdown = re.sub(r'##', "##", markdown)
    return markdown


# ---------------------------------------------------------------------
# ⭐ AUTO-CLEAN BULLETS (Fix broken dash formatting)
# ---------------------------------------------------------------------
def fix_bullets(markdown: str) -> str:
    markdown = re.sub(r'^\* ', "- ", markdown, flags=re.MULTILINE)
    markdown = re.sub(r'– ', "- ", markdown)
    markdown = re.sub(r'− ', "- ", markdown)
    return markdown


# ---------------------------------------------------------------------
# ⭐ ADVANCED, BEAUTIFUL, STRUCTURED SUMMARY GENERATOR
# ---------------------------------------------------------------------
def summarize_text(text):
    prompt = f"""
    Summarize the text below in a clean, well-formatted structure.

    Rules:
    - Create headings based ONLY on the content (do NOT use generic headings).
    - Keep the summary formal, clean and easy to read.
    - Use bullet points wherever needed.
    - Do NOT add unnecessary sections like "Main Concepts", "Key Definitions" etc.
    - Only include headings that come from the real content.

    Text:
    {text}
    """

    response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}]
)


    return response.choices[0].message.content




# ---------------------------------------------------------------------
# ⭐ IMPROVED QUESTION ANSWERING (STRICT, CLEAN MARKDOWN)
# ---------------------------------------------------------------------
def answer_question(text: str, question: str):
    prompt = f"""
Answer the question **ONLY from the given text**.

RULES:
- Clean, short Markdown
- Bullet points allowed
- Highlight important words using **bold**
- If answer is not in text, reply exactly:
  **"Information not available in the provided text."**

TEXT:
{text}

QUESTION:
{question}

Provide the answer now:
"""
    return ai(prompt)
