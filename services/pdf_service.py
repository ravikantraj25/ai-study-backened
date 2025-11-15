import io
from PyPDF2 import PdfReader
from fastapi import HTTPException

def extract_text_from_pdf(file_obj):
    try:
        file_bytes = file_obj.read()
        pdf = PdfReader(io.BytesIO(file_bytes))

        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""

        return text

    except Exception as e:
        print("PDF ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Failed to read PDF")
