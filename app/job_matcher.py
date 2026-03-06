from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Sample job listings (we'll replace this with real data later)
SAMPLE_JOBS = [
    {
        "id": 1,
        "title": "Backend Developer",
        "company": "TechCorp",
        "required_skills": ["python", "django", "postgresql", "docker", "git", "aws"],
        "description": "Build and maintain scalable backend services using Python and Django."
    },
    {
        "id": 2,
        "title": "Frontend Developer",
        "company": "WebStudio",
        "required_skills": ["javascript", "react", "html", "css", "typescript", "git"],
        "description": "Create responsive user interfaces with React and modern CSS."
    },
    {
        "id": 3,
        "title": "Data Scientist",
        "company": "DataFlow",
        "required_skills": ["python", "machine learning", "pandas", "numpy", "scikit-learn", "sql"],
        "description": "Analyze large datasets and build predictive models using Python."
    },
    {
        "id": 4,
        "title": "Full Stack Developer",
        "company": "StartupXYZ",
        "required_skills": ["python", "javascript", "react", "node.js", "mongodb", "docker", "git"],
        "description": "Work across the entire stack building features from database to UI."
    },
    {
        "id": 5,
        "title": "ML Engineer",
        "company": "AI Solutions",
        "required_skills": ["python", "tensorflow", "pytorch", "deep learning", "docker", "aws", "git"],
        "description": "Deploy and optimize machine learning models in production environments."
    }
]


def skill_match_score(resume_skills: list, job_skills: list) -> dict:
    """Calculate how well resume skills match a job's required skills."""
    resume_set = set(s.lower() for s in resume_skills)
    job_set = set(s.lower() for s in job_skills)

    matching = resume_set.intersection(job_set)
    missing = job_set - resume_set
    extra = resume_set - job_set

    score = len(matching) / len(job_set) * 100 if job_set else 0

    return {
        "score": round(score, 1),
        "matching_skills": sorted(list(matching)),
        "missing_skills": sorted(list(missing)),
        "extra_skills": sorted(list(extra))
    }


def text_similarity_score(resume_text: str, job_description: str) -> float:
    """Use TF-IDF and cosine similarity to compare resume text to job description."""
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return round(float(similarity[0][0]) * 100, 1)


def match_resume_to_jobs(resume_skills: list, resume_text: str, jobs: list = None) -> list:
    """Match a resume against all jobs and return ranked results."""
    if jobs is None:
        jobs = SAMPLE_JOBS

    results = []

    for job in jobs:
        skill_result = skill_match_score(resume_skills, job["required_skills"])
        text_score = text_similarity_score(resume_text, job.get("description", ""))

        # Combined score: 70% skill match, 30% text similarity
        combined_score = round(skill_result["score"] * 0.7 + text_score * 0.3, 1)

        result = {
            "job_id": job.get("id"),
            "title": job.get("title", "Unknown Title"),
            "company": job.get("company", "Unknown Company"),
            "combined_score": combined_score,
            "skill_score": skill_result["score"],
            "text_score": text_score,
            "matching_skills": skill_result["matching_skills"],
            "missing_skills": skill_result["missing_skills"]
        }

        # Include extra fields from real job data if available
        if "location" in job:
            result["location"] = job["location"]
        if "salary_min" in job:
            result["salary_min"] = job["salary_min"]
        if "salary_max" in job:
            result["salary_max"] = job["salary_max"]
        if "url" in job:
            result["url"] = job["url"]

        results.append(result)

    # Sort by combined score, highest first
    results.sort(key=lambda x: x["combined_score"], reverse=True)
    return results


if __name__ == "__main__":
    # Test with sample resume data
    test_skills = ["python", "javascript", "react", "sql", "git", "pandas", "numpy"]
    test_text = "Experienced developer with Python and JavaScript skills. Built web applications using React and worked with SQL databases. Familiar with data analysis using pandas."

    print("Job Matching Results:")
    print("=" * 60)

    matches = match_resume_to_jobs(test_skills, test_text)
    for match in matches:
        print(f"\n{match['title']} at {match['company']}")
        print(f"  Combined Score: {match['combined_score']}%")
        print(f"  Skill Match: {match['skill_score']}%")
        print(f"  Text Match: {match['text_score']}%")
        print(f"  Matching: {', '.join(match['matching_skills'])}")
        print(f"  Missing: {', '.join(match['missing_skills'])}")
