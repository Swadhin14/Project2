from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid
from app.services.pdf_parser import extract_text_from_pdf
from app.services.chunks import chunk_resume_text
from app.services.vector_store import index_chunks

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    contents = await file.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    # 🔹 Parse PDF text
    extracted_text = extract_text_from_pdf(file_path)
    
    print("EXTRACTED TEXT PREVIEW:")
    print(extracted_text[:300])
    
   
    chunks = chunk_resume_text(extracted_text, unique_filename)
    print("TOTAL CHUNKS:", len(chunks))
    print("FIRST CHUNK:", chunks[0] if chunks else "No chunks")
    
    # Index chunks in vector store
    index_chunks(unique_filename, chunks)
    
    return {
        "success": True,
        "filename": unique_filename,
        "message": "Resume uploaded successfully",
        "text_preview": extracted_text[:500],
        "text_length": len(extracted_text),
        "chunks_created":len(chunks),
        "first_chunk": chunks[0] if chunks else None
    }