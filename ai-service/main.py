from __future__ import annotations

import os
import json
import traceback
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import tempfile

from utils.parser import extract_text
from utils.analyzer import analyze_resume_text
from utils.scorer import calculate_ats_score
from utils.suggestions import generate_suggestions
from utils.job_matcher import match_jobs

app = FastAPI(title="AI Resume Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "ok", "service": "AI Resume Analyzer"}


@app.post("/analyze-resume")
async def analyze_resume(file: UploadFile = File(...)):
    """Full pipeline: parse -> extract -> score -> suggest -> match jobs."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    try:
        # Save temp file
        suffix = ext
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # 1. Extract text
        raw_text = extract_text(tmp_path, ext)
        if not raw_text or len(raw_text.strip()) < 50:
            raise HTTPException(status_code=422, detail="Could not extract meaningful text from the resume.")

        # 2. Analyze (NLP)
        analysis = analyze_resume_text(raw_text)

        # 3. Calculate ATS score
        score_result = calculate_ats_score(raw_text, analysis)

        # 4. Generate suggestions
        suggestions = generate_suggestions(raw_text, analysis, score_result)

        # 5. Match jobs
        job_matches = match_jobs(analysis.get("skills", []))

        # Cleanup
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

        return {
            "raw_text": raw_text[:5000],
            "ats_score": score_result["total_score"],
            "score_breakdown": score_result["breakdown"],
            "sections": analysis.get("sections", {}),
            "skills": analysis.get("skills", []),
            "summary": analysis.get("summary", ""),
            "experience_years": analysis.get("experience_years", 0),
            "education_level": analysis.get("education_level", ""),
            "suggestions": suggestions,
            "job_matches": job_matches,
        }

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    """Just extract text from a resume file."""
    ext = os.path.splitext(file.filename)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    raw_text = extract_text(tmp_path, ext)
    try:
        os.unlink(tmp_path)
    except Exception:
        pass
    return {"raw_text": raw_text}


@app.post("/extract-skills")
async def extract_skills(file: UploadFile = File(...)):
    """Extract skills from a resume file."""
    ext = os.path.splitext(file.filename)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    raw_text = extract_text(tmp_path, ext)
    analysis = analyze_resume_text(raw_text)
    try:
        os.unlink(tmp_path)
    except Exception:
        pass
    return {"skills": analysis.get("skills", [])}


class JobMatchRequest(BaseModel):
    skills: List[str]
    role: Optional[str] = None


@app.post("/job-match")
async def job_match(request: JobMatchRequest):
    """Match given skills against job dataset."""
    skill_dicts = [{"name": s, "category": "technical"} for s in request.skills]
    matches = match_jobs(skill_dicts, target_role=request.role)
    return {"job_matches": matches}
