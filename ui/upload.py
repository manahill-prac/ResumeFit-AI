"""
upload.py
---------
Resume and job description upload UI for ResumeFit AI.
"""

import streamlit as st
from ui.bilingual import get_text


def render_upload_section(lang: str = "en") -> tuple[bytes | None, str, str]:
    """
    Render the resume upload and job description input section.
    
    Returns:
        (file_bytes, file_type, job_description)
        file_bytes: bytes of uploaded file, or None
        file_type: 'pdf' or 'docx'
        job_description: text entered by user
    """
    t = lambda key: get_text(key, lang)

    st.markdown(f"""
    <div class="upload-header">
        <h2>{t('upload_title')}</h2>
        <p style="color: var(--text-secondary);">{t('upload_instruction')}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    # ── Left Column: File Upload ──────────────────────────────
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-header">📄 Resume</div>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            label=t("upload_formats"),
            type=["pdf", "docx", "doc"],
            help=t("upload_formats"),
            label_visibility="visible",
        )

        file_bytes = None
        file_type = ""

        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            fname = uploaded_file.name.lower()
            if fname.endswith(".pdf"):
                file_type = "pdf"
            elif fname.endswith((".docx", ".doc")):
                file_type = "docx"
            else:
                st.error(t("upload_invalid"))
                return None, "", ""

            # File info card
            size_kb = len(file_bytes) / 1024
            st.markdown(f"""
            <div class="file-info-card">
                <div class="file-icon">{'📕' if file_type == 'pdf' else '📘'}</div>
                <div class="file-details">
                    <div class="file-name">{uploaded_file.name}</div>
                    <div class="file-size">{size_kb:.1f} KB • {file_type.upper()}</div>
                </div>
                <div class="file-check">✓</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Right Column: Job Description ─────────────────────────
    with col2:
        st.markdown(f"""
        <div class="card-label">💼 {t('upload_job_desc')}</div>
        """, unsafe_allow_html=True)

        job_description = st.text_area(
            label=t("upload_job_desc"),
            placeholder=t("upload_job_placeholder"),
            height=220,
            label_visibility="collapsed",
        )

        if job_description:
            word_count = len(job_description.split())
            st.markdown(f"""
            <div class="char-count">{word_count} words</div>
            """, unsafe_allow_html=True)

    return file_bytes, file_type, job_description
