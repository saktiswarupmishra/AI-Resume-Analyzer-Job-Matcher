"""Resume analyzer — NLP-based skill extraction, section detection, and experience parsing."""
from __future__ import annotations

import re
from typing import Any, Dict, List

# Try to load spaCy; fall back gracefully
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    HAS_SPACY = True
    print("[analyzer] spaCy loaded successfully (en_core_web_sm)")
except Exception as e:
    HAS_SPACY = False
    nlp = None
    print("[analyzer] spaCy not available (%s)" % str(e))
    print("[analyzer] This is NORMAL on Python 3.14 — all features work without spaCy (NER-based name/org extraction disabled)")


# ── Skill databases ──────────────────────────────────────────────────────────

TECHNICAL_SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "ruby",
    "php", "swift", "kotlin", "scala", "r", "matlab", "perl", "bash", "shell",
    "html", "css", "sass", "less", "react", "angular", "vue", "vue.js", "next.js",
    "nuxt.js", "svelte", "node.js", "express", "fastapi", "flask", "django",
    "spring", "spring boot", ".net", "asp.net", "rails", "laravel",
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra",
    "sqlite", "oracle", "dynamodb", "firebase", "supabase",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
    "ci/cd", "git", "github", "gitlab", "bitbucket",
    "rest", "graphql", "grpc", "websocket", "microservices",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow",
    "pytorch", "scikit-learn", "pandas", "numpy", "opencv",
    "linux", "windows", "macos", "nginx", "apache",
    "figma", "sketch", "adobe xd", "photoshop", "illustrator",
    "jira", "confluence", "slack", "trello", "notion",
    "agile", "scrum", "kanban", "devops", "sre",
    "power bi", "tableau", "excel", "data analysis", "data science",
    "blockchain", "web3", "solidity", "ethereum",
    "react native", "flutter", "ionic", "android", "ios",
    "prisma", "sequelize", "typeorm", "mongoose", "hibernate",
}

SOFT_SKILLS = {
    "communication", "leadership", "teamwork", "problem solving", "critical thinking",
    "time management", "adaptability", "creativity", "collaboration", "mentoring",
    "project management", "strategic planning", "decision making", "negotiation",
    "presentation", "public speaking", "conflict resolution", "empathy",
    "analytical thinking", "attention to detail", "self-motivated", "initiative",
    "customer service", "interpersonal skills", "organizational skills",
}

# ── Section patterns ─────────────────────────────────────────────────────────

SECTION_PATTERNS: Dict[str, str] = {
    "education": r"(?i)\b(education|academic|qualification|degree|university|college|school)\b",
    "experience": r"(?i)\b(experience|employment|work\s*history|professional\s*experience|career)\b",
    "skills": r"(?i)\b(skills|technologies|tech\s*stack|competencies|proficiencies)\b",
    "projects": r"(?i)\b(projects|portfolio|personal\s*projects|notable\s*projects)\b",
    "certifications": r"(?i)\b(certifications?|licenses?|accreditations?)\b",
    "summary": r"(?i)\b(summary|objective|profile|about\s*me|career\s*summary)\b",
    "contact": r"(?i)\b(contact|email|phone|address|linkedin|github)\b",
    "awards": r"(?i)\b(awards?|honors?|achievements?|recognition)\b",
    "publications": r"(?i)\b(publications?|papers?|research)\b",
    "languages": r"(?i)\b(languages?|spoken\s*languages?)\b",
}

# ── Education level detection ────────────────────────────────────────────────

EDUCATION_LEVELS: List[tuple] = [
    ("phd", r"(?i)\b(ph\.?d|doctor|doctorate)\b"),
    ("masters", r"(?i)\b(master|m\.?s\.?|m\.?a\.?|mba|m\.?tech|m\.?sc)\b"),
    ("bachelors", r"(?i)\b(bachelor|b\.?s\.?|b\.?a\.?|b\.?tech|b\.?sc|b\.?e\.?|undergraduate)\b"),
    ("associate", r"(?i)\b(associate|diploma|a\.?s\.?|a\.?a\.?)\b"),
    ("high_school", r"(?i)\b(high\s*school|secondary|hsc|ssc|12th|10th)\b"),
]


