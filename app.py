"""
app.py
------
ResumeFit AI — Main Streamlit Application Entry Point.

A professional AI-powered resume analysis and job match platform.
Supports English and Urdu with full ATS scoring, skill gap analysis,
interview prep, and AI feedback.
"""

import os
import io
import streamlit as st
from pathlib import Path

# ─────────────────────────────────────────────
# Page Config (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeFit AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Internal Modules
# ─────────────────────────────────────────────
from utils.parser import parse_resume
from utils.skills import extract_skills_from_text
from utils.matcher import calculate_match
from utils.ats import calculate_ats_score
from utils.interview import generate_interview_questions
from ui.bilingual import get_text, get_score_label
from ui.upload import render_upload_section
from ui.dashboard import (
    render_metric_cards,
    render_match_gauge,
    render_ats_breakdown,
    render_component_radar,
    render_skills_section,
    render_interview_questions,
    render_ai_feedback,
    render_ats_suggestions,
    render_candidate_info,
)


# ─────────────────────────────────────────────
# CSS Injection
# ─────────────────────────────────────────────

def inject_css() -> None:
    """Load and inject the custom CSS stylesheet."""
    css_path = Path(__file__).parent / "assets" / "styles" / "styles.css"
    if css_path.exists():
        with open(css_path, "r") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        # Inline fallback minimal CSS
        st.markdown("""
        <style>
        :root {
          --primary: #1E2A38; --secondary: #5B6C8F; --accent: #3FA796;
          --bg: #F7F9FC; --card: #FFFFFF; --text-primary: #222831;
          --text-secondary: #6B7280; --success: #6BBF59; --warning: #E6A23C;
          --border: #E5E7EB; --radius: 12px; --radius-sm: 8px;
          --shadow: 0 1px 3px rgba(0,0,0,0.08);
        }
        </style>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# AI Feedback (OpenAI)
# ─────────────────────────────────────────────

def generate_ai_feedback(
    resume_text: str,
    match_result: dict,
    ats_result: dict,
    jd_text: str,
) -> dict:
    """
    Generate structured AI feedback using OpenAI.
    Falls back to rule-based feedback if API key is missing.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "")
    
    # ── Rule-based fallback ───────────────────
    if not api_key:
        return _rule_based_feedback(match_result, ats_result)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        match_score = match_result.get("overall_score", 0)
        ats_score = ats_result.get("ats_score", 0)
        matched = ", ".join(match_result.get("matched_skills", [])[:8])
        missing = ", ".join(match_result.get("missing_skills", [])[:8])
        jd_snippet = jd_text[:500] if jd_text else "Not provided"

        prompt = f"""You are an expert career coach and resume reviewer.

Analyze this resume and provide structured feedback in JSON format.

RESUME (excerpt):
{resume_text[:1000]}

JOB DESCRIPTION (excerpt):
{jd_snippet}

ANALYSIS DATA:
- Job Match Score: {match_score}%
- ATS Score: {ats_score}%
- Matched Skills: {matched}
- Missing Skills: {missing}

Return ONLY valid JSON (no markdown, no backticks) with this exact structure:
{{
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
  "suggestions": ["suggestion 1", "suggestion 2", "suggestion 3", "suggestion 4"]
}}

Keep each item concise (1–2 sentences max)."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.5,
        )

        content = response.choices[0].message.content or ""
        # Clean potential markdown code block
        content = content.strip().lstrip("```json").lstrip("```").rstrip("```").strip()

        import json
        parsed = json.loads(content)
        parsed["ai_powered"] = True
        return parsed

    except Exception:
        result = _rule_based_feedback(match_result, ats_result)
        result["ai_powered"] = False
        return result


def _rule_based_feedback(match_result: dict, ats_result: dict) -> dict:
    """Generate basic feedback from scoring data without OpenAI."""
    match_score = match_result.get("overall_score", 0)
    ats_score = ats_result.get("ats_score", 0)
    matched = match_result.get("matched_skills", [])
    missing = match_result.get("missing_skills", [])

    strengths = []
    weaknesses = []
    suggestions = []

    if matched:
        strengths.append(f"Strong skill alignment: {', '.join(matched[:4])}.")
    if match_score >= 70:
        strengths.append("Good overall match with the job description.")
    if ats_score >= 70:
        strengths.append("Resume is well-structured and ATS-friendly.")
    if not strengths:
        strengths.append("Resume has some relevant experience and skills.")

    if missing:
        weaknesses.append(f"Missing key skills: {', '.join(missing[:4])}.")
    if ats_score < 60:
        weaknesses.append("ATS score needs improvement — focus on keywords and formatting.")
    if match_score < 50:
        weaknesses.append("Overall job match is low — tailor your resume to the job description.")
    if not weaknesses:
        weaknesses.append("Minor gaps exist but overall the resume is competitive.")

    suggestions.extend(ats_result.get("suggestions", [])[:3])
    if missing:
        suggestions.append(f"Upskill in: {', '.join(missing[:3])} through certifications or projects.")
    if not suggestions:
        suggestions.append("Continue refining your resume with quantified achievements.")

    return {
        "strengths": strengths[:3],
        "weaknesses": weaknesses[:3],
        "suggestions": suggestions[:4],
        "ai_powered": False,
    }


# ─────────────────────────────────────────────
# Voice Feedback
# ─────────────────────────────────────────────

def generate_voice_feedback(feedback: dict, match_score: int, ats_score: int) -> bytes | None:
    """
    Generate a voice summary using gTTS.
    Returns MP3 bytes or None if gTTS is unavailable.
    """
    try:
        from gtts import gTTS

        strengths = feedback.get("strengths", [])
        suggestions = feedback.get("suggestions", [])

        summary_lines = [
            f"Here is your ResumeFit AI analysis summary.",
            f"Your job match score is {match_score} percent, and your ATS score is {ats_score} percent.",
        ]
        if strengths:
            summary_lines.append(f"Key strengths: {strengths[0]}")
        if suggestions:
            summary_lines.append(f"Top recommendation: {suggestions[0]}")
        summary_lines.append("Review the dashboard for the full analysis and good luck with your application!")

        summary_text = " ".join(summary_lines)
        audio = gTTS(text=summary_text, lang="en", slow=False)
        buf = io.BytesIO()
        audio.write_to_fp(buf)
        return buf.getvalue()

    except Exception:
        return None


# ─────────────────────────────────────────────
# Session State
# ─────────────────────────────────────────────

def init_session_state() -> None:
    """Initialize all session state variables."""
    defaults = {
        "lang": "en",
        "analysis_done": False,
        "parsed_resume": None,
        "match_result": None,
        "ats_result": None,
        "ai_feedback": None,
        "interview_questions": None,
        "voice_audio": None,
        "active_page": "upload",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────

def render_sidebar() -> str:
    """Render sidebar navigation. Returns the selected page."""
    lang = st.session_state.lang
    t = lambda k: get_text(k, lang)

    with st.sidebar:
        # Logo / Brand
        st.markdown(f"""
        <div style="padding: 8px 0 24px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 24px;">
            <div style="font-size: 1.5rem; font-weight: 700; color: white; letter-spacing: -0.02em;">
                📄 ResumeFit
            </div>
            <div style="font-size: 0.75rem; color: rgba(255,255,255,0.4); margin-top: 2px;">AI Resume Analyzer</div>
        </div>
        """, unsafe_allow_html=True)

        # Language toggle
        lang_label = t("language_toggle")
        if st.button(f"🌐 {lang_label}", use_container_width=True):
            st.session_state.lang = "ur" if lang == "en" else "en"
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:rgba(255,255,255,0.35); margin-bottom:8px;'>{t('sidebar_title')}</div>", unsafe_allow_html=True)

        # Navigation options
        pages = {
            "upload": f"📤 {t('nav_upload')}",
            "dashboard": f"📊 {t('nav_dashboard')}",
            "skills": f"💡 {t('nav_skills')}",
            "interview": f"🎤 {t('nav_interview')}",
            "feedback": f"🤖 {t('nav_feedback')}",
        }

        for page_key, page_label in pages.items():
            is_active = st.session_state.active_page == page_key
            style = "background: rgba(63,167,150,0.2); border-radius: 8px;" if is_active else ""
            if st.button(page_label, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.active_page = page_key
                st.rerun()

        # API Key input
        st.markdown("<br><hr style='border-color:rgba(255,255,255,0.1);'><br>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:rgba(255,255,255,0.35); margin-bottom:8px;'>API Settings</div>", unsafe_allow_html=True)

        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Optional: Enables AI-powered feedback and interview questions.",
            label_visibility="collapsed",
        )
        if api_key_input:
            os.environ["OPENAI_API_KEY"] = api_key_input
            st.success("✓ API key set", icon="🔑")

        st.markdown("""
        <div style='margin-top: 16px; font-size: 0.72rem; color: rgba(255,255,255,0.3); line-height: 1.6;'>
        Without an API key, the app uses intelligent rule-based analysis.
        </div>
        """, unsafe_allow_html=True)

    return st.session_state.active_page


# ─────────────────────────────────────────────
# Page: Upload + Analysis
# ─────────────────────────────────────────────

def page_upload() -> None:
    """Render the resume upload and analysis trigger page."""
    lang = st.session_state.lang
    t = lambda k: get_text(k, lang)

    file_bytes, file_type, job_description = render_upload_section(lang)

    st.markdown("<br>", unsafe_allow_html=True)

    # Analyze button
    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        analyze_clicked = st.button(
            f"🔍 {t('upload_analyze')}",
            type="primary",
            use_container_width=True,
            disabled=(file_bytes is None),
        )

    with col_info:
        if file_bytes is None:
            st.markdown(f"""
            <div style="padding: 10px 0; color: var(--text-secondary, #6B7280); font-size: 0.87rem;">
                ↑ Upload your resume to begin analysis
            </div>
            """, unsafe_allow_html=True)

    if analyze_clicked and file_bytes:
        with st.spinner(t("loading")):
            # 1. Parse resume
            parsed = parse_resume(file_bytes, file_type)
            resume_text = parsed.get("raw_text", "")

            if not resume_text.strip():
                st.error(t("error"))
                return

            # 2. Calculate match
            match_result = calculate_match(resume_text, job_description)

            # 3. ATS scoring
            ats_result = calculate_ats_score(resume_text, job_description)

            # 4. AI Feedback
            ai_feedback = generate_ai_feedback(
                resume_text, match_result, ats_result, job_description
            )

            # 5. Interview questions
            interview_qs = generate_interview_questions(
                resume_text,
                job_description,
                match_result.get("missing_skills", []),
            )

            # Store results in session state
            st.session_state.parsed_resume = parsed
            st.session_state.match_result = match_result
            st.session_state.ats_result = ats_result
            st.session_state.ai_feedback = ai_feedback
            st.session_state.interview_questions = interview_qs
            st.session_state.analysis_done = True

        st.success(f"✅ {t('upload_success')} Navigate to Dashboard to see your results.", icon="🎉")

        # Auto-navigate to dashboard
        st.session_state.active_page = "dashboard"
        st.rerun()


# ─────────────────────────────────────────────
# Page: Dashboard
# ─────────────────────────────────────────────

def page_dashboard() -> None:
    """Render the main analysis dashboard."""
    lang = st.session_state.lang
    t = lambda k: get_text(k, lang)

    if not st.session_state.analysis_done:
        st.info(f"📤 {t('no_resume')} — go to **Upload Resume** to begin.")
        return

    match_result = st.session_state.match_result
    ats_result = st.session_state.ats_result
    parsed = st.session_state.parsed_resume

    st.markdown(f"## {t('dashboard_title')}")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top: Candidate info ───────────────────
    render_candidate_info(parsed)

    # ── KPI Cards ────────────────────────────
    render_metric_cards(match_result, ats_result, lang)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row ───────────────────────────
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        render_match_gauge(match_result.get("overall_score", 0), lang)
    with col2:
        render_component_radar(match_result, lang)

    st.markdown("<hr style='border-color: #E5E7EB; margin: 24px 0;'>", unsafe_allow_html=True)

    # ── ATS Breakdown ─────────────────────────
    col3, col4 = st.columns([1, 1], gap="large")
    with col3:
        render_ats_breakdown(ats_result, lang)
    with col4:
        render_ats_suggestions(ats_result, lang)


# ─────────────────────────────────────────────
# Page: Skills Analysis
# ─────────────────────────────────────────────

def page_skills() -> None:
    """Render the skills analysis page."""
    lang = st.session_state.lang
    t = lambda k: get_text(k, lang)

    if not st.session_state.analysis_done:
        st.info(f"📤 {t('no_resume')} — go to **Upload Resume** to begin.")
        return

    st.markdown(f"## {t('skills_title')}")
    st.markdown("<br>", unsafe_allow_html=True)
    render_skills_section(st.session_state.match_result, lang)


# ─────────────────────────────────────────────
# Page: Interview Prep
# ─────────────────────────────────────────────

def page_interview() -> None:
    """Render the interview preparation page."""
    lang = st.session_state.lang
    t = lambda k: get_text(k, lang)

    if not st.session_state.analysis_done:
        st.info(f"📤 {t('no_resume')} — go to **Upload Resume** to begin.")
        return

    st.markdown(f"## {t('interview_title')}")
    st.markdown("<br>", unsafe_allow_html=True)
    render_interview_questions(st.session_state.interview_questions, lang)


# ─────────────────────────────────────────────
# Page: AI Feedback
# ─────────────────────────────────────────────

def page_feedback() -> None:
    """Render the AI feedback and voice output page."""
    lang = st.session_state.lang
    t = lambda k: get_text(k, lang)

    if not st.session_state.analysis_done:
        st.info(f"📤 {t('no_resume')} — go to **Upload Resume** to begin.")
        return

    st.markdown(f"## {t('feedback_title')}")

    feedback = st.session_state.ai_feedback
    ai_badge = "🤖 AI-Powered" if feedback.get("ai_powered") else "📋 Rule-Based"
    st.markdown(f"<span class='badge badge-ai'>{ai_badge}</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    render_ai_feedback(feedback, lang)

    # ── Voice Feedback ────────────────────────
    st.markdown("<hr style='border-color: #E5E7EB; margin: 24px 0;'>", unsafe_allow_html=True)
    st.markdown(f"#### 🔊 {t('voice_feedback')}")

    if st.button(f"🎧 {t('voice_feedback')}"):
        with st.spinner("Generating audio..."):
            match_score = st.session_state.match_result.get("overall_score", 0)
            ats_score = st.session_state.ats_result.get("ats_score", 0)
            audio_bytes = generate_voice_feedback(feedback, match_score, ats_score)

        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
            st.download_button(
                label=f"⬇ {t('download_audio')}",
                data=audio_bytes,
                file_name="resumefit_feedback.mp3",
                mime="audio/mp3",
            )
        else:
            st.warning("Voice feedback unavailable. Install `gtts` to enable this feature.")


# ─────────────────────────────────────────────
# Main App
# ─────────────────────────────────────────────

def main() -> None:
    """Main application entry point."""
    init_session_state()
    inject_css()

    lang = st.session_state.lang
    t = lambda k: get_text(k, lang)

    # ── Header ───────────────────────────────
    st.markdown(f"""
    <div class="main-header">
        <h1>📄 {t('app_title')} <span class="header-accent">AI</span></h1>
        <p>{t('app_subtitle')}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar Navigation ────────────────────
    active_page = render_sidebar()

    # ── Route to correct page ─────────────────
    if active_page == "upload":
        page_upload()
    elif active_page == "dashboard":
        page_dashboard()
    elif active_page == "skills":
        page_skills()
    elif active_page == "interview":
        page_interview()
    elif active_page == "feedback":
        page_feedback()


if __name__ == "__main__":
    main()
