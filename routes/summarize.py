from fastapi import APIRouter, UploadFile, File, HTTPException, Request, BackgroundTasks
from services.pdf_service import extract_text_from_pdf
from services.ai_service import summarize_text
from services.history_service import save_history
from auth_utils import get_current_user_optional
# Removed unused import: notes_collection

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
        print(f"Error extracting PDF text: {e}") # Log for developer
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF (file might be empty or scanned images).")

    # 3. Generate Summary using AI
    try:
        summary = summarize_text(raw_text)
    except Exception as e:
        print(f"Error generating summary: {e}") # Log for developer
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")

    # 4. SAVE HISTORY (The Modern Way)
    user = await get_current_user_optional(request)
    
    if user:
        # Use background task for non-blocking save
        background_tasks.add_task(
            save_history,
            user_id=str(user["_id"]),
            action_type="pdf_summarize",
            input_data={"filename": file.filename}, # Good: specific filename instead of raw text
            result_data=summary
        )

    # 5. Return Response
    return {
        "summary": summary,
        "filename": file.filename
    }