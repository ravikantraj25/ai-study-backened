from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from services.pdf_service import extract_text_from_pdf
from services.ai_service import summarize_text, ai
from db.mongo import notes_collection


router = APIRouter()

@router.post("/summarize")
async def summarize_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Upload a PDF file")

    raw_text = extract_text_from_pdf(file.file)

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    summary = summarize_text(raw_text)

    # save in mongodb
    note = {
        "fileName": file.filename,
        "raw_text": raw_text,
        "summary": summary
    }

    result = notes_collection.insert_one(note)

    return {
        "note_id": str(result.inserted_id),
        "summary": summary,
        "raw_text": raw_text     # <-- REQUIRED for QnA
    }
