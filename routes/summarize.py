from fastapi import APIRouter, UploadFile, File, HTTPException, Request, BackgroundTasks
from services.pdf_service import extract_text_from_pdf
from services.ai_service import summarize_text
from services.history_service import save_history  # <--- Use the service
from auth_utils import get_current_user_optional
from db.mongo import notes_collection # Keeping this if you still use the legacy notes collection

router = APIRouter()

@router.post("/summarize")
async def summarize_pdf(
    request: Request, 
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...)
):
    # 1. Validate File Type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a valid PDF file")

    # 2. Extract Text
    try:
        raw_text = extract_text_from_pdf(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF (file might be empty or scanned images).")

    # 3. Generate Summary using AI
    try:
        summary = summarize_text(raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")

    # 4. (Optional) Save to legacy 'notes' collection if your app still needs it
    # note_doc = {
    #     "fileName": file.filename,
    #     "raw_text": raw_text,
    #     "summary": summary
    # }
    # result = notes_collection.insert_one(note_doc)

    # 5. SAVE HISTORY (The Modern Way)
    user = await get_current_user_optional(request)
    
    if user:
        # Use background task for non-blocking save
        background_tasks.add_task(
            save_history,
            user_id=str(user["_id"]),
            action_type="pdf_summarize",
            input_data={"filename": file.filename},
            result_data=summary
        )

    # 6. Return Response
    return {
        "summary": summary,
        "filename": file.filename,
        # "note_id": str(result.inserted_id) # Uncomment if using legacy notes_collection above
    }