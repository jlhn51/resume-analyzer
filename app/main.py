import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from app.resume_parser import parse_resume

app = FastAPI(
    title="Resume Analyzer API",
    description="Upload a resume and get structured data with skill analysis",
    version="0.1.0"
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "running", "message": "Resume Analyzer API is live"}


@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    """Accept a PDF resume upload and return parsed data."""

    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted"
        )
    
    # Save the uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse the resume
    try:
        result = parse_resume(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing resume: {str(e)}"
        )
    finally:
        # Clean up the uploaded file
        os.remove(file_path)

    return {
        "filename": file.filename,
        "data": {
            "name": result["name"],
            "email": result["email"],
            "phone": result["phone"],
            "skills": result["skills"]
        }
    }