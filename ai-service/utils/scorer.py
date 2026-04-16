"""ATS scoring algorithm — rates resumes on a 0-100 scale."""
from __future__ import annotations

import re
from typing import Any, Dict


def calculate_ats_score(raw_text: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate ATS compatibility score with section-wise breakdown."""
    breakdown: Dict[str, Any] = {}
    text_lower = raw_text.lower()

    # ── 1. Section completeness (30 pts) ──────────────────────────────────
    sections = analysis.get("sections", {})
    essential = ["contact", "education", "experience", "skills"]
    bonus = ["summary", "projects", "certifications"]

    essential_found = sum(1 for s in essential if sections.get(s, False))
    bonus_found = sum(1 for s in bonus if sections.get(s, False))

    section_score = min(30, (essential_found / len(essential)) * 22 + (bonus_found / len(bonus)) * 8)
    breakdown["section_completeness"] = {
        "score": round(section_score),
        "max": 30,
        "detail": f"{essential_found}/{len(essential)} essential, {bonus_found}/{len(bonus)} bonus sections",
    }

    # ── 2. Skill density (25 pts) ─────────────────────────────────────────
    skills = analysis.get("skills", [])
    tech_count = sum(1 for s in skills if s.get("category") == "technical")
    soft_count = sum(1 for s in skills if s.get("category") == "soft")

    skill_score = min(25, tech_count * 1.5 + soft_count * 1.0)
    breakdown["skill_density"] = {
        "score": round(skill_score),
        "max": 25,
        "detail": f"{tech_count} technical, {soft_count} soft skills",
    }

    # ── 3. Experience relevance (20 pts) ──────────────────────────────────
    exp_years = analysis.get("experience_years", 0)
    has_action_verbs = _count_action_verbs(text_lower)
    has_metrics = len(re.findall(r"\d+%|\$\d+|\d+\+?\s*(users?|clients?|projects?|team)", text_lower))

    exp_score = min(20, (min(exp_years, 10) / 10) * 10 + min(has_action_verbs, 10) * 0.5 + min(has_metrics, 5) * 1.0)
    breakdown["experience_relevance"] = {
        "score": round(exp_score),
        "max": 20,
        "detail": f"{exp_years} years, {has_action_verbs} action verbs, {has_metrics} metrics",
    }

    # ── 4. Formatting quality (15 pts) ────────────────────────────────────
    formatting_score = 15
    word_count = len(raw_text.split())
    line_count = len(raw_text.strip().split("\n"))

    if word_count < 150:
        formatting_score -= 5
    if word_count > 1500:
        formatting_score -= 3
    if not re.search(r"[•\-\*▪]", raw_text):
        formatting_score -= 2
    if not re.search(r"[\w.-]+@[\w.-]+", raw_text):
        formatting_score -= 3
    if not re.search(r"[\+]?\d[\d\-\s]{8,}", raw_text):
        formatting_score -= 2

    formatting_score = max(0, formatting_score)
    breakdown["formatting"] = {
        "score": round(formatting_score),
        "max": 15,
        "detail": f"{word_count} words, {line_count} lines",
    }

    # ── 5. Keyword richness (10 pts) ──────────────────────────────────────
    industry_keywords = [
        "managed", "developed", "implemented", "designed", "led", "optimized",
        "analyzed", "collaborated", "delivered", "achieved", "improved", "reduced",
        "responsible", "contributed", "maintained", "built", "created", "automated",
    ]
    kw_count = sum(1 for kw in industry_keywords if kw in text_lower)
    keyword_score = min(10, kw_count * 0.8)
    breakdown["keyword_richness"] = {
        "score": round(keyword_score),
        "max": 10,
        "detail": f"{kw_count}/{len(industry_keywords)} action keywords",
    }

    # ── Total ─────────────────────────────────────────────────────────────
    total = round(sum(v["score"] for v in breakdown.values()))
    total = min(100, max(0, total))

    return {
        "total_score": total,
        "breakdown": breakdown,
    }


def _count_action_verbs(text: str) -> int:
    """Count strong action verbs in the text."""
    verbs = [
        "achieved", "built", "created", "delivered", "designed", "developed",
        "established", "generated", "implemented", "improved", "launched",
        "led", "managed", "optimized", "orchestrated", "pioneered",
        "reduced", "resolved", "spearheaded", "streamlined", "transformed",
    ]
    return sum(1 for v in verbs if v in text)
