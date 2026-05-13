"""
skills.py
---------
Skill extraction and matching for ResumeFit AI.
Uses keyword matching against a curated technical skills database.
"""

import re
from typing import Optional

# ─────────────────────────────────────────────
# Skills Database
# ─────────────────────────────────────────────

# Technical skills organized by category
TECHNICAL_SKILLS_DB = {
    "Programming Languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c",
        "ruby", "go", "golang", "rust", "swift", "kotlin", "scala",
        "php", "r", "matlab", "perl", "bash", "shell scripting",
        "powershell", "dart", "lua", "groovy", "elixir", "haskell",
    ],
    "Web Frameworks": [
        "react", "reactjs", "react.js", "angular", "angularjs", "vue",
        "vuejs", "vue.js", "next.js", "nextjs", "nuxt.js", "svelte",
        "django", "flask", "fastapi", "express", "expressjs", "node.js",
        "nodejs", "spring", "spring boot", "laravel", "rails",
        "ruby on rails", "asp.net", ".net", "dotnet", "gatsby",
    ],
    "Databases": [
        "sql", "mysql", "postgresql", "postgres", "mongodb", "redis",
        "elasticsearch", "oracle", "sql server", "mssql", "sqlite",
        "cassandra", "dynamodb", "firebase", "neo4j", "couchdb",
        "mariadb", "influxdb", "snowflake", "bigquery",
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "google cloud", "gcp",
        "docker", "kubernetes", "k8s", "terraform", "ansible", "puppet",
        "chef", "jenkins", "gitlab ci", "github actions", "circleci",
        "travis ci", "heroku", "vercel", "netlify", "cloudflare",
        "linux", "unix", "nginx", "apache", "vagrant",
    ],
    "Data & AI": [
        "machine learning", "deep learning", "neural networks",
        "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
        "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
        "nlp", "natural language processing", "computer vision",
        "data science", "data analysis", "big data", "hadoop", "spark",
        "apache spark", "tableau", "power bi", "excel", "statistics",
        "regression", "classification", "clustering", "opencv",
        "hugging face", "transformers", "bert", "gpt",
    ],
    "Mobile": [
        "android", "ios", "react native", "flutter", "xamarin",
        "ionic", "swift", "swiftui", "kotlin", "java android",
        "mobile development",
    ],
    "Tools & Practices": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence",
        "agile", "scrum", "kanban", "ci/cd", "rest api", "graphql",
        "microservices", "api design", "unit testing", "tdd",
        "bdd", "pytest", "junit", "selenium", "postman",
        "figma", "sketch", "adobe xd", "linux administration",
        "networking", "cybersecurity", "devops", "sre",
    ],
    "Soft Skills": [
        "communication", "leadership", "teamwork", "problem solving",
        "critical thinking", "time management", "project management",
        "collaboration", "adaptability", "creativity", "presentation",
        "mentoring", "coaching", "negotiation", "analytical",
    ],
}

# Flat list of all technical skills (excluding soft skills) for quick lookup
ALL_TECHNICAL_SKILLS = [
    skill
    for category, skills in TECHNICAL_SKILLS_DB.items()
    if category != "Soft Skills"
    for skill in skills
]

ALL_SOFT_SKILLS = TECHNICAL_SKILLS_DB["Soft Skills"]


# ─────────────────────────────────────────────
# Skill Extraction
# ─────────────────────────────────────────────

def normalize_text(text: str) -> str:
    """Lowercase and clean up text for matching."""
    return text.lower().strip()


def extract_skills_from_text(text: str) -> dict:
    """
    Extract technical and soft skills from resume text using keyword matching.
    
    Returns:
        dict with keys:
            - 'technical': list of matched technical skills
            - 'soft': list of matched soft skills
            - 'all': combined list
            - 'by_category': dict of skills grouped by category
    """
    normalized = normalize_text(text)
    
    technical_found = set()
    soft_found = set()
    by_category: dict[str, list[str]] = {}

    for category, skills in TECHNICAL_SKILLS_DB.items():
        matched = []
        for skill in skills:
            # Use word-boundary matching to avoid partial matches
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, normalized):
                matched.append(skill)
                if category == "Soft Skills":
                    soft_found.add(skill)
                else:
                    technical_found.add(skill)
        if matched:
            by_category[category] = matched

    # Deduplicate (e.g. "react" and "reactjs" both match)
    technical_list = sorted(list(technical_found))
    soft_list = sorted(list(soft_found))

    return {
        "technical": technical_list,
        "soft": soft_list,
        "all": technical_list + soft_list,
        "by_category": by_category,
    }


def extract_skills_from_job_description(jd_text: str) -> list[str]:
    """
    Extract required skills from a job description.
    Uses the same database but returns a flat list.
    """
    result = extract_skills_from_text(jd_text)
    return result["all"]


def find_missing_skills(resume_skills: list[str], jd_skills: list[str]) -> list[str]:
    """
    Identify skills required by the job but absent from the resume.
    
    Args:
        resume_skills: Skills extracted from the resume
        jd_skills: Skills extracted from the job description
    Returns:
        List of skills in jd_skills not found in resume_skills
    """
    resume_set = {s.lower() for s in resume_skills}
    return [skill for skill in jd_skills if skill.lower() not in resume_set]


def find_matched_skills(resume_skills: list[str], jd_skills: list[str]) -> list[str]:
    """
    Find skills that appear in both the resume and job description.
    """
    resume_set = {s.lower() for s in resume_skills}
    return [skill for skill in jd_skills if skill.lower() in resume_set]


def categorize_skill(skill: str) -> str:
    """Return the category for a given skill, or 'Other' if not found."""
    skill_lower = skill.lower()
    for category, skills in TECHNICAL_SKILLS_DB.items():
        if skill_lower in [s.lower() for s in skills]:
            return category
    return "Other"


def get_skill_importance(skill: str, jd_text: str) -> str:
    """
    Estimate skill importance by frequency in the job description.
    Returns: 'critical', 'important', or 'nice-to-have'
    """
    count = len(re.findall(r"\b" + re.escape(skill.lower()) + r"\b", jd_text.lower()))
    if count >= 3:
        return "critical"
    elif count >= 2:
        return "important"
    else:
        return "nice-to-have"
