import os
import requests
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY")
BASE_URL = "https://api.adzuna.com/v1/api/jobs"


def search_jobs(query: str, location: str = "us", num_results: int = 10) -> list:
    """Search for jobs using the Adzuna API."""
    url = f"{BASE_URL}/{location}/search/1"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_API_KEY,
        "what": query,
        "results_per_page": num_results,
        "content-type": "application/json"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return []
    
    jobs = []
    for result in data.get("results", []):
        job = {
            "id": result.get("id"),
            "title": result.get("title", "Unknown Title"),
            "company": result.get("company", {}).get("display_name", "Unknown Location"),
            "description": result.get("description", ""),
            "location": result.get("location", {}).get("display_name", "Unknown Location"),
            "salary_min": result.get("salary_min"),
            "salary_max": result.get("salary_max"),
            "url": result.get("redirect_url", ""),
            "created": result.get("created", "")
        }

        # Extract skills from the job description to use with our matcher
        job["required_skills"] = extract_skills_from_description(job["description"])
        jobs.append(job)

    return jobs


def extract_skills_from_description(description: str) -> list:
    """Pull skills from a job description using our skills database."""
    from app.resume_parser import SKILLS_DB
    import re

    desc_lower = description.lower()
    found_skills = []

    for skill in SKILLS_DB:
        if len(skill) <= 2:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, desc_lower):
                found_skills.append(skill)


        else:
            if skill in desc_lower:
                found_skills.append(skill)

    return found_skills


if __name__ == "__main__":
    print("Searching for Python developer jobs... \n")
    
    results = search_jobs("python developer")

    if not results:
        print("No results found. Check your API credentials")
    else:
        for job in results:
            print(f"{job['title']}")
            print(f" Company: {job['company']}")
            print(f" Location: {job['location']}")
            if job['salary_min'] and job['salary_max']:
                print(f" Salary: ${job['salary_min']:,.0f} - ${job['salary_max']:,.0f}")
            print(f" Skills: {', '.join(job['required_skills']) if job['required_skills'] else 'None detected'}")
            print(f" URL: {job['url']}")
            print()