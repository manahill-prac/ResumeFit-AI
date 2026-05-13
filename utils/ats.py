"""
ats.py
------
ATS (Applicant Tracking System) score estimation for ResumeFit AI.
Analyzes resume structure, keywords, and formatting quality.
"""

import re
from typing import Optional


# ─────────────────────────────────────────────
# ATS Factor Weights
# ─────────────────────────────────────────────

ATS_WEIGHTS = {
    "keyword_optimization": 0.30,  # 30%
    "formatting": 0.20,            # 20%
    "readability": 0.20,           # 20%
    "section_completeness": 0.20,  # 20%
    "contact_information": 0.10,   # 10%
}


# ─────────────────────────────────────────────
# Section Detectors
# ─────────────────────────────────────────────

SECTION_PATTERNS = {
    "experience": [
        "experience", "work experience", "employment", "work history",
        "professional experience", "career history"
    ],
    "education": [
        "education", "academic", "qualifications", "degrees", "studies"
    ],
    "skills": [
        "skills", "technical skills", "competencies", "technologies",
        "expertise", "core competencies"
    ],
    "summary": [
        "summary", "objective", "profile", "about me", "overview",
        "professional summary", "career objective"
    ],
    "projects": [
        "projects", "personal projects", "portfolio", "key projects"
    ],
    "certifications": [
        "certifications", "certificates", "courses", "training", "licenses"
    ],
    "contact": [
        "contact", "personal information", "personal details"
    ],
}


def _detect_sections(text: str) -> dict[str, bool]:
    """
    Detect which standard resume sections are present.
    Returns a dict of section_name -> bool.
    """
    text_lower = text.lower()
    detected = {}
    for section, keywords in SECTION_PATTERNS.items():
        detected[section] = any(kw in text_lower for kw in keywords)
    return detected


# ─────────────────────────────────────────────
# Component Scorers
# ─────────────────────────────────────────────

def _score_keyword_optimization(resume_text: str, jd_text: Optional[str] = None) -> tuple[float, list[str]]:
    """
    Score how well the resume incorporates relevant keywords.
    If JD is provided, checks JD keyword presence.
    Otherwise checks for generic resume action verbs.
    """
    suggestions = []

    action_verbs = [
        "developed", "implemented", "managed", "led", "built", "designed",
        "created", "improved", "optimized", "deployed", "architected",
        "delivered", "analyzed", "collaborated", "mentored", "increased",
        "reduced", "automated", "scaled", "launched",
    ]

    text_lower = resume_text.lower()
    verb_count = sum(1 for v in action_verbs if v in text_lower)
    verb_score = min(verb_count / 10, 1.0)  # Max at 10+ action verbs

    # Keyword density from JD
    jd_score = 0.5  # Default if no JD
    if jd_text and jd_text.strip():
        from utils.skills import extract_skills_from_job_description, find_matched_skills
        jd_skills = extract_skills_from_job_description(jd_text)
        from utils.skills import extract_skills_from_text
        resume_skills = extract_skills_from_text(resume_text)["all"]
        matched = find_matched_skills(resume_skills, jd_skills)
        jd_score = len(matched) / len(jd_skills) if jd_skills else 0.5

    if verb_count < 5:
        suggestions.append("Add more action verbs (developed, implemented, led, etc.) to describe your experience.")
    if jd_text and jd_score < 0.5:
        suggestions.append("Incorporate more keywords from the job description into your resume.")

    final_score = (verb_score * 0.4 + jd_score * 0.6)
    return final_score, suggestions


def _score_formatting(resume_text: str) -> tuple[float, list[str]]:
    """
    Score the formatting quality of the resume.
    Checks length, structure, and common formatting issues.
    """
    suggestions = []
    score = 1.0
    word_count = len(resume_text.split())

    # Length check: ideal 300–800 words
    if word_count < 150:
        score -= 0.3
        suggestions.append("Your resume appears too short. Add more detail to your experience and skills.")
    elif word_count > 1200:
        score -= 0.2
        suggestions.append("Your resume may be too long. ATS systems prefer concise 1–2 page resumes.")

    # Check for common bad patterns
    if resume_text.count("|") > 10:
        score -= 0.1
        suggestions.append("Avoid using pipe characters (|) as separators — they can confuse ATS parsers.")

    if len(re.findall(r"[•●▪▸■]", resume_text)) < 3:
        suggestions.append("Use bullet points to list your achievements and responsibilities for better readability.")

    # Check for dates (experience dating is important)
    date_pattern = r"\b(19|20)\d{2}\b"
    if not re.search(date_pattern, resume_text):
        score -= 0.15
        suggestions.append("Include dates for your work experiences and education.")

    return max(score, 0.0), suggestions


