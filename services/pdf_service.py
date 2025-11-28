import fitz  # PyMuPDF
from fastapi import HTTPException

def extract_text_from_pdf(file_obj):
    try:
        file_bytes = file_obj.read()
        pdf = fitz.open(stream=file_bytes, filetype="pdf")
        full_text = ""

        for page in pdf:
            # Normal text extraction
            text = page.get_text("text")
            full_text += text

        return full_text.strip()

    except Exception as e:
        print("PDF Extraction Error:", str(e))
        raise HTTPException(status_code=500, detail="Failed to extract text from PDF")
