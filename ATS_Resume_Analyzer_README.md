# ResumeIQ — AI-Powered ATS Resume Analyzer

> **Production-grade Applicant Tracking System** that evaluates resumes against job descriptions using a hybrid rule-based + LLM pipeline, delivering structured scores and explainable hiring recommendations.

---

## Table of Contents

- [Overview](#overview)
- [Live Demo](#live-demo)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Scoring System](#scoring-system)
- [UI Overview](#ui-overview)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

---

## Overview

**ResumeIQ** is a production-ready ATS (Applicant Tracking System) that automates resume screening by:

- Parsing PDF resumes into structured data
- Extracting required skills from job descriptions using NLP + Gemini AI
- Calculating a weighted ATS score across skills, projects, education, and experience
- Generating a concise, professional hiring recommendation via Gemini

Built for accuracy, explainability, and scalability — suitable for real-world HR tooling, portfolio showcases, and internship demonstrations.

---

## Live Demo

```
Coming soon — deploy to Railway / Render with one click
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        CLIENT                           │
│             HTML/CSS/JS (Minimal UI)                    │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP / REST
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                       │
│                                                         │
│   ┌──────────────┐    ┌───────────────────────────┐    │
│   │  PDF Parser  │    │    JD Skill Extractor      │    │
│   │ (pdfplumber) │    │ (Rule-based + Gemini AI)   │    │
│   └──────┬───────┘    └────────────┬──────────────┘    │
│          │                         │                     │
│          ▼                         ▼                     │
│   ┌────────────────────────────────────────────┐        │
│   │           Hybrid Skill Matcher             │        │
│   │    (Keyword Match + Semantic Fallback)     │        │
│   └──────────────────┬─────────────────────────┘        │
│                      │                                   │
│          ┌───────────▼────────────┐                     │
│          │     Scoring Engine     │                     │
│          │  Skills  50% ─────────┤                     │
│          │  Projects 30% ────────┤                     │
│          │  Education 10% ───────┤  → ATS Score        │
│          │  Experience 10% ──────┘                     │
│          └───────────┬────────────┘                     │
│                      │                                   │
│          ┌───────────▼────────────┐                     │
│          │  Gemini AI Recommender │                     │
│          └───────────┬────────────┘                     │
│                      │                                   │
└──────────────────────┼──────────────────────────────────┘
                       │
                       ▼
             JSON Response Output
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI (Python 3.11+) |
| PDF Parsing | pdfplumber |
| AI / LLM | Google Gemini 1.5 Flash |
| Skill Extraction | Hybrid (Regex + Gemini) |
| Frontend | Vanilla HTML, CSS, JavaScript |
| API Auth | API Key via `.env` |
| Validation | Pydantic v2 |
| Logging | Python `logging` + structured JSON logs |
| Containerization | Docker + Docker Compose |
| Testing | Pytest + HTTPX |
| Code Quality | Ruff, Black, pre-commit hooks |

---

## Features

### Core
- PDF resume text extraction with noise cleanup
- Hybrid skill extraction — rule-based keyword matching + AI contextual detection
- Project-level skill detection (reads descriptions, not just headers)
- Education grade parsing — CGPA and percentage (auto-converted)
- Experience year extraction via regex + NLP
- Weighted ATS scoring engine (configurable weights)
- Gemini AI-generated professional recommendation

### Production Extras
- Structured JSON logging with request IDs
- Input validation and safe error responses
- File type and size guards on upload
- CORS configuration for frontend integration
- Async file handling to avoid blocking
- Environment-based configuration (no hardcoded secrets)
- Docker-ready with health check endpoint

---

## Project Structure

```
resumeiq/
│
├── app/
│   ├── main.py               # FastAPI app entry point, routes
│   ├── config.py             # Settings via pydantic-settings
│   │
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           └── analyze.py    # POST /api/v1/analyze
│   │
│   ├── core/
│   │   ├── parser.py         # PDF text extraction + cleanup
│   │   ├── matcher.py        # Hybrid skill matcher
│   │   ├── scorer.py         # Weighted ATS scoring engine
│   │   └── ai_engine.py      # Gemini API integration
│   │
│   ├── models/
│   │   ├── request.py        # Pydantic input models
│   │   └── response.py       # Pydantic output models
│   │
│   ├── data/
│   │   └── skills_db.json    # Curated master skills list
│   │
│   └── utils/
│       ├── logger.py         # Structured JSON logger
│       └── file_guard.py     # Upload validation helpers
│
├── frontend/
│   └── index.html            # Single-file minimal UI
│
├── tests/
│   ├── test_parser.py
│   ├── test_matcher.py
│   ├── test_scorer.py
│   └── test_api.py
│
├── uploads/                  # Temp upload directory (gitignored)
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Google Gemini API Key ([get one here](https://aistudio.google.com/app/apikey))

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/resumeiq.git
cd resumeiq
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
# Open .env and add your GEMINI_API_KEY
```

### 5. Run the Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Open in Browser

```
API Docs:  http://localhost:8000/docs
UI:        Open frontend/index.html in your browser
```

---

## Environment Variables

Create a `.env` file at the project root:

```env
# Required
GEMINI_API_KEY=your_google_gemini_api_key_here

# Optional — defaults shown
APP_ENV=development
MAX_UPLOAD_SIZE_MB=5
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

> Never commit `.env` to version control. Use `.env.example` for documentation.

---

## API Reference

### `POST /api/v1/analyze`

Analyze a resume against a job description.

**Content-Type:** `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `resume` | File (PDF) | Yes | Candidate's resume in PDF format |
| `job_description` | string | Yes | Full job description as plain text |

**Response — 200 OK**

```json
{
  "request_id": "3f7a1c29-...",
  "ats_score": 74.5,
  "grade": "B+",
  "skills_matched": ["Python", "FastAPI", "SQL", "Docker"],
  "skills_missing": ["Kubernetes", "Redis"],
  "sub_scores": {
    "skills": 38.0,
    "projects": 18.5,
    "education": 10.0,
    "experience": 8.0
  },
  "recommendation": "Strong technical candidate with hands-on project experience. Minor gaps in infrastructure tooling. Recommended for technical interview round.",
  "processed_at": "2025-09-01T14:32:11Z"
}
```

**Error Responses**

| Status | Meaning |
|---|---|
| 400 | Invalid file type or empty JD |
| 413 | File exceeds size limit |
| 422 | Validation error |
| 500 | Internal server / Gemini API error |

### `GET /health`

Returns service health status.

```json
{ "status": "ok", "version": "1.0.0" }
```

---

## Scoring System

### Weight Distribution

| Component | Weight | Rationale |
|---|---|---|
| Skills Match | 50% | Primary signal for role fit |
| Project Relevance | 30% | Validates practical application |
| Education | 10% | Academic baseline |
| Experience | 10% | Industry exposure |

### Skill Score — 50 pts

```
Skill Score = (Matched Skills / Total JD Skills) × 50
```

Matching is hybrid:
1. Exact and normalized keyword match (rule-based)
2. Contextual AI extraction for inferred skills (Gemini)

### Project Score — 30 pts

Each project is scanned for JD-relevant technologies. Projects contribute proportionally based on skill overlap:

```
Project Score = Σ (Skills Found in Project / JD Skills) × 30
                  (capped at 30)
```

### Education Score — 10 pts

| CGPA | Points |
|---|---|
| ≥ 8.0 | 10 |
| ≥ 6.0 | 7 |
| < 6.0 | 4 |

Percentage is auto-converted: `CGPA = Percentage / 9.5`

### Experience Score — 10 pts

| Years of Experience | Points |
|---|---|
| ≥ 3 years | 10 |
| ≥ 1 year | 7 |
| < 1 year (or fresher) | 4 |

### Grade Scale

| ATS Score | Grade | Decision Band |
|---|---|---|
| 85 – 100 | A | Strong Hire |
| 70 – 84 | B+ | Recommended |
| 55 – 69 | B | Consider |
| 40 – 54 | C | Borderline |
| < 40 | D | Not Recommended |

---

## UI Overview

The frontend is a single `index.html` file — no framework, no build step.

```
┌────────────────────────────────────────┐
│  ResumeIQ                    [Light☀] │
├────────────────────────────────────────┤
│                                        │
│  [ Upload Resume (PDF) ▲ ]            │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │  Paste Job Description here...  │  │
│  └──────────────────────────────────┘  │
│                                        │
│         [ Analyze Resume → ]          │
│                                        │
├────────────────────────────────────────┤
│  ATS Score          74.5 / 100  [B+]  │
│                                        │
│  ✅ Matched Skills                     │
│  Python · FastAPI · SQL · Docker      │
│                                        │
│  ❌ Missing Skills                     │
│  Kubernetes · Redis                   │
│                                        │
│  📊 Score Breakdown                   │
│  Skills ████████░░  38/50             │
│  Projects ████░░░░  18.5/30           │
│  Education ██████░  10/10             │
│  Experience █████░   8/10             │
│                                        │
│  💬 Recommendation                    │
│  Strong technical candidate...        │
└────────────────────────────────────────┘
```

---

## Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing
```

Test files cover:
- `test_parser.py` — PDF extraction edge cases
- `test_matcher.py` — skill matching accuracy
- `test_scorer.py` — scoring logic and boundary conditions
- `test_api.py` — end-to-end API integration tests

---

## Docker Deployment

### Build and Run

```bash
docker compose up --build
```

### `docker-compose.yml` (excerpt)

```yaml
version: "3.9"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./uploads:/app/uploads
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### One-click Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

---

## Roadmap

| Status | Feature |
|---|---|
| ✅ Done | PDF parsing, hybrid skill extraction |
| ✅ Done | Weighted scoring engine |
| ✅ Done | Gemini AI recommendation |
| ✅ Done | Minimal HTML/CSS/JS UI |
| 🔄 In Progress | Semantic skill matching with embeddings |
| 🔄 In Progress | Synonym normalization (React vs React.js) |
| 📋 Planned | FAISS vector database for similarity search |
| 📋 Planned | Multi-role batch screening API |
| 📋 Planned | Recruiter dashboard (React) |
| 📋 Planned | JWT auth + user accounts |
| 📋 Planned | Resume improvement suggestions |

---

## Contributing

Contributions are welcome. To get started:

1. Fork the repository
2. Create a feature branch — `git checkout -b feat/your-feature`
3. Commit with conventional commits — `git commit -m "feat: add synonym mapping"`
4. Push and open a Pull Request

Please ensure:
- All tests pass — `pytest tests/`
- Code is formatted — `black .` and `ruff check .`
- New features include tests

---

## Known Limitations

- Keyword-based matching may miss semantic synonyms (e.g., "ML" vs "Machine Learning")
- Highly stylized or image-heavy PDF resumes may not parse cleanly
- Project score depends on resume text quality and formatting consistency
- Gemini API availability affects recommendation generation (fallback: rule-based summary)

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## Author

**Dhanesh Vaishnav**
MCA Final Year | Full Stack & AI Developer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://linkedin.com/in/yourprofile)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?logo=github)](https://github.com/yourusername)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-green)](https://yourportfolio.com)

---

> Built with ❤️ for the hiring community — making resume screening faster, fairer, and more transparent.
