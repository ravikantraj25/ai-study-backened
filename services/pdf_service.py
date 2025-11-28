import fitz       # PyMuPDF
import pytesseract
from PIL import Image
import io
from fastapi import HTTPException


def extract_text_from_pdf(file_obj):
    try:
        # Read full file bytes
        file_bytes = file_obj.read()

        # Open PDF with PyMuPDF
        pdf = fitz.open(stream=file_bytes, filetype="pdf")
        full_text = ""

        for page in pdf:
            # Try normal text extraction
            text = page.get_text("text")

            if text.strip():
                full_text += text
            else:
                # Fallback to OCR for scanned/image pages
                pix = page.get_pixmap(dpi=200)
                img_bytes = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_bytes))
                ocr_text = pytesseract.image_to_string(img)
                full_text += ocr_text

        return full_text.strip()

    except Exception as e:
        print("PDF Extraction Error:", str(e))
        raise HTTPException(status_code=500, detail="Failed to extract text from PDF")
