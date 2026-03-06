import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.resume_parser import parse_resume
from app.job_matcher import match_resume_to_jobs
from app.job_search import search_jobs

app = FastAPI(
    title="Resume Analyzer API",
    description="Upload a resume and get structured data with skill analysis",
    version="0.1.0"
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def root():
    """Serve the frontend."""
    return FileResponse("static/index.html")


@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    """Accept a PDF resume upload and return parsed data with real job matches."""

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

    # Search for real jobs based on the candidate's top skills
    search_query = " ".join(result["skills"][:3])
    real_jobs = search_jobs(search_query)

    # Match resume against real jobs
    job_matches = match_resume_to_jobs(result["skills"], result["raw_text"], real_jobs)

    return {
        "filename": file.filename,
        "data": {
            "name": result["name"],
            "email": result["email"],
            "phone": result["phone"],
            "skills": result["skills"]
        },
        "job_matches": job_matches
    }