def analyze_resume_text(text: str) -> Dict[str, Any]:
    """Analyze resume text and extract structured information."""
    result: Dict[str, Any] = {
        "skills": [],
        "sections": {},
        "summary": "",
        "experience_years": 0,
        "education_level": "",
    }

    text_lower = text.lower()

    # ── Extract skills ────────────────────────────────────────────────────
    found_skills: List[Dict[str, str]] = []

    for skill in TECHNICAL_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found_skills.append({
                "name": skill.title() if len(skill) > 3 else skill.upper(),
                "category": "technical",
                "level": _infer_skill_level(skill, text_lower),
            })

    for skill in SOFT_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found_skills.append({
                "name": skill.title(),
                "category": "soft",
                "level": "intermediate",
            })

    result["skills"] = found_skills

    # ── Detect sections ───────────────────────────────────────────────────
    sections_found: Dict[str, bool] = {}
    for section, pattern in SECTION_PATTERNS.items():
        if re.search(pattern, text):
            sections_found[section] = True
        else:
            sections_found[section] = False
    result["sections"] = sections_found

    # ── Detect education level ────────────────────────────────────────────
    for level, pattern in EDUCATION_LEVELS:
        if re.search(pattern, text):
            result["education_level"] = level
            break

    # ── Estimate experience years ─────────────────────────────────────────
    result["experience_years"] = _estimate_experience_years(text)

    # ── Generate summary using spaCy NER ──────────────────────────────────
    if HAS_SPACY and nlp:
        try:
            doc = nlp(text[:50000])  # limit for performance
            entities: Dict[str, List[str]] = {}
            for ent in doc.ents:
                label = ent.label_
                if label not in entities:
                    entities[label] = []
                if ent.text not in entities[label] and len(entities[label]) < 5:
                    entities[label].append(ent.text)

            name = entities.get("PERSON", [""])[0]
            orgs = entities.get("ORG", [])
            summary_parts: List[str] = []
            if name:
                summary_parts.append(f"Candidate: {name}.")
            if result["education_level"]:
                summary_parts.append(f"Education: {result['education_level'].replace('_', ' ').title()}.")
            if result["experience_years"]:
                summary_parts.append(f"~{result['experience_years']} years of experience.")
            if len(found_skills) > 0:
                top = [s["name"] for s in found_skills[:8]]
                summary_parts.append(f"Key skills: {', '.join(top)}.")
            if orgs:
                summary_parts.append(f"Organizations: {', '.join(orgs[:3])}.")
            result["summary"] = " ".join(summary_parts)
        except Exception:
            # Fall through to fallback if spaCy fails
            pass

    # Fallback summary (also used if spaCy summary is empty)
    if not result["summary"]:
        parts: List[str] = []
        if result["education_level"]:
            parts.append(f"Education: {result['education_level'].replace('_', ' ').title()}.")
        if result["experience_years"]:
            parts.append(f"~{result['experience_years']} years of experience.")
        if found_skills:
            top = [s["name"] for s in found_skills[:8]]
            parts.append(f"Key skills: {', '.join(top)}.")
        result["summary"] = " ".join(parts)

    return result


def _infer_skill_level(skill: str, text_lower: str) -> str:
    """Heuristic skill-level inference based on contextual clues."""
    advanced_clues = ["expert", "advanced", "lead", "senior", "architect", "principal", "5+ years", "extensive"]
    beginner_clues = ["beginner", "basic", "familiar", "learning", "exposure", "introductory"]

    for clue in advanced_clues:
        if clue in text_lower and skill in text_lower:
            return "advanced"
    for clue in beginner_clues:
        if clue in text_lower and skill in text_lower:
            return "beginner"
    return "intermediate"


def _estimate_experience_years(text: str) -> float:
    """Estimate total years of experience from text."""
    # Look for patterns like "5 years", "3+ years", "2019-2024"
    year_mentions = re.findall(r"(\d+)\+?\s*(?:years?|yrs?)", text, re.IGNORECASE)
    if year_mentions:
        return max(float(y) for y in year_mentions)

    # Try date range estimation
    years = re.findall(r"\b(20\d{2}|19\d{2})\b", text)
    if len(years) >= 2:
        years_int = sorted(set(int(y) for y in years))
        return float(years_int[-1] - years_int[0])

    return 0
