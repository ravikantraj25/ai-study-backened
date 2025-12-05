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
You are an expert Professor and Communicator. Your goal is to explain the input deeply, clearly, and engagingly.

⚡ INTERNAL RULES ⚡
1. ANALYZE THE INPUT:
   - If '{topic}' is a broad subject (e.g., "Photosynthesis"), structure it logically (Intro -> Process -> Importance).
   - If '{topic}' is a specific question (e.g., "Why do leaves change color?"), make the first section a DIRECT answer, then expand on context.
   
2. CONTENT STYLE:
   - Use clear, conversational, yet academic language.
   - Use ANALOGIES in the "paragraph" or "examples" fields to explain complex ideas.
   - Avoid Markdown characters (like **, ##, or -) inside the JSON values. Keep text clean.

3. JSON STRUCTURE (Strict Enforcement):
   - Return ONLY a valid JSON array.
   - No text before or after the JSON.
   - No ```json code blocks.

📌 EXACT JSON FORMAT:
[
  {{
    "title": "Clear Section Heading",
    "paragraph": "A comprehensive explanation (3-5 sentences). If complex, use an analogy.",
    "bullets": [
      "Key fact or step 1",
      "Key fact or step 2 (keep these distinct and factual)",
      "Key fact or step 3"
    ],
    "examples": [
      "Real-world application or scenario",
      "A relatable comparison/analogy"
    ],
    "faqs": [
      {{"q": "A common misconception or follow-up question?", "a": "A short, precise correction or answer."}}
    ],
    "important_terms": ["KeyTerm1", "KeyTerm2"]
  }}
]

📌 REQUIREMENTS:
- Generate 3 to 6 sections depending on depth required.
- Section 1 must always be the Introduction or Direct Answer.
- Ensure "important_terms" are actually used in the text.
- "faqs" should address what a student might be confused about.

Input Topic/Question: "{topic}"
"""

    # Assuming 'ai' and 'force_json' are your existing helper functions
    raw = ai(prompt)
    return force_json(raw)



# ================================================================
#  STRUCTURED SUMMARY GENERATOR
# ================================================================
def summarize_text(text: str):
    prompt = f"""
You are an expert Document Analyst. Your goal is to create a structured, visually appealing summary of the provided text.

⚡ ANALYZE THE DOCUMENT TYPE FIRST:
1. If it is a **RESUME/CV**: Focus on "Candidate Profile", "Top Skills", "Experience Highlights".
2. If it is **STUDY MATERIAL**: Focus on "Core Concepts", "Definitions", "Exam Key Points".
3. If it is **GENERAL**: Focus on "Executive Summary", "Key Details".

⚡ OUTPUT FORMAT (STRICT JSON):
You must return a valid JSON object. No Markdown. No text outside JSON.
{{
  "document_type": "Resume" | "Academic" | "General",
  "emoji": "📄",
  "title": "A short, catchy title for this document",
  "overview": "A 2-3 sentence high-level summary of the entire content.",
  "quick_stats": [
    {{"label": "e.g., Experience", "value": "4 Years"}},
    {{"label": "e.g., Key Topic", "value": "Photosynthesis"}} 
    // (Generate 2-4 relevant stats based on content)
  ],
  "sections": [
    {{
      "heading": "Section Title (e.g., Professional Experience or Light Reaction)",
      "content": "Brief summary of this section.",
      "bullets": ["Key detail 1", "Key detail 2", "Key detail 3"]
    }}
  ],
  "key_takeaways": ["Insight 1", "Insight 2", "Insight 3"]
}}

⚡ RULES:
- **Clean Text:** Do not use markdown (**, ##) inside strings.
- **Brevity:** Keep bullets crisp.
- **Relevance:** Only include information present in the text.

Input Text:
{text}
"""

    # Assuming you have the 'ai' and 'force_json' helpers from before
    raw = ai(prompt)
    return force_json(raw)


# ================================================================
#  PREMIUM NOTES GENERATOR
# ================================================================
def generate_notes(text: str):
    prompt = f"""
You are an expert Academic Tutor using the Cornell Note-Taking method.
Analyze the provided text and organize it into a structured, exam-ready study guide.

⚡ ANALYSIS RULES:
1. Identify the Main Topic and create a catchy Title.
2. Break the content into logical SECTIONS (e.g., "Introduction", "Process", "Key Factors").
3. Extract the most important facts as crisp, high-value BULLET POINTS.
4. Use **bold** markdown for key terms or definitions within the bullets.

⚡ JSON OUTPUT FORMAT (Strict):
Return ONLY a valid JSON object. No markdown blocks.
{{
  "title": "Main Subject of the Text",
  "summary": "A 1-sentence high-level overview.",
  "sections": [
    {{
      "heading": "Section Title (e.g. Core Principles)",
      "points": [
        "First key point with **important term** highlighted.",
        "Second key point regarding the specific detail.",
        "Third key point with a fact or number."
      ]
    }}
  ]
}}

⚡ CONTENT GUIDELINES:
- **No Fluff:** Remove filler words. Keep bullets direct and factual.
- **Hierarchy:** Group related ideas under the correct Heading.
- **Clarity:** Ensure even a beginner can understand the notes.
- **Accuracy:** Do not invent information.

Input Text:
{text}
"""
    # Assuming 'ai' and 'force_json' are your helpers
    raw = ai(prompt)
    return force_json(raw)



# ================================================================
#  STRICT QnA — ZERO HALLUCINATION
# ================================================================
def answer_question(text: str, question: str):
    prompt = f"""
You are an intelligent Exam Tutor. Answer the user's question based STRICTLY on the provided context text.

⚡ RULES:
1. **Direct Answer:** Provide a clear, concise answer (2-4 sentences).
2. **Evidence:** Extract the exact sentence/phrase from the text that supports your answer (for credibility).
3. **Formatting:** Use **bold** for key terms.
4. **Follow-up:** Suggest 3 smart follow-up questions the user might ask next.
5. **No Hallucinations:** If the answer is NOT in the text, return "success": false.

⚡ OUTPUT FORMAT (JSON ONLY):
{{
  "success": true,
  "answer": "The direct answer with **bold** keywords.",
  "evidence": "The exact quote from the text used to derive the answer.",
  "follow_ups": ["Question 1?", "Question 2?", "Question 3?"]
}}

OR (if answer not found):
{{
  "success": false,
  "answer": "I could not find the answer to that specific question in the provided text."
}}

CONTEXT TEXT:
{text}

USER QUESTION:
{question}
"""
    # Assuming 'ai' and 'force_json' are your existing helpers
    raw = ai(prompt)
    return force_json(raw)
