# 📚 AI Study Assistant – Backend (FastAPI + Groq + MongoDB)

This is the backend for the **AI Study Assistant**, a Generative-AI powered tool that helps students with:

- PDF Summarization  
- Notes Creation  
- Topic Explanation  
- Q&A from Content  
- MCQ Generation  
- Saving notes to MongoDB  

The backend is built using **FastAPI**, **Groq AI**, and **MongoDB Atlas**, and exposes clean REST APIs for frontend integration.

---

## 🚀 Features

### 🔹 1. PDF Summarization  
Upload a PDF → Extract text → AI summarizes it in simple bullet points.

### 🔹 2. Topic Explanation  
Explain any topic in simple and easy-to-understand language.

### 🔹 3. Q&A from Content  
Ask questions from text or notes → AI answers based on content.

### 🔹 4. Notes Storage  
Summaries and extracted text are saved in MongoDB Cloud.

### 🔹 5. MCQ Generator (Optional API)
AI can create multiple-choice questions from content.

---

## 🧠 Tech Stack

| Layer | Technology |
|------|------------|
| Backend Framework | **FastAPI** |
| AI Model | **Groq (Llama 3.1 8B Instant)** |
| Database | **MongoDB Atlas** |
| PDF Processing | **PyPDF2** |
| Environment | Python 3.10+ |
| Deployment | Render / Railway (optional) |

---

## 📁 Project Folder Structure

```
ai-study-backend/
│
├── main.py
├── requirements.txt
├── .env
├── .gitignore
│
├── db/
│   └── mongo.py
│
├── services/
│   ├── ai_service.py
│   └── pdf_service.py
│
├── routes/
│   ├── summarize.py
│   └── study_assistant.py
│
└── venv/        # Ignored from git
```

