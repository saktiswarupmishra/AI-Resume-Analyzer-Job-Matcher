<p align="center">
  <h1 align="center">🧠 ResumeAI — Smart Resume Analyzer & Job Matcher</h1>
  <p align="center">
    An AI-powered full-stack platform that analyzes resumes, provides ATS compatibility scores, extracts skills using NLP, generates actionable improvement suggestions, and intelligently matches candidates to jobs using TF-IDF cosine similarity.
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Vue.js-3.5-4FC08D?logo=vue.js&logoColor=white" alt="Vue 3" />
  <img src="https://img.shields.io/badge/Vite-5.4-646CFF?logo=vite&logoColor=white" alt="Vite" />
  <img src="https://img.shields.io/badge/Express-4.21-000000?logo=express&logoColor=white" alt="Express" />
  <img src="https://img.shields.io/badge/Prisma-5.20-2D3748?logo=prisma&logoColor=white" alt="Prisma" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white" alt="MySQL" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python" />
</p>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [API Reference](#-api-reference)
- [Database Schema](#-database-schema)
- [AI Pipeline](#-ai-pipeline)
- [Environment Variables](#-environment-variables)
- [License](#-license)

---

## 🔭 Overview

**ResumeAI** is a microservices-based web application that empowers job seekers to:

1. **Upload** their resume (PDF / DOCX)
2. **Parse** and extract text using PyMuPDF / python-docx
3. **Analyze** the resume with NLP (spaCy entity recognition + regex-based skill extraction)
4. **Score** ATS compatibility on a 0–100 scale across 5 weighted categories
5. **Generate** prioritized, actionable improvement suggestions
6. **Match** against a curated job dataset using TF-IDF + cosine similarity

The platform features JWT-secured authentication, a responsive Vue 3 SPA with dark glassmorphism UI, and background async processing of resume analysis.

---

## 🏗 Architecture

```
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│                  │       │                  │       │                  │
│   Vue 3 + Vite   │──────▶│  Express.js API  │──────▶│  FastAPI (AI)    │
│   Frontend       │ :6756 │  Gateway         │ :3000 │  Microservice    │ :8000
│                  │       │                  │       │                  │
└──────────────────┘       └────────┬─────────┘       └──────────────────┘
                                    │
                                    ▼
                           ┌──────────────────┐
                           │   MySQL (Prisma)  │
                           │   Database        │
                           └──────────────────┘
```

- **Frontend** → Vite dev server on `:6756`, proxies `/api` to the backend
- **Backend** → Express API Gateway on `:3000`, handles auth, file uploads, and persists analysis results
- **AI Service** → FastAPI on `:8000`, runs the full NLP analysis pipeline
- **Database** → MySQL via Prisma ORM for user data, resumes, scores, skills, and job matches

---

## ✨ Features

### 🔐 Authentication & Security
- User registration and login with **bcrypt** hashed passwords
- **JWT** token-based authentication with configurable expiration
- Protected route guards on both frontend and backend
- Middleware-based request authorization

### 📄 Resume Management
- Upload **PDF** and **DOCX** files (up to 10 MB)
- Local file storage with Multer (optional Cloudinary integration)
- Resume history dashboard with status tracking
- Full CRUD operations on uploaded resumes

### 🤖 AI-Powered Analysis
- **Text Extraction** — PyMuPDF for PDFs, python-docx for DOCX files
- **Skill Extraction** — 140+ technical skills and 25+ soft skills database with regex matching
- **Section Detection** — Identifies 10 resume sections (education, experience, skills, projects, etc.)
- **Education Level Detection** — PhD → High School classification
- **Experience Estimation** — Years of experience from date ranges and explicit mentions
- **NER-based Summary** — spaCy named entity recognition for candidate and organization extraction

### 📊 ATS Scoring Engine
Rates resumes on a **0–100 scale** across 5 weighted categories:

| Category               | Weight | What's Measured                                |
|------------------------|--------|-----------------------------------------------|
| Section Completeness   | 30 pts | Presence of essential & bonus resume sections  |
| Skill Density          | 25 pts | Count of technical and soft skills detected    |
| Experience Relevance   | 20 pts | Years of experience, action verbs, and metrics |
| Formatting Quality     | 15 pts | Word count, bullet points, contact info        |
| Keyword Richness       | 10 pts | Industry action keywords                       |

### 💡 Smart Suggestions
- Prioritized (high / medium / low) improvement recommendations
- Section-specific: missing summary, skills, projects, certifications
- Content quality: action verbs, measurable achievements, word count
- Formatting: bullet points, contact info, resume length

### 🎯 Intelligent Job Matching
- **TF-IDF + Cosine Similarity** for semantic matching
- Keyword overlap scoring as secondary signal
- Combined weighted score (60% TF-IDF + 40% keyword)
- Curated dataset of 50+ job listings across multiple industries
- Human-readable match reasons with matched skill highlights

### 🎨 Modern Frontend
- Vue 3 Composition API with `<script setup>` syntax
- Dark theme with glassmorphism UI design
- Responsive sidebar navigation (collapses to icons on mobile)
- Smooth page transitions and micro-animations
- Inter font for premium typography

---

## 🛠 Tech Stack

### Frontend
| Technology       | Purpose                    |
|------------------|----------------------------|
| Vue 3            | Reactive UI framework      |
| Vue Router 4     | SPA routing & route guards |
| Vite 5           | Dev server & build tool    |
| Axios            | HTTP client                |
| Inter (Google)   | Typography                 |

### Backend (API Gateway)
| Technology         | Purpose                       |
|--------------------|-------------------------------|
| Express 4          | HTTP server framework         |
| Prisma 5           | MySQL ORM & migrations        |
| bcryptjs           | Password hashing              |
| jsonwebtoken       | JWT authentication            |
| Multer             | File upload handling          |
| Axios / form-data  | AI service communication      |
| Cloudinary (opt.)  | Cloud file storage            |

### AI Microservice
| Technology        | Purpose                         |
|-------------------|---------------------------------|
| FastAPI           | Async Python API framework      |
| PyMuPDF (fitz)    | PDF text extraction             |
| python-docx       | DOCX text extraction            |
| spaCy             | NLP & Named Entity Recognition  |
| scikit-learn      | TF-IDF vectorization & cosine similarity |
| NumPy             | Numerical computation           |
| Pydantic          | Request/response validation     |

### Database
| Technology | Purpose                |
|------------|------------------------|
| MySQL      | Relational data store  |
| Prisma     | Schema management, migrations, type-safe queries |

---

## 📁 Project Structure

```
AI Resume Analyzer + Job Matcher/
├── frontend/                      # Vue 3 SPA
│   ├── index.html                 # Entry HTML with SEO meta tags
│   ├── vite.config.js             # Vite config with API proxy
│   ├── package.json
│   └── src/
│       ├── main.js                # App bootstrap
│       ├── App.vue                # Root layout with sidebar
│       ├── router/
│       │   └── index.js           # Route definitions & auth guards
│       ├── composables/
│       │   ├── useAuth.js         # Authentication state & methods
│       │   └── useApi.js          # Axios instance with token injection
│       ├── views/
│       │   ├── LoginView.vue      # Login page
│       │   ├── RegisterView.vue   # Registration page
│       │   ├── DashboardView.vue  # Resume list & overview
│       │   ├── UploadView.vue     # Resume upload with drag & drop
│       │   ├── AnalysisView.vue   # ATS score, skills, & suggestions
│       │   └── JobsView.vue       # Job match results
│       └── assets/                # Static assets & global CSS
│
├── backend/                       # Node.js API Gateway
│   ├── server.js                  # Express app entry point
│   ├── package.json
│   ├── .env                       # Environment configuration
│   ├── middleware/
│   │   └── auth.js                # JWT verification middleware
│   ├── routes/
│   │   ├── auth.js                # Register / Login / Me endpoints
│   │   ├── resume.js              # Upload / List / Get / Delete + AI processing
│   │   └── analysis.js            # Analysis results & job match endpoints
│   ├── prisma/
│   │   ├── schema.prisma          # Database schema definition
│   │   ├── seed.js                # Database seeding script
│   │   └── migrations/            # Prisma migration history
│   └── uploads/                   # Local file storage directory
│
├── ai-service/                    # Python AI Microservice
│   ├── main.py                    # FastAPI app & endpoint definitions
│   ├── requirements.txt           # Python dependencies
│   ├── test_setup.py              # Setup verification script
│   ├── data/
│   │   └── jobs.json              # Curated job dataset (50+ listings)
│   └── utils/
│       ├── parser.py              # PDF & DOCX text extraction
│       ├── analyzer.py            # NLP skill extraction & section detection
│       ├── scorer.py              # ATS scoring algorithm (0–100)
│       ├── suggestions.py         # Actionable improvement generator
│       └── job_matcher.py         # TF-IDF cosine similarity job matching
│
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.10
- **MySQL** ≥ 8.0
- **npm** (comes with Node.js)
- **pip** (comes with Python)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-resume-analyzer.git
cd "AI Resume Analyzer + Job Matcher"
```

### 2. Set Up the Database

Create a MySQL database:

```sql
CREATE DATABASE resume_analyzer;
```

### 3. Configure the Backend

```bash
cd backend
npm install
```

Edit `.env` with your database credentials:

```env
DATABASE_URL="mysql://root:your_password@localhost:3306/resume_analyzer"
JWT_SECRET="your-secure-secret-key"
JWT_EXPIRES_IN="7d"
AI_SERVICE_URL="http://localhost:8000"
PORT=3000
```

Run Prisma setup (generates client, runs migrations, seeds data):

```bash
npm run setup
```

### 4. Set Up the AI Service

```bash
cd ../ai-service
pip install -r requirements.txt
```

*(Optional)* Install spaCy language model for enhanced NER:

```bash
python -m spacy download en_core_web_sm
```

> **Note:** spaCy is optional. All core features (skill extraction, ATS scoring, job matching) work without it. spaCy adds named entity recognition for candidate name and organization extraction in summaries.

### 5. Set Up the Frontend

```bash
cd ../frontend
npm install
```

### 6. Start All Services

Open **three terminals** and run:

```bash
# Terminal 1 — Backend API Gateway
cd backend
npm run dev                     # → http://localhost:3000

# Terminal 2 — AI Microservice
cd ai-service
uvicorn main:app --reload       # → http://localhost:8000

# Terminal 3 — Frontend Dev Server
cd frontend
npm run dev                     # → http://localhost:6756
```

Visit **http://localhost:6756** to access the application.

---

## 📡 API Reference

### Authentication

| Method | Endpoint           | Auth | Description               |
|--------|--------------------|------|---------------------------|
| POST   | `/api/auth/register` | ❌   | Register a new user        |
| POST   | `/api/auth/login`    | ❌   | Login and receive JWT      |
| GET    | `/api/auth/me`       | ✅   | Get current user profile   |

### Resume Management

| Method | Endpoint             | Auth | Description                              |
|--------|----------------------|------|------------------------------------------|
| POST   | `/api/resume/upload` | ✅   | Upload resume (PDF/DOCX) & trigger analysis |
| GET    | `/api/resume/list`   | ✅   | List all resumes for current user        |
| GET    | `/api/resume/:id`    | ✅   | Get resume with full analysis data       |
| DELETE | `/api/resume/:id`    | ✅   | Delete a resume and its associated data  |

### Analysis

| Method | Endpoint                    | Auth | Description                     |
|--------|-----------------------------|------|---------------------------------|
| GET    | `/api/analysis/:resumeId`   | ✅   | Get analysis results & skills   |
| GET    | `/api/analysis/jobs/:resumeId` | ✅ | Get job matches for a resume    |

### AI Service (Internal)

| Method | Endpoint            | Description                                |
|--------|---------------------|--------------------------------------------|
| GET    | `/`                 | Health check                               |
| POST   | `/analyze-resume`   | Full pipeline: parse → analyze → score → suggest → match |
| POST   | `/parse-resume`     | Extract text only                          |
| POST   | `/extract-skills`   | Extract skills only                        |
| POST   | `/job-match`        | Match given skills against job dataset     |

---

## 🗄 Database Schema

```
┌──────────┐       ┌──────────────┐       ┌────────────────┐
│   User   │───1:N─│    Resume    │───1:1─│ AnalysisResult │
│          │       │              │       │                │
│ id       │       │ id           │       │ atsScore       │
│ name     │       │ userId       │       │ scoreBreakdown │
│ email    │       │ fileName     │       │ sections       │
│ password │       │ fileUrl      │       │ suggestions    │
│ avatar   │       │ rawText      │       │ summary        │
└──────────┘       │ status       │       │ experienceYears│
                   └──────┬───────┘       │ educationLevel │
                          │               └────────────────┘
                     1:N  │  1:N
                 ┌────────┴────────┐
                 ▼                 ▼
           ┌──────────┐     ┌──────────┐
           │  Skill   │     │ JobMatch │
           │          │     │          │
           │ name     │     │ jobTitle │
           │ category │     │ company  │
           │ level    │     │ matchScore│
           └──────────┘     │ matchReason│
                            └──────────┘
```

---

## 🤖 AI Pipeline

The resume analysis runs through a 5-stage pipeline:

```
Upload (PDF/DOCX)
       │
       ▼
┌─────────────────┐
│  1. PARSER      │  PyMuPDF / python-docx
│  Extract Text   │  → raw text string
└────────┬────────┘
         ▼
┌─────────────────┐
│  2. ANALYZER    │  Regex + spaCy NER
│  Extract Data   │  → skills, sections, education, experience
└────────┬────────┘
         ▼
┌─────────────────┐
│  3. SCORER      │  5-category weighted algorithm
│  ATS Score      │  → 0-100 score + breakdown
└────────┬────────┘
         ▼
┌─────────────────┐
│  4. SUGGESTIONS │  Rule-based engine
│  Improve Tips   │  → prioritized action items
└────────┬────────┘
         ▼
┌─────────────────┐
│  5. JOB MATCHER │  TF-IDF + Cosine Similarity
│  Match Jobs     │  → ranked job recommendations
└─────────────────┘
```

---

## ⚙ Environment Variables

### Backend (`backend/.env`)

| Variable               | Default                                        | Description                         |
|------------------------|------------------------------------------------|-------------------------------------|
| `DATABASE_URL`         | `mysql://root:@localhost:3306/resume_analyzer`  | MySQL connection string             |
| `JWT_SECRET`           | `super-secret-jwt-key-change-in-production`     | Secret key for JWT signing          |
| `JWT_EXPIRES_IN`       | `7d`                                           | Token expiration duration           |
| `AI_SERVICE_URL`       | `http://localhost:8000`                         | URL of the FastAPI AI service       |
| `PORT`                 | `3000`                                         | Backend server port                 |
| `CLOUDINARY_CLOUD_NAME`| *(empty)*                                      | Optional Cloudinary cloud name      |
| `CLOUDINARY_API_KEY`   | *(empty)*                                      | Optional Cloudinary API key         |
| `CLOUDINARY_API_SECRET`| *(empty)*                                      | Optional Cloudinary API secret      |

---

## 📝 License

This project is for educational and portfolio purposes. Feel free to fork and modify.

---

<p align="center">
  Built with ❤️ using Vue 3, Node + Express, FastAPI & AI(Python)
</p>
