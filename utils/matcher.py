"""
matcher.py
----------
Job match scoring for ResumeFit AI.
Calculates weighted match percentage between resume and job description.
"""

import re
from typing import Optional

# TF-IDF based similarity (always available via scikit-learn)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from utils.skills import (
    extract_skills_from_text,
    extract_skills_from_job_description,
    find_matched_skills,
    find_missing_skills,
)


# ─────────────────────────────────────────────
# Scoring Weights
# ─────────────────────────────────────────────

WEIGHTS = {
    "skills": 0.40,       # 40% – skills match
    "experience": 0.25,   # 25% – experience match
    "education": 0.10,    # 10% – education keywords
    "keywords": 0.15,     # 15% – general keyword overlap
    "projects": 0.10,     # 10% – project/domain relevance
}


# ─────────────────────────────────────────────
# Component Scorers
# ─────────────────────────────────────────────

def _tfidf_similarity(text_a: str, text_b: str) -> float:
    """
    Calculate cosine similarity between two texts using TF-IDF.
    Returns a float between 0 and 1.
    """
    if not text_a.strip() or not text_b.strip():
        return 0.0
    try:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        vectors = vectorizer.fit_transform([text_a, text_b])
        score = cosine_similarity(vectors[0], vectors[1])[0][0]
        return float(score)
    except Exception:
        return 0.0


def _score_skills(resume_text: str, jd_text: str) -> tuple[float, list[str], list[str]]:
    """
    Score skill overlap between resume and job description.
    Returns: (score 0-1, matched_skills, missing_skills)
    """
    resume_skills = extract_skills_from_text(resume_text)["all"]
    jd_skills = extract_skills_from_job_description(jd_text)

    if not jd_skills:
        return 0.5, resume_skills, []  # No JD skills to compare

    matched = find_matched_skills(resume_skills, jd_skills)
    missing = find_missing_skills(resume_skills, jd_skills)

    score = len(matched) / len(jd_skills) if jd_skills else 0.0
    return min(score, 1.0), matched, missing


def _score_experience(resume_text: str, jd_text: str) -> float:
    """
    Compare experience-related content between resume and JD.
    Uses TF-IDF on experience section keywords.
    """
    exp_keywords = [
        "experience", "worked", "developed", "managed", "led", "built",
        "implemented", "designed", "architected", "delivered", "deployed",
        "maintained", "improved", "optimized", "years"
    ]

    resume_exp = " ".join(
        word for word in resume_text.lower().split()
        if any(kw in word for kw in exp_keywords)
    )
    jd_exp = " ".join(
        word for word in jd_text.lower().split()
        if any(kw in word for kw in exp_keywords)
    )

    # Also try TF-IDF on full texts for experience overlap
    full_sim = _tfidf_similarity(resume_text, jd_text)
    exp_sim = _tfidf_similarity(resume_exp, jd_exp) if resume_exp and jd_exp else 0.3

    return (full_sim * 0.4 + exp_sim * 0.6)


def _score_education(resume_text: str, jd_text: str) -> float:
    """
    Score match on education requirements.
    Looks for degree and field matches.
    """
    edu_keywords = [
        "bachelor", "master", "phd", "degree", "computer science",
        "engineering", "information technology", "mathematics",
        "statistics", "mba", "bsc", "msc", "diploma"
    ]

    resume_edu = " ".join(
        word for word in resume_text.lower().split()
        if any(kw in word for kw in edu_keywords)
    )
    jd_edu = " ".join(
        word for word in jd_text.lower().split()
        if any(kw in word for kw in edu_keywords)
    )

    if not jd_edu:
        return 0.7  # JD doesn't specify education, give benefit of the doubt

    return _tfidf_similarity(resume_edu or resume_text, jd_edu or jd_text)


def _score_keywords(resume_text: str, jd_text: str) -> float:
    """General keyword overlap using TF-IDF cosine similarity."""
    return _tfidf_similarity(resume_text, jd_text)


def _score_projects(resume_text: str, jd_text: str) -> float:
    """
    Score relevance of projects/portfolio to the JD domain.
    """
    project_indicators = [
        "project", "built", "developed", "created", "portfolio",
        "github", "deployed", "application", "system", "platform", "tool"
    ]

    resume_proj = " ".join(
        word for word in resume_text.lower().split()
        if any(ind in word for ind in project_indicators)
    )

    if not resume_proj:
        return 0.3

    return _tfidf_similarity(resume_proj, jd_text)


# ─────────────────────────────────────────────
# Main Matcher
# ─────────────────────────────────────────────

def calculate_match(resume_text: str, jd_text: str) -> dict:
    """
    Calculate the overall match between a resume and job description.
    
    Returns a dict containing:
        - overall_score: int (0–100)
        - component_scores: dict of each weight component (0–100)
        - matched_skills: list of skills found in both
        - missing_skills: list of JD skills not in resume
        - resume_skills: all skills from resume
        - jd_skills: all required skills from JD
        - match_label: qualitative label
    """
    if not resume_text.strip() or not jd_text.strip():
        return _empty_result()

    # Score each component
    skills_score, matched_skills, missing_skills = _score_skills(resume_text, jd_text)
    experience_score = _score_experience(resume_text, jd_text)
    education_score = _score_education(resume_text, jd_text)
    keywords_score = _score_keywords(resume_text, jd_text)
    projects_score = _score_projects(resume_text, jd_text)

    # Weighted total
    overall = (
        skills_score * WEIGHTS["skills"]
        + experience_score * WEIGHTS["experience"]
        + education_score * WEIGHTS["education"]
        + keywords_score * WEIGHTS["keywords"]
        + projects_score * WEIGHTS["projects"]
    )

    # Convert to 0–100 scale
    overall_pct = min(round(overall * 100), 100)

    # Pull all skills
    resume_skills = extract_skills_from_text(resume_text)["all"]
    jd_skills = extract_skills_from_job_description(jd_text)

    return {
        "overall_score": overall_pct,
        "component_scores": {
            "skills": round(skills_score * 100),
            "experience": round(experience_score * 100),
            "education": round(education_score * 100),
            "keywords": round(keywords_score * 100),
            "projects": round(projects_score * 100),
        },
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "match_label": _get_match_label(overall_pct),
        "weights": WEIGHTS,
    }


def _empty_result() -> dict:
    """Return a zeroed result when input is missing."""
    return {
        "overall_score": 0,
        "component_scores": {k: 0 for k in WEIGHTS},
        "matched_skills": [],
        "missing_skills": [],
        "resume_skills": [],
        "jd_skills": [],
        "match_label": "Insufficient data",
        "weights": WEIGHTS,
    }


def _get_match_label(score: int) -> str:
    """Return a qualitative match label."""
    if score >= 85:
        return "Excellent Match"
    elif score >= 70:
        return "Good Match"
    elif score >= 50:
        return "Moderate Match"
    elif score >= 30:
        return "Weak Match"
    else:
        return "Poor Match"
