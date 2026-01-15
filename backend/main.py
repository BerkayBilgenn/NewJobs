"""
Reverse Job Search Dashboard - FastAPI Backend
Main API routes for CV upload and job search functionality.
"""

import os
import json
import re
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import PyPDF2
from io import BytesIO

from bot import LinkedInBot
from kariyer_bot import KariyerNetBot
from matcher import JobMatcher

# Initialize FastAPI app
app = FastAPI(
    title="Yeniİşim API",
    description="CV yükle, LinkedIn ve Kariyer.net'te iş ara, eşleşme skorlarını gör",
    version="1.0.0"
)

# CORS Configuration - Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
cv_data = {
    "text": "",
    "keywords": [],
    "job_title": "",
    "location": "Istanbul"
}

# File paths
JOBS_FILE = os.path.join(os.path.dirname(__file__), "jobs.json")
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")

# Ensure uploads directory exists
os.makedirs(UPLOADS_DIR, exist_ok=True)


class CVResponse(BaseModel):
    success: bool
    job_title: str  # Primary suggestion (first one)
    job_titles: list[str]  # All suggestions
    location: str
    keywords: list[str]
    message: str


class JobResponse(BaseModel):
    title: str
    company: str
    link: str
    image_url: Optional[str] = None
    match_score: float
    description: Optional[str] = None


