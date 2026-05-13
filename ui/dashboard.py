"""
dashboard.py
------------
Main analysis dashboard UI for ResumeFit AI.
Renders all score cards, charts, skills, and feedback panels.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from ui.bilingual import get_text, get_score_label


# ─────────────────────────────────────────────
# Score Color Helpers
# ─────────────────────────────────────────────

def _score_color(score: int) -> str:
    """Return a hex color based on score range."""
    if score >= 75:
        return "#6BBF59"   # success green
    elif score >= 50:
        return "#E6A23C"   # warning amber
    else:
        return "#E05C5C"   # danger red


# ─────────────────────────────────────────────
# Top Metrics Row
# ─────────────────────────────────────────────

def render_metric_cards(match_result: dict, ats_result: dict, lang: str = "en") -> None:
    """Render the top-row KPI cards."""
    t = lambda k: get_text(k, lang)

    match_score = match_result.get("overall_score", 0)
    ats_score = ats_result.get("ats_score", 0)
    skills_count = len(match_result.get("resume_skills", []))
    missing_count = len(match_result.get("missing_skills", []))

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        _metric_card(
            label=t("match_score"),
            value=f"{match_score}%",
            sub=get_score_label(match_score, lang),
            color=_score_color(match_score),
            icon="🎯",
        )
    with c2:
        _metric_card(
            label=t("ats_score"),
            value=f"{ats_score}%",
            sub=get_score_label(ats_score, lang),
            color=_score_color(ats_score),
            icon="🤖",
        )
    with c3:
        _metric_card(
            label=t("skills_found"),
            value=str(skills_count),
            sub="skills detected",
            color="#5B6C8F",
            icon="💡",
        )
    with c4:
        _metric_card(
            label=t("missing_skills"),
            value=str(missing_count),
            sub="to acquire",
            color="#E6A23C" if missing_count > 0 else "#6BBF59",
            icon="📋",
        )


def _metric_card(label: str, value: str, sub: str, color: str, icon: str) -> None:
    """Render a single metric KPI card."""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-body">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color: {color};">{value}</div>
            <div class="metric-sub">{sub}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Match Score Gauge Chart
# ─────────────────────────────────────────────

def render_match_gauge(score: int, lang: str = "en") -> None:
    """Render a circular gauge chart for match percentage."""
    t = lambda k: get_text(k, lang)
    color = _score_color(score)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": t("match_score"), "font": {"size": 16, "color": "#222831"}},
        number={"suffix": "%", "font": {"size": 40, "color": color}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#6B7280"},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "white",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 30], "color": "#FEE2E2"},
                {"range": [30, 60], "color": "#FEF3C7"},
                {"range": [60, 100], "color": "#D1FAE5"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.75,
                "value": score,
            },
        },
    ))

    fig.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, sans-serif"},
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# ATS Score Breakdown
# ─────────────────────────────────────────────

def render_ats_breakdown(ats_result: dict, lang: str = "en") -> None:
    """Render ATS component score progress bars."""
    t = lambda k: get_text(k, lang)

    component_labels = {
        "keyword_optimization": t("ats_keyword"),
        "formatting": t("ats_format"),
        "readability": t("ats_readability"),
        "section_completeness": t("ats_completeness"),
        "contact_information": t("ats_contact"),
    }

    scores = ats_result.get("component_scores", {})

    st.markdown(f"#### {t('ats_title')}")
    st.markdown(f"**ATS Score: {ats_result.get('ats_score', 0)}%**")
    st.progress(ats_result.get("ats_score", 0) / 100)
    st.markdown("<br>", unsafe_allow_html=True)

    for key, label in component_labels.items():
        score = scores.get(key, 0)
        color = _score_color(score)
        st.markdown(f"""
        <div class="ats-bar-row">
            <span class="ats-bar-label">{label}</span>
            <span class="ats-bar-score" style="color:{color};">{score}%</span>
        </div>
        """, unsafe_allow_html=True)
        st.progress(score / 100)
        st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Component Score Radar Chart
# ─────────────────────────────────────────────

def render_component_radar(match_result: dict, lang: str = "en") -> None:
    """Render a radar/spider chart of match component scores."""
    t = lambda k: get_text(k, lang)
    scores = match_result.get("component_scores", {})

    if not scores:
        return

    categories = ["Skills", "Experience", "Education", "Keywords", "Projects"]
    values = [
        scores.get("skills", 0),
        scores.get("experience", 0),
        scores.get("education", 0),
        scores.get("keywords", 0),
        scores.get("projects", 0),
    ]
    values_closed = values + [values[0]]
    categories_closed = categories + [categories[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill="toself",
        fillcolor="rgba(63, 167, 150, 0.15)",
        line=dict(color="#3FA796", width=2),
        name="Match Score",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10)),
            angularaxis=dict(tickfont=dict(size=12)),
        ),
        showlegend=False,
        height=300,
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# Skills Section
# ─────────────────────────────────────────────

def render_skills_section(match_result: dict, lang: str = "en") -> None:
    """Render matched and missing skills as tag chips."""
    t = lambda k: get_text(k, lang)

    matched = match_result.get("matched_skills", [])
    missing = match_result.get("missing_skills", [])
    resume_skills = match_result.get("resume_skills", [])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### ✅ {t('matched_skills')}")
        if matched:
            chips_html = " ".join(
                f'<span class="skill-chip skill-matched">{s}</span>' for s in matched
            )
            st.markdown(f'<div class="skills-container">{chips_html}</div>', unsafe_allow_html=True)
        else:
            st.info("Upload a job description to see matched skills.")

        st.markdown(f"<br>#### 🧠 {t('technical_skills')}", unsafe_allow_html=True)
        if resume_skills:
            non_matched = [s for s in resume_skills if s not in matched][:20]
            chips_html = " ".join(
                f'<span class="skill-chip skill-resume">{s}</span>' for s in non_matched
            )
            st.markdown(f'<div class="skills-container">{chips_html}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f"#### ⚠️ {t('missing_skills_title')}")
        if missing:
            chips_html = " ".join(
                f'<span class="skill-chip skill-missing">{s}</span>' for s in missing
            )
            st.markdown(f'<div class="skills-container">{chips_html}</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="info-box warning">
                💡 <strong>Tip:</strong> Focus on acquiring these {len(missing)} skills to significantly 
                improve your match rate.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success("Great! Your resume covers all the required skills.")


# ─────────────────────────────────────────────
# Interview Questions
# ─────────────────────────────────────────────

def render_interview_questions(questions: dict, lang: str = "en") -> None:
    """Render interview questions in accordion tabs."""
    t = lambda k: get_text(k, lang)

    ai_powered = questions.get("ai_powered", False)
    badge = "🤖 AI-Generated" if ai_powered else "📋 Curated"

    st.markdown(f"""
    <div class="section-header">
        <h4>{t('interview_title')}</h4>
        <span class="badge {'badge-ai' if ai_powered else 'badge-default'}">{badge}</span>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        f"🔧 {t('technical_questions')}",
        f"🧑‍💼 {t('behavioral_questions')}",
        f"🎯 {t('role_questions')}",
    ])

    with tab1:
        _render_question_list(questions.get("technical", []))

    with tab2:
        _render_question_list(questions.get("behavioral", []))

    with tab3:
        _render_question_list(questions.get("role_specific", []))


