"""
bilingual.py
------------
Bilingual support for ResumeFit AI.
Provides English and Urdu translations for all UI labels.
"""

# Translation dictionaries
TRANSLATIONS = {
    "en": {
        # App
        "app_title": "ResumeFit AI",
        "app_subtitle": "Intelligent Resume Analysis & Job Match Platform",
        "language_toggle": "اردو",

        # Sidebar
        "sidebar_title": "Navigation",
        "nav_upload": "Upload Resume",
        "nav_dashboard": "Dashboard",
        "nav_skills": "Skills Analysis",
        "nav_interview": "Interview Prep",
        "nav_feedback": "AI Feedback",

        # Upload
        "upload_title": "Upload Your Resume",
        "upload_instruction": "Drag & drop your resume here or click to browse",
        "upload_formats": "Supported formats: PDF, DOCX",
        "upload_job_desc": "Paste Job Description",
        "upload_job_placeholder": "Paste the full job description here...",
        "upload_analyze": "Analyze Resume",
        "upload_success": "Resume uploaded successfully!",
        "upload_error": "Upload failed. Please try again.",
        "upload_invalid": "Invalid file format. Only PDF and DOCX are supported.",

        # Dashboard
        "dashboard_title": "Analysis Dashboard",
        "match_score": "Job Match Score",
        "ats_score": "ATS Score",
        "skills_found": "Skills Detected",
        "missing_skills": "Missing Skills",
        "experience_years": "Years of Experience",
        "sections_complete": "Profile Completeness",

        # Skills
        "skills_title": "Skills Analysis",
        "matched_skills": "Matched Skills",
        "missing_skills_title": "Missing Skills",
        "skill_gap": "Skill Gap Analysis",
        "technical_skills": "Technical Skills",
        "soft_skills": "Soft Skills",

        # ATS
        "ats_title": "ATS Score Breakdown",
        "ats_keyword": "Keyword Optimization",
        "ats_format": "Formatting",
        "ats_readability": "Readability",
        "ats_completeness": "Section Completeness",
        "ats_contact": "Contact Information",
        "ats_suggestions": "Improvement Suggestions",

        # Interview
        "interview_title": "Interview Preparation",
        "technical_questions": "Technical Questions",
        "behavioral_questions": "Behavioral Questions",
        "role_questions": "Role-Specific Questions",
        "generate_questions": "Generate Interview Questions",

        # Feedback
        "feedback_title": "AI Feedback",
        "strengths": "Strengths",
        "weaknesses": "Areas to Improve",
        "suggestions": "Recommendations",
        "voice_feedback": "Play Voice Feedback",
        "download_audio": "Download Audio",

        # General
        "loading": "Analyzing your resume...",
        "error": "Something went wrong. Please try again.",
        "no_resume": "Please upload a resume first.",
        "score_label": "Score",
        "view_details": "View Details",
        "excellent": "Excellent",
        "good": "Good",
        "average": "Average",
        "needs_work": "Needs Improvement",
    },
    "ur": {
        # App
        "app_title": "ریزیومے فٹ اے آئی",
        "app_subtitle": "ذہین ریزیومے تجزیہ اور ملازمت مطابقت پلیٹ فارم",
        "language_toggle": "English",

        # Sidebar
        "sidebar_title": "نیویگیشن",
        "nav_upload": "ریزیومے اپلوڈ کریں",
        "nav_dashboard": "ڈیش بورڈ",
        "nav_skills": "مہارتوں کا تجزیہ",
        "nav_interview": "انٹرویو کی تیاری",
        "nav_feedback": "اے آئی فیڈبیک",

        # Upload
        "upload_title": "اپنا ریزیومے اپلوڈ کریں",
        "upload_instruction": "ریزیومے یہاں ڈراپ کریں یا براؤز کریں",
        "upload_formats": "قابل قبول فارمیٹ: PDF, DOCX",
        "upload_job_desc": "ملازمت کی تفصیل درج کریں",
        "upload_job_placeholder": "یہاں مکمل ملازمت کی تفصیل پیسٹ کریں...",
        "upload_analyze": "ریزیومے کا تجزیہ کریں",
        "upload_success": "ریزیومے کامیابی سے اپلوڈ ہو گیا!",
        "upload_error": "اپلوڈ ناکام ہوا۔ دوبارہ کوشش کریں۔",
        "upload_invalid": "غلط فائل فارمیٹ۔ صرف PDF اور DOCX قابل قبول ہیں۔",

        # Dashboard
        "dashboard_title": "تجزیہ ڈیش بورڈ",
        "match_score": "ملازمت مطابقت اسکور",
        "ats_score": "اے ٹی ایس اسکور",
        "skills_found": "پائی گئی مہارتیں",
        "missing_skills": "مطلوبہ مہارتیں",
        "experience_years": "تجربے کے سال",
        "sections_complete": "پروفائل مکملیت",

        # Skills
        "skills_title": "مہارتوں کا تجزیہ",
        "matched_skills": "مطابق مہارتیں",
        "missing_skills_title": "غائب مہارتیں",
        "skill_gap": "مہارت کا فرق",
        "technical_skills": "تکنیکی مہارتیں",
        "soft_skills": "نرم مہارتیں",

        # ATS
        "ats_title": "اے ٹی ایس اسکور تفصیل",
        "ats_keyword": "کلیدی الفاظ کی بہتری",
        "ats_format": "فارمیٹنگ",
        "ats_readability": "پڑھنے کی آسانی",
        "ats_completeness": "سیکشن مکملیت",
        "ats_contact": "رابطہ معلومات",
        "ats_suggestions": "بہتری کی تجاویز",

        # Interview
        "interview_title": "انٹرویو کی تیاری",
        "technical_questions": "تکنیکی سوالات",
        "behavioral_questions": "رویے کے سوالات",
        "role_questions": "کردار مخصوص سوالات",
        "generate_questions": "انٹرویو سوالات بنائیں",

        # Feedback
        "feedback_title": "اے آئی فیڈبیک",
        "strengths": "طاقتیں",
        "weaknesses": "بہتری کے شعبے",
        "suggestions": "سفارشات",
        "voice_feedback": "آواز کا فیڈبیک سنیں",
        "download_audio": "آڈیو ڈاؤن لوڈ کریں",

        # General
        "loading": "آپ کا ریزیومے تجزیہ ہو رہا ہے...",
        "error": "کچھ غلط ہو گیا۔ دوبارہ کوشش کریں۔",
        "no_resume": "پہلے ریزیومے اپلوڈ کریں۔",
        "score_label": "اسکور",
        "view_details": "تفصیل دیکھیں",
        "excellent": "بہترین",
        "good": "اچھا",
        "average": "اوسط",
        "needs_work": "بہتری درکار",
    }
}


def get_text(key: str, lang: str = "en") -> str:
    """
    Retrieve a translated string for the given key and language.
    Falls back to English if key not found in target language.
    """
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))


def get_score_label(score: int, lang: str = "en") -> str:
    """Return a qualitative label based on numeric score."""
    t = lambda k: get_text(k, lang)
    if score >= 85:
        return t("excellent")
    elif score >= 70:
        return t("good")
    elif score >= 50:
        return t("average")
    else:
        return t("needs_work")
