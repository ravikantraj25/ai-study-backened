import fitz  # PyMuPDF
from fastapi import HTTPException

def extract_text_from_pdf(file_obj):
    try:
        # 1. Read file bytes
        file_bytes = file_obj.read()
        
        # 2. Open PDF from memory
        with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
            
            # 3. Handle Password Protection (Try empty password)
            if pdf.is_encrypted:
                pdf.authenticate("") 
            
            full_text = []

            # 4. Iterate through pages
            for page in pdf:
                # 'sort=True' helps read text in natural reading order (columns/layouts)
                text = page.get_text("text", sort=True)
                
                if text.strip():
                    full_text.append(text)

        # 5. Join pages with separation
        final_output = "\n\n".join(full_text)

        # 6. Check for "Scanned PDF" (Image-based)
        if not final_output.strip():
            raise HTTPException(
                status_code=400, 
                detail="No text found. This PDF might be scanned/image-based. Please upload a selectable text PDF."
            )

        return final_output.strip()

    except HTTPException as he:
        # Re-raise HTTP exceptions (like the scanned PDF warning above)
        raise he
    except Exception as e:
        print(f"❌ PDF Extraction Error: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to read PDF file. It may be corrupted.")