def _render_question_list(questions: list[str]) -> None:
    """Render a numbered list of interview questions."""
    if not questions:
        st.info("No questions generated.")
        return
    for i, q in enumerate(questions, 1):
        st.markdown(f"""
        <div class="question-card">
            <span class="question-number">Q{i}</span>
            <span class="question-text">{q}</span>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# AI Feedback
# ─────────────────────────────────────────────

def render_ai_feedback(feedback: dict, lang: str = "en") -> None:
    """Render AI-generated feedback: strengths, weaknesses, suggestions."""
    t = lambda k: get_text(k, lang)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### 💪 {t('strengths')}")
        strengths = feedback.get("strengths", [])
        if strengths:
            for item in strengths:
                st.markdown(f"""
                <div class="feedback-item feedback-strength">
                    <span class="feedback-icon">✓</span> {item}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No data available.")

    with col2:
        st.markdown(f"#### 🔧 {t('weaknesses')}")
        weaknesses = feedback.get("weaknesses", [])
        if weaknesses:
            for item in weaknesses:
                st.markdown(f"""
                <div class="feedback-item feedback-weakness">
                    <span class="feedback-icon">△</span> {item}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No data available.")

    st.markdown(f"#### 💡 {t('suggestions')}")
    suggestions = feedback.get("suggestions", [])
    if suggestions:
        for item in suggestions:
            st.markdown(f"""
            <div class="feedback-item feedback-suggestion">
                <span class="feedback-icon">→</span> {item}
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ATS Suggestions Panel
# ─────────────────────────────────────────────

def render_ats_suggestions(ats_result: dict, lang: str = "en") -> None:
    """Render ATS improvement suggestions."""
    t = lambda k: get_text(k, lang)

    suggestions = ats_result.get("suggestions", [])
    if not suggestions:
        st.success("✅ Your resume is well-optimized for ATS systems!")
        return

    st.markdown(f"#### 📌 {t('ats_suggestions')}")
    for s in suggestions:
        st.markdown(f"""
        <div class="suggestion-item">
            <span>→</span> {s}
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Candidate Info Card
# ─────────────────────────────────────────────

def render_candidate_info(parsed_resume: dict) -> None:
    """Render parsed candidate profile information."""
    name = parsed_resume.get("name", "Not found")
    email = parsed_resume.get("email", "Not found")
    phone = parsed_resume.get("phone", "Not found")
    linkedin = parsed_resume.get("linkedin", "")
    experience_years = parsed_resume.get("experience_years", 0)
    education = parsed_resume.get("education", [])
    certs = parsed_resume.get("certifications", [])

    st.markdown(f"""
    <div class="profile-card">
        <div class="profile-avatar">{name[0].upper() if name and name != 'Not found' else '?'}</div>
        <div class="profile-info">
            <div class="profile-name">{name}</div>
            <div class="profile-details">
                {"📧 " + email if email and email != "Not found" else ""}
                {"&nbsp;&nbsp;📱 " + phone if phone and phone != "Not found" else ""}
                {f"&nbsp;&nbsp;💼 {experience_years} yrs exp" if experience_years else ""}
            </div>
            {f'<div class="profile-linkedin">🔗 {linkedin}</div>' if linkedin else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if education:
        with st.expander("🎓 Education"):
            for edu in education[:3]:
                st.markdown(f"• {edu}")

    if certs:
        with st.expander("🏆 Certifications"):
            for cert in certs[:5]:
                st.markdown(f"• {cert}")
