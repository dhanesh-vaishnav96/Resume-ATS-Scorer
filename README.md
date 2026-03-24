# ResumeIQ — AI-Powered ATS Resume Analyzer

> **Production-grade Applicant Tracking System** that evaluates resumes against job descriptions using a hybrid rule-based + LLM pipeline, delivering structured scores and explainable hiring recommendations.

---

## 🚀 Overview

**ResumeIQ** is a production-ready ATS (Applicant Tracking System) that automates resume screening by:

- **Parsing PDF resumes** into structured, clean data.
- **Extracting required skills** from job descriptions using NLP and Gemini AI.
- **Calculating a weighted ATS score** across skills, projects, education, and experience.
- **Generating professional recommendations** via Google Gemini 1.5 Flash.

Built for accuracy and scalability, it's suitable for real-world HR tooling and portfolio showcases.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI (Python 3.11+) |
| **PDF Parsing** | pdfplumber |
| **AI / LLM** | Google Gemini 1.5 Flash |
| **Skill Extraction** | Hybrid (Regex + Gemini) |
| **Frontend** | Vanilla HTML, CSS, JavaScript |
| **Validation** | Pydantic v2 |
| **Deployment** | Docker + Docker Compose |
| **Testing** | Pytest + HTTPX |

---

## 🔄 Workflow

The system follows a controlled pipeline architecture:

1.  **Extraction**: The user uploads a PDF and pastes a JD. `pdfplumber` extracts text, and Gemini identifies required skills.
2.  **Matching**: A hybrid matcher compares resume skills against JD requirements using keyword matching and semantic context.
3.  **Scoring**: The engine calculates a score based on:
    - **Skills Match (50%)**: Linear scoring of identified vs. required skills.
    - **Projects (30%)**: Relevance of project descriptions to the JD.
    - **Education (10%)**: Automated CGPA/Percentage conversion.
    - **Experience (10%)**: Year extraction with fresher-aware logic.
4.  **AI Audit**: Gemini generates a structured recommendation highlighting strengths and weaknesses.
5.  **Output**: A detailed JSON response and visual dashboard (Frontend) are presented to the user.

---

## 📁 Project Structure

```text
ATS Score Generator/
├── app/
│   ├── api/ v1/ endpoints/
│   │   └── analyze.py        # POST /api/v1/analyze
│   ├── core/
│   │   ├── parser.py         # PDF text extraction
│   │   ├── matcher.py        # Hybrid skill matcher
│   │   ├── scorer.py         # Weighted scoring engine
│   │   └── ai_engine.py      # Gemini API integration
│   ├── models/               # Pydantic schemas
│   └── data/                 # Skills database
├── frontend/
│   └── index.html            # Minimalistic dashboard
├── tests/                    # Comprehensive test suite
├── Dockerfile                # Containerization
└── .env.example              # Environment template
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.11+
- Google Gemini API Key

### 2. Installation
```bash
# Clone the repo
git clone <repository_url>
cd ATS_Score_Generator

# Create Virtual Environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install Dependencies
pip install -r requirements.txt
```

### 3. Configuration
Copy `.env.example` to `.env` and add your `GEMINI_API_KEY`.

### 4. Running the App
```bash
# Start FastAPI
uvicorn app.main:app --reload
```
Open `frontend/index.html` in your browser to use the UI.

---

## 🎯 Scoring System

| ATS Score | Grade | Decision Band |
|---|---|---|
| 85 – 100 | A | Strong Hire |
| 70 – 84 | B+ | Recommended |
| 55 – 69 | B | Consider |
| < 40 | D | Not Recommended |

---

## 🐳 Docker Deployment
```bash
docker compose up --build
```

---

*Built by [Dhanesh Vaishnav](https://github.com/dhanesh-vaishnav)*
