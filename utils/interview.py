"""
interview.py
------------
Interview question generation for ResumeFit AI.
Uses OpenAI API to generate targeted interview questions.
"""

import os
from typing import Optional
from openai import OpenAI


# ─────────────────────────────────────────────
# OpenAI Client
# ─────────────────────────────────────────────

def _get_openai_client() -> Optional[OpenAI]:
    """Initialize OpenAI client from environment variable."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


# ─────────────────────────────────────────────
# Prompt Builders
# ─────────────────────────────────────────────

def _build_technical_prompt(resume_text: str, missing_skills: list[str], jd_text: str) -> str:
    """Build prompt for technical interview questions."""
    missing_str = ", ".join(missing_skills[:8]) if missing_skills else "None"
    jd_snippet = jd_text[:600] if jd_text else "Not provided"

    return f"""You are a senior technical interviewer. Based on the resume and job description below, generate exactly 5 targeted technical interview questions.

RESUME (excerpt):
{resume_text[:800]}

JOB DESCRIPTION (excerpt):
{jd_snippet}

SKILL GAPS TO ADDRESS: {missing_str}

Generate 5 technical questions that:
1. Test the candidate's depth in their claimed skills
2. Probe on skill gaps identified
3. Are relevant to the specific role

Format: Return ONLY a numbered list (1. 2. 3. 4. 5.) with no extra explanation."""


def _build_behavioral_prompt(resume_text: str) -> str:
    """Build prompt for behavioral interview questions."""
    return f"""You are an experienced HR interviewer. Based on this resume, generate exactly 5 behavioral interview questions using the STAR method framework.

RESUME (excerpt):
{resume_text[:600]}

Generate 5 behavioral questions that:
1. Probe real experiences from the candidate's history
2. Explore leadership, teamwork, and problem-solving
3. Are role-appropriate and professional

Format: Return ONLY a numbered list (1. 2. 3. 4. 5.) with no extra explanation."""


def _build_role_specific_prompt(resume_text: str, jd_text: str, missing_skills: list[str]) -> str:
    """Build prompt for role-specific interview questions."""
    missing_str = ", ".join(missing_skills[:5]) if missing_skills else "None"
    jd_snippet = jd_text[:500] if jd_text else "Not provided"

    return f"""You are a hiring manager. Based on the job description and candidate's profile, generate exactly 5 role-specific interview questions.

JOB DESCRIPTION:
{jd_snippet}

CANDIDATE PROFILE (excerpt):
{resume_text[:500]}

MISSING SKILLS: {missing_str}

Generate 5 questions that:
1. Assess fit for this specific role and company context
2. Test knowledge of tools/frameworks in the JD
3. Evaluate how the candidate handles their skill gaps

Format: Return ONLY a numbered list (1. 2. 3. 4. 5.) with no extra explanation."""


# ─────────────────────────────────────────────
# Question Parsers
# ─────────────────────────────────────────────

def _parse_numbered_list(text: str) -> list[str]:
    """Parse a numbered list response into a Python list."""
    lines = text.strip().splitlines()
    questions = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Strip leading numbers, dots, parentheses
        cleaned = line.lstrip("0123456789.)- ").strip()
        if len(cleaned) > 10:  # Filter out very short non-question lines
            questions.append(cleaned)
    return questions[:5]  # Enforce max 5


# ─────────────────────────────────────────────
# Fallback Questions
# ─────────────────────────────────────────────

FALLBACK_TECHNICAL = [
    "Can you walk me through a complex technical problem you solved recently?",
    "How do you approach debugging a production issue under time pressure?",
    "Describe your experience with version control and collaborative development.",
    "What is your process for code review and maintaining code quality?",
    "How do you stay updated with the latest technologies in your field?",
]

FALLBACK_BEHAVIORAL = [
    "Tell me about a time you had to meet a tight deadline. How did you handle it?",
    "Describe a situation where you had a conflict with a teammate and how you resolved it.",
    "Give an example of a project where you took the initiative to improve something.",
    "Tell me about a time you failed and what you learned from it.",
    "Describe how you prioritize tasks when working on multiple projects simultaneously.",
]

FALLBACK_ROLE_SPECIFIC = [
    "Why are you interested in this specific role and company?",
    "How do your skills align with the requirements listed in the job description?",
    "Where do you see yourself growing professionally in the next 2–3 years?",
    "What value do you believe you can bring to this team from day one?",
    "How do you approach learning a new technology or tool required for a role?",
]


# ─────────────────────────────────────────────
# Main Generator
# ─────────────────────────────────────────────

def generate_interview_questions(
    resume_text: str,
    jd_text: str = "",
    missing_skills: Optional[list[str]] = None,
) -> dict:
    """
    Generate three sets of interview questions: technical, behavioral, role-specific.
    
    Uses OpenAI API if key is available; falls back to curated defaults.
    
    Returns:
        dict with keys: technical, behavioral, role_specific, ai_powered (bool)
    """
    missing_skills = missing_skills or []
    client = _get_openai_client()

    if not client:
        # No API key — return curated fallback questions
        return {
            "technical": FALLBACK_TECHNICAL,
            "behavioral": FALLBACK_BEHAVIORAL,
            "role_specific": FALLBACK_ROLE_SPECIFIC,
            "ai_powered": False,
        }

    technical = _ai_generate(
        client,
        _build_technical_prompt(resume_text, missing_skills, jd_text),
        FALLBACK_TECHNICAL,
    )
    behavioral = _ai_generate(
        client,
        _build_behavioral_prompt(resume_text),
        FALLBACK_BEHAVIORAL,
    )
    role_specific = _ai_generate(
        client,
        _build_role_specific_prompt(resume_text, jd_text, missing_skills),
        FALLBACK_ROLE_SPECIFIC,
    )

    return {
        "technical": technical,
        "behavioral": behavioral,
        "role_specific": role_specific,
        "ai_powered": True,
    }


def _ai_generate(client: OpenAI, prompt: str, fallback: list[str]) -> list[str]:
    """Call OpenAI and parse the response. Returns fallback on any error."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.7,
        )
        content = response.choices[0].message.content or ""
        parsed = _parse_numbered_list(content)
        return parsed if len(parsed) >= 3 else fallback
    except Exception:
        return fallback
