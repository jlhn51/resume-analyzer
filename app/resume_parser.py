import spacy
from PyPDF2 import PdfReader
import re

# Load the spaCy English model
nlp = spacy.load("en_core_web_sm")

# Skills we'll look for in resumes (expand this later)
SKILLS_DB = [
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go",
    "sql", "html", "css", "react", "angular", "vue", "node.js", "django",
    "flask", "fastapi", "docker", "kubernetes", "aws", "azure", "gcp",
    "git", "linux", "mongodb", "postgresql", "mysql", "redis",
    "machine learning", "deep learning", "nlp", "data analysis",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy"
]

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract raw text from a PDF file."""
    reader =  PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()


def extract_name(doc) -> str:
    """Extract the person's name using spaCy's named entity recognition."""
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return "Name not found"


def extract_email(text: str) -> str:
    """Extract email address from resume text."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match =  re.search(email_pattern, text)
    return match.group() if match else "Email not found"


def extract_phone(text: str) -> str:
    """Extract phone number from resume text."""
    phone_pattern = r'(\+?1?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})'
    match = re.search(phone_pattern, text)
    return match.group().strip() if match else "Phone not found"


def extract_skills(text: str) -> list:
    """Match skills from our database against the resume text."""
    text_lower = text.lower()
    found_skills = []
    for skill in SKILLS_DB:
        if len(skill) <= 2:
            # For short skills like "c" or "go", match whole words only
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        else:
            if skill in text_lower:
                found_skills.append(skill)
    return found_skills


def parse_resume(pdf_path: str) -> dict:
    """Main functtion: takes a PDF path and return structured resume data."""
    raw_text =  extract_text_from_pdf(pdf_path)
    doc = nlp(raw_text)

    resume_data = {
        "name": extract_name(doc),
        "email": extract_email(raw_text),
        "phone": extract_phone(raw_text),
        "skills": extract_skills(raw_text),
        "raw_text": raw_text
    }

    return resume_data


# This lets us test the parser directly from the command line
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python resume_parser.py <path_to_resume.pdf")
        sys.exit(1)

    result = parse_resume(sys.argv[1])

    print(f"\nName: {result['name']}")
    print(f"Email: {result['email']}")
    print(f"Phone: {result['phone']}")
    print(f"Skills found: {result['skills']}")
    print(f"\nRaw text preview: {result['raw_text'][:500]}...")