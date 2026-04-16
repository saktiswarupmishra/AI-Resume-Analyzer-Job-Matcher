"""Job matching engine — uses TF-IDF cosine similarity to match resume skills with jobs."""
from __future__ import annotations

import os
import json
from typing import Any, Dict, List, Optional

# Lazy import sklearn — only when needed
_vectorizer_available = False
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    _vectorizer_available = True
except ImportError:
    print("[job_matcher] scikit-learn not available, falling back to keyword-only matching")


# Load job dataset — use absolute path based on this file's location
_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
_JOBS_PATH = os.path.join(_DATA_DIR, "jobs.json")


def _load_jobs() -> List[Dict[str, Any]]:
    try:
        with open(_JOBS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[job_matcher] Failed to load jobs.json: {e}")
        print(f"[job_matcher] Looked at path: {_JOBS_PATH}")
        return []


def match_jobs(
    skills: List[Dict[str, str]],
    target_role: Optional[str] = None,
    top_n: int = 10,
) -> List[Dict[str, Any]]:
    """Match extracted skills against the job dataset."""
    jobs = _load_jobs()
    if not jobs or not skills:
        return []

    # Build skill string
    skill_names = [s.get("name", "").lower() for s in skills]
    resume_text = " ".join(skill_names)
    if target_role:
        resume_text += " " + target_role.lower()

    # Filter by role if specified
    if target_role:
        role_lower = target_role.lower()
        filtered = [j for j in jobs if role_lower in j.get("title", "").lower() or role_lower in j.get("category", "").lower()]
        if filtered:
            jobs = filtered

    if _vectorizer_available:
        return _match_with_tfidf(skill_names, resume_text, jobs, top_n)
    else:
        return _match_with_keywords(skill_names, jobs, top_n)


def _match_with_tfidf(
    skill_names: List[str],
    resume_text: str,
    jobs: List[Dict[str, Any]],
    top_n: int,
) -> List[Dict[str, Any]]:
    """TF-IDF + Cosine Similarity matching."""
    # Build job texts for TF-IDF
    job_texts: List[str] = []
    for job in jobs:
        parts = [
            job.get("title", ""),
            job.get("description", ""),
            " ".join(job.get("required_skills", [])),
            job.get("category", ""),
        ]
        job_texts.append(" ".join(parts).lower())

    # TF-IDF Vectorization + Cosine Similarity
    all_texts = [resume_text] + job_texts
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Combine with keyword overlap
    results: List[Dict[str, Any]] = []
    for i, job in enumerate(jobs):
        required = [s.lower() for s in job.get("required_skills", [])]
        overlap = sum(1 for s in skill_names if any(s in r or r in s for r in required))
        keyword_score = overlap / max(len(required), 1)
        combined_score = (similarities[i] * 0.6 + keyword_score * 0.4) * 100

        if combined_score > 5:
            results.append(_build_result(job, combined_score, skill_names, required))

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:top_n]


def _match_with_keywords(
    skill_names: List[str],
    jobs: List[Dict[str, Any]],
    top_n: int,
) -> List[Dict[str, Any]]:
    """Fallback keyword-only matching when sklearn is unavailable."""
    results: List[Dict[str, Any]] = []
    for job in jobs:
        required = [s.lower() for s in job.get("required_skills", [])]
        overlap = sum(1 for s in skill_names if any(s in r or r in s for r in required))
        keyword_score = (overlap / max(len(required), 1)) * 100

        if keyword_score > 5:
            results.append(_build_result(job, keyword_score, skill_names, required))

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:top_n]


def _build_result(
    job: Dict[str, Any],
    score: float,
    skill_names: List[str],
    required: List[str],
) -> Dict[str, Any]:
    return {
        "title": job.get("title", ""),
        "company": job.get("company", ""),
        "location": job.get("location", ""),
        "description": job.get("description", ""),
        "required_skills": job.get("required_skills", []),
        "match_score": round(score, 1),
        "match_reason": _build_match_reason(skill_names, required),
        "url": job.get("url", ""),
        "salary": job.get("salary", ""),
        "category": job.get("category", ""),
    }


def _build_match_reason(resume_skills: List[str], job_skills: List[str]) -> str:
    """Build a human-readable match reason."""
    matched = [s for s in resume_skills if any(s in j or j in s for j in job_skills)]
    if matched:
        return "Matched skills: " + ", ".join(set(s.title() for s in matched[:6]))
    return "Matched based on overall profile similarity"
