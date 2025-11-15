from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY")

# Initialize AI client
client = Groq(api_key=GROQ_KEY)

def ai(prompt):
    """
    Sends a prompt to Groq Llama 3 (free) and returns the AI response.
    """
    response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

    return response.choices[0].message.content



# Summarize text
def summarize_text(text):
    prompt = f"Summarize this text in bullet points:\n\n{text}"
    return ai(prompt)


# Answer question strictly from given text
def answer_question(text, question):
    prompt = f"""
Use ONLY the following text to answer the question.
If answer is not found, say "Information not available in the provided text."

TEXT:
{text}

QUESTION:
{question}
"""
    return ai(prompt)
