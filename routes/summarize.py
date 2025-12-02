# backend/routes/summarize.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from services.pdf_service import extract_text_from_pdf
from services.ai_service import summarize_text
from db.mongo import notes_collection, history_collection
from auth_utils import get_current_user_optional
from bson import ObjectId

router = APIRouter()

@router.post("/summarize")
async def summarize_pdf(request: Request, file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Upload a PDF file")

    raw_text = extract_text_from_pdf(file.file)

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    summary = summarize_text(raw_text)

    # save in mongodb (notes)
    note = {
        "fileName": file.filename,
        "raw_text": raw_text,
        "summary": summary
    }

    result = notes_collection.insert_one(note)

    # Save history if user logged in
    user = await get_current_user_optional(request)
    if user:
        history_doc = {
            "user_id": str(user.get("_id") or user.get("id") or user.get("email")),
            "type": "pdf_summarize",
            "input": {"filename": file.filename},
            "result": summary,
            "created_at": __import__("datetime").datetime.utcnow()
        }
        history_collection.insert_one(history_doc)

    return {
        "note_id": str(result.inserted_id),
        "summary": summary,
        "raw_text": raw_text
    }