class SearchResponse(BaseModel):
    success: bool
    jobs: list[JobResponse]
    message: str


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file content."""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")


def extract_keywords(text: str) -> list[str]:
    """
    Extract relevant keywords from CV text.
    Simple approach: Look for common tech skills, job titles, and tools.
    """
    # Common tech keywords to look for
    tech_keywords = [
        "python", "javascript", "react", "node", "java", "c++", "c#",
        "sql", "mongodb", "postgresql", "mysql", "redis",
        "aws", "azure", "gcp", "docker", "kubernetes",
        "machine learning", "data science", "deep learning", "ai",
        "frontend", "backend", "fullstack", "full-stack", "devops",
        "agile", "scrum", "git", "ci/cd", "rest api", "graphql",
        "typescript", "vue", "angular", "django", "flask", "fastapi",
        "html", "css", "tailwind", "bootstrap", "sass",
        "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn",
        "selenium", "playwright", "cypress", "testing",
        "project manager", "product manager", "data analyst", "data engineer",
        "software engineer", "developer", "architect", "designer"
    ]
    
    text_lower = text.lower()
    found_keywords = []
    
    for keyword in tech_keywords:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords[:15]  # Return top 15 keywords


def guess_job_titles(keywords: list[str], text: str) -> list[str]:
    """
    Guess multiple possible job titles from CV content.
    Returns a list of 3-5 matching job titles based on skills and experience.
    """
    text_lower = text.lower()
    keywords_lower = [k.lower() for k in keywords]
    keywords_text = " ".join(keywords_lower)
    
    # Score-based job title matching
    job_scores = {}
    
    # Define job titles and their matching criteria (keywords, patterns)
    job_criteria = {
        "Growth Engineer": {
            "keywords": ["growth", "seo", "meta ads", "google ads", "analytics", "a/b test", "cro"],
            "patterns": [r"growth\s+(engineer|hacking|marketing)", r"dijital\s+pazarlama"]
        },
        "Full Stack Developer": {
            "keywords": ["fullstack", "full-stack", "react", "python", "javascript", "flask", "django", "html", "css"],
            "patterns": [r"full[- ]?stack"]
        },
        "Backend Developer": {
            "keywords": ["python", "flask", "django", "fastapi", "sql", "postgresql", "api", "backend"],
            "patterns": [r"backend\s+developer"]
        },
        "Frontend Developer": {
            "keywords": ["react", "javascript", "html", "css", "vue", "angular", "frontend", "typescript"],
            "patterns": [r"frontend\s+developer"]
        },
        "Automation Engineer": {
            "keywords": ["selenium", "automation", "playwright", "testing", "bot", "scraping", "api"],
            "patterns": [r"otomasyon", r"automation"]
        },
        "Data Analyst": {
            "keywords": ["data", "analytics", "pandas", "excel", "sql", "visualization", "reporting", "veri"],
            "patterns": [r"data\s+analyst", r"veri\s+analiz"]
        },
        "Data Engineer": {
            "keywords": ["data", "pipeline", "etl", "sql", "python", "spark", "airflow"],
            "patterns": [r"data\s+engineer"]
        },
        "Python Developer": {
            "keywords": ["python", "django", "flask", "fastapi", "pandas"],
            "patterns": [r"python\s+developer"]
        },
        "Software Engineer": {
            "keywords": ["software", "engineer", "developer", "programming", "coding"],
            "patterns": [r"software\s+engineer", r"yazılım"]
        },
        "DevOps Engineer": {
            "keywords": ["docker", "kubernetes", "aws", "azure", "ci/cd", "devops", "jenkins"],
            "patterns": [r"devops"]
        },
        "Machine Learning Engineer": {
            "keywords": ["machine learning", "deep learning", "tensorflow", "pytorch", "ai", "ml"],
            "patterns": [r"machine\s+learning", r"yapay\s+zeka"]
        },
        "Product Manager": {
            "keywords": ["product", "roadmap", "agile", "scrum", "stakeholder"],
            "patterns": [r"product\s+manager", r"ürün\s+yönetici"]
        },
        "Digital Marketing Specialist": {
            "keywords": ["marketing", "seo", "sem", "google ads", "meta ads", "social media", "content"],
            "patterns": [r"dijital\s+pazarlama", r"digital\s+marketing"]
        },
        "E-commerce Specialist": {
            "keywords": ["e-commerce", "ticimax", "shopify", "woocommerce", "erp"],
            "patterns": [r"e-?ticaret", r"e-?commerce"]
        },
    }
    
    for job_title, criteria in job_criteria.items():
        score = 0
        
        # Check keywords
        for keyword in criteria["keywords"]:
            if keyword in keywords_text or keyword in text_lower:
                score += 10
        
        # Check patterns
        for pattern in criteria["patterns"]:
            if re.search(pattern, text_lower):
                score += 25
        
        if score > 0:
            job_scores[job_title] = score
    
    # Sort by score and get top matches
    sorted_jobs = sorted(job_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Return top 4 job titles, minimum 2
    top_jobs = [job for job, score in sorted_jobs[:4]]
    
    # If we got less than 2 results, add defaults
    if len(top_jobs) < 2:
        defaults = ["Software Developer", "Full Stack Developer"]
        for default in defaults:
            if default not in top_jobs:
                top_jobs.append(default)
            if len(top_jobs) >= 2:
                break
    
    return top_jobs


def guess_job_title(keywords: list[str], text: str) -> str:
    """Legacy function - returns first suggestion for backwards compatibility."""
    suggestions = guess_job_titles(keywords, text)
    return suggestions[0] if suggestions else "Software Developer"


def save_jobs_to_file(jobs: list[dict]):
    """Persist jobs to JSON file."""
    with open(JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)


def load_jobs_from_file() -> list[dict]:
    """Load jobs from JSON file if exists."""
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Reverse Job Search API is running"}


@app.post("/upload_cv", response_model=CVResponse)
async def upload_cv(file: UploadFile = File(...)):
    """
    Upload a CV (PDF) and extract keywords.
    Returns detected job title, location, and keywords.
    """
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    # Read and save file
    content = await file.read()
    file_path = os.path.join(UPLOADS_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Extract text from PDF
    text = extract_text_from_pdf(content)
    
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")
    
    # Extract keywords
    keywords = extract_keywords(text)
    
    # Guess multiple job titles
    job_titles = guess_job_titles(keywords, text)
    job_title = job_titles[0] if job_titles else "Software Developer"
    
    # Store in memory
    cv_data["text"] = text
    cv_data["keywords"] = keywords
    cv_data["job_title"] = job_title
    cv_data["job_titles"] = job_titles
    cv_data["location"] = "Istanbul"  # Default location
    
    return CVResponse(
        success=True,
        job_title=job_title,
        job_titles=job_titles,
        location=cv_data["location"],
        keywords=keywords,
        message=f"Successfully extracted {len(keywords)} keywords from your CV"
    )


@app.post("/search_jobs", response_model=SearchResponse)
async def search_jobs(job_title: Optional[str] = None, location: Optional[str] = None, platform: Optional[str] = "linkedin"):
    """
    Search for jobs on LinkedIn or Kariyer.net.
    
    Args:
        job_title: Job title to search for
        location: Location to search in
        platform: "linkedin" or "kariyer" (default: linkedin)
    
    Returns matched jobs with similarity scores.
    """
    # Use provided values or fall back to CV data
    search_title = job_title or cv_data.get("job_title", "Software Developer")
    search_location = location or cv_data.get("location", "Istanbul")
    
    if not cv_data.get("text"):
        raise HTTPException(
            status_code=400, 
            detail="Please upload a CV first before searching for jobs"
        )
    
    try:
        # Choose the right bot based on platform
        if platform == "kariyer":
            bot = KariyerNetBot()
            raw_jobs = bot.search_jobs(search_title, search_location, max_jobs=200)
        else:
            # Default to LinkedIn
            bot = LinkedInBot(headless=False)
            raw_jobs = bot.search_jobs(search_title, search_location, max_jobs=200)
        bot.close()
        
        if not raw_jobs:
            return SearchResponse(
                success=True,
                jobs=[],
                message="No jobs found. Try different keywords."
            )
        
        # Calculate match scores using keywords-based matching
        # (More accurate when we only have job titles, not full descriptions)
        matcher = JobMatcher()
        matched_jobs = []
        
        # Get CV keywords for matching
        cv_keywords = cv_data.get("keywords", [])
        cv_keywords_lower = [k.lower() for k in cv_keywords]
        
        for job in raw_jobs:
            job_title = job.get('title', '').lower()
            job_company = job.get('company', '').lower()
            job_desc = job.get('description', '').lower()
            job_text = f"{job_title} {job_company} {job_desc}"
            
            # Count how many CV keywords appear in the job text (title + description)
            keyword_matches = sum(1 for kw in cv_keywords_lower if kw in job_text)
            
            # Base score from keyword matches
            if cv_keywords:
                keyword_score = (keyword_matches / len(cv_keywords)) * 100
            else:
                keyword_score = 0
            
            # Bonus for exact role match in title
            search_role = search_title.lower()
            role_words = search_role.split()
            role_match_bonus = sum(15 for word in role_words if word in job_title and len(word) > 3)
            
            # Bonus if description exists and has keyword matches
            desc_bonus = 10 if job_desc and keyword_matches > 0 else 0
            
            # Combined score (capped at 100)
            score = min(100, keyword_score + role_match_bonus + desc_bonus)
            score = round(score, 1)
            
            matched_jobs.append(JobResponse(
                title=job.get("title", "Unknown"),
                company=job.get("company", "Unknown"),
                link=job.get("link", "#"),
                image_url=job.get("image_url"),
                match_score=score,
                description=job.get("description")
            ))
        
        # Sort by match score (highest first)
        matched_jobs.sort(key=lambda x: x.match_score, reverse=True)
        
        # Save to file for persistence
        save_jobs_to_file([j.dict() for j in matched_jobs])
        
        return SearchResponse(
            success=True,
            jobs=matched_jobs,
            message=f"Found {len(matched_jobs)} jobs matching your profile"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bot error: {str(e)}")


@app.get("/jobs", response_model=SearchResponse)
async def get_cached_jobs():
    """Get previously searched jobs from cache."""
    jobs = load_jobs_from_file()
    return SearchResponse(
        success=True,
        jobs=[JobResponse(**j) for j in jobs],
        message=f"Loaded {len(jobs)} cached jobs"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
