# 📄 ResumeFit AI

> Intelligent Resume Analysis & Job Match Platform — powered by AI, deployable on Streamlit Cloud.

![ResumeFit AI](https://img.shields.io/badge/ResumeFit-AI-3FA796?style=for-the-badge&logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.10+-1E2A38?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=for-the-badge&logo=streamlit)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-412991?style=for-the-badge&logo=openai)

---

## 🎯 Overview

**ResumeFit AI** is a professional resume analyzer that helps job seekers understand how well their resume matches a target job description. It provides:

- **ATS Score** — how well your resume performs against applicant tracking systems
- **Job Match Percentage** — weighted similarity score across skills, experience, education, and keywords
- **Skill Gap Analysis** — matched vs. missing skills with importances
- **AI Feedback** — strengths, weaknesses, and actionable recommendations
- **Interview Prep** — AI-generated technical, behavioral, and role-specific questions
- **Voice Feedback** — spoken summary via text-to-speech
- **Bilingual UI** — English and Urdu

---

## ✨ Features

| Feature | Description |
|---|---|
| 📤 Resume Upload | PDF and DOCX support |
| 📊 Dashboard | Score cards, charts, radar analysis |
| 🎯 Job Match | Weighted TF-IDF cosine similarity |
| 🤖 ATS Scoring | 5-factor ATS optimization check |
| 💡 Skills Analysis | 200+ skills database, tag-chip UI |
| 🎤 Interview Prep | AI-generated Q&A by category |
| 🔊 Voice Feedback | gTTS audio summary |
| 🌐 Bilingual | English + Urdu UI toggle |

---

## 🗂️ Project Structure

```
resume-analyzer/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md
│
├── utils/
│   ├── parser.py           # PDF/DOCX text extraction & field parsing
│   ├── skills.py           # Skill extraction from 200+ skills DB
│   ├── matcher.py          # Weighted job match calculator
│   ├── ats.py              # ATS score estimator (5 factors)
│   └── interview.py        # AI interview question generator
│
├── ui/
│   ├── dashboard.py        # All dashboard UI components
│   ├── upload.py           # Upload section component
│   └── bilingual.py        # English/Urdu translation dictionaries
│
├── assets/
│   └── styles/
│       └── styles.css      # Professional custom CSS
│
└── temp_uploads/           # Temporary file storage (gitignored)
```

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/resume-analyzer.git
cd resume-analyzer
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your OpenAI API key (optional)
```bash
export OPENAI_API_KEY=sk-your-key-here
```
> **Note:** The app works fully without an API key using intelligent rule-based analysis. An API key enables AI-generated feedback and interview questions.

### 4. Run the app
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

---

## 🌐 Deploy on Streamlit Cloud

1. Push your project to a **GitHub repository**

2. Go to [share.streamlit.io](https://share.streamlit.io) and click **New app**

3. Select your repository, branch (`main`), and main file (`app.py`)

4. In **Advanced settings → Secrets**, add:
   ```toml
   OPENAI_API_KEY = "sk-your-key-here"
   ```

5. Click **Deploy** — your app goes live in ~2 minutes!

---

## 🔑 API Setup

### OpenAI (Optional but recommended)

1. Go to [platform.openai.com](https://platform.openai.com)
2. Create an account and generate an API key
3. Add it via the sidebar in the app, or as an environment variable

The app uses `gpt-3.5-turbo` for cost efficiency.

**Without API key:** The app uses TF-IDF similarity + rule-based analysis — all core features still work.

---

## 📸 Screenshots

> *(Add screenshots after deployment)*

| Upload Page | Dashboard | Skills Analysis |
|---|---|---|
| ![upload](screenshots/upload.png) | ![dashboard](screenshots/dashboard.png) | ![skills](screenshots/skills.png) |

---

## 🎨 Design System

| Token | Value |
|---|---|
| Primary | `#1E2A38` Deep Navy |
| Secondary | `#5B6C8F` Slate Blue |
| Accent | `#3FA796` Warm Teal |
| Background | `#F7F9FC` Off White |
| Success | `#6BBF59` |
| Warning | `#E6A23C` |

Typography: **DM Sans** (body) + **DM Serif Display** (headings)

---

## 🧑‍💻 Tech Stack

- **Frontend:** Streamlit
- **AI:** OpenAI GPT-3.5-turbo
- **NLP:** scikit-learn TF-IDF, keyword matching
- **PDF:** pdfplumber, PyPDF2
- **DOCX:** python-docx
- **Charts:** Plotly
- **TTS:** gTTS
- **Language:** Python 3.10+

---

## 📄 License

MIT License — free to use, modify, and deploy.

---

*Built with ❤️ for job seekers everywhere.*