def _score_readability(resume_text: str) -> tuple[float, list[str]]:
    """
    Score readability based on sentence structure and clarity.
    """
    suggestions = []
    sentences = re.split(r"[.!?]\s+", resume_text)
    valid_sentences = [s for s in sentences if len(s.split()) > 3]

    if not valid_sentences:
        return 0.3, ["Resume content appears fragmented. Write in complete, clear sentences."]

    avg_words = sum(len(s.split()) for s in valid_sentences) / len(valid_sentences)

    score = 1.0
    if avg_words > 30:
        score -= 0.2
        suggestions.append("Some sentences are too long. Keep them concise for better readability.")
    elif avg_words < 5:
        score -= 0.15
        suggestions.append("Expand your descriptions — very short lines may not convey enough information.")

    # Check for numbers / quantified achievements
    has_numbers = bool(re.search(r"\b\d+[%+]?\b", resume_text))
    if not has_numbers:
        score -= 0.2
        suggestions.append("Quantify your achievements (e.g., 'Increased performance by 40%' or 'Managed a team of 5').")

    return max(score, 0.0), suggestions


def _score_section_completeness(resume_text: str) -> tuple[float, list[str]]:
    """
    Score based on how many standard resume sections are present.
    """
    detected = _detect_sections(resume_text)
    suggestions = []

    required = ["experience", "education", "skills", "summary"]
    optional = ["projects", "certifications"]

    present_required = sum(1 for s in required if detected.get(s))
    present_optional = sum(1 for s in optional if detected.get(s))

    for section in required:
        if not detected.get(section):
            suggestions.append(f"Add a '{section.capitalize()}' section — ATS systems specifically look for this.")

    score = (present_required / len(required)) * 0.8 + (present_optional / len(optional)) * 0.2
    return score, suggestions


def _score_contact_information(resume_text: str) -> tuple[float, list[str]]:
    """
    Score based on presence of essential contact information.
    """
    suggestions = []
    score = 0.0

    has_email = bool(re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", resume_text))
    has_phone = bool(re.search(r"(\+?\d[\d\s\-().]{7,}\d)", resume_text))
    has_linkedin = bool(re.search(r"linkedin\.com", resume_text, re.IGNORECASE))

    if has_email:
        score += 0.4
    else:
        suggestions.append("Include your email address in the resume.")

    if has_phone:
        score += 0.4
    else:
        suggestions.append("Include your phone number in the resume.")

    if has_linkedin:
        score += 0.2
    else:
        suggestions.append("Add your LinkedIn profile URL to increase credibility.")

    return score, suggestions


# ─────────────────────────────────────────────
# Master ATS Scorer
# ─────────────────────────────────────────────

def calculate_ats_score(resume_text: str, jd_text: Optional[str] = None) -> dict:
    """
    Calculate a comprehensive ATS score for the resume.
    
    Args:
        resume_text: Raw resume text
        jd_text: Optional job description for keyword matching
    
    Returns:
        dict with:
            - ats_score: int (0–100)
            - component_scores: individual factor scores
            - suggestions: list of improvement recommendations
            - section_status: which sections were detected
    """
    if not resume_text.strip():
        return {
            "ats_score": 0,
            "component_scores": {k: 0 for k in ATS_WEIGHTS},
            "suggestions": ["No resume content found."],
            "section_status": {},
        }

    kw_score, kw_suggestions = _score_keyword_optimization(resume_text, jd_text)
    fmt_score, fmt_suggestions = _score_formatting(resume_text)
    read_score, read_suggestions = _score_readability(resume_text)
    sec_score, sec_suggestions = _score_section_completeness(resume_text)
    contact_score, contact_suggestions = _score_contact_information(resume_text)

    # Weighted total
    overall = (
        kw_score * ATS_WEIGHTS["keyword_optimization"]
        + fmt_score * ATS_WEIGHTS["formatting"]
        + read_score * ATS_WEIGHTS["readability"]
        + sec_score * ATS_WEIGHTS["section_completeness"]
        + contact_score * ATS_WEIGHTS["contact_information"]
    )

    all_suggestions = kw_suggestions + fmt_suggestions + read_suggestions + sec_suggestions + contact_suggestions

    return {
        "ats_score": min(round(overall * 100), 100),
        "component_scores": {
            "keyword_optimization": round(kw_score * 100),
            "formatting": round(fmt_score * 100),
            "readability": round(read_score * 100),
            "section_completeness": round(sec_score * 100),
            "contact_information": round(contact_score * 100),
        },
        "suggestions": all_suggestions if all_suggestions else ["Your resume looks ATS-optimized!"],
        "section_status": _detect_sections(resume_text),
        "weights": ATS_WEIGHTS,
    }
