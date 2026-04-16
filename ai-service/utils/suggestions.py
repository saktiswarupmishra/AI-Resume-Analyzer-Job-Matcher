"""AI suggestion generator — produces actionable resume improvement tips."""
from __future__ import annotations

import re
import os
from typing import Any, Dict, List


def generate_suggestions(raw_text: str, analysis: Dict[str, Any], score: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate improvement suggestions based on analysis and score."""
    suggestions: List[Dict[str, str]] = []
    sections = analysis.get("sections", {})
    skills = analysis.get("skills", [])
    breakdown = score.get("breakdown", {})
    text_lower = raw_text.lower()

    # ── Section-based suggestions ─────────────────────────────────────────
    if not sections.get("summary"):
        suggestions.append({
            "type": "section",
            "priority": "high",
            "title": "Add a Professional Summary",
            "description": "Include a 2-3 sentence professional summary at the top of your resume. This helps recruiters quickly understand your profile and is critical for ATS systems.",
        })

    if not sections.get("skills"):
        suggestions.append({
            "type": "section",
            "priority": "high",
            "title": "Add a Dedicated Skills Section",
            "description": "Create a clearly labeled 'Skills' section listing your technical and soft skills. ATS systems scan for this section specifically.",
        })

    if not sections.get("projects"):
        suggestions.append({
            "type": "section",
            "priority": "medium",
            "title": "Include Projects Section",
            "description": "Add a 'Projects' section to showcase practical applications of your skills. Include project name, technologies used, and measurable outcomes.",
        })

    if not sections.get("certifications"):
        suggestions.append({
            "type": "section",
            "priority": "low",
            "title": "Consider Adding Certifications",
            "description": "Relevant certifications (AWS, Google Cloud, PMP, etc.) can boost your ATS score and credibility significantly.",
        })

    # ── Skill-based suggestions ───────────────────────────────────────────
    tech_skills = [s for s in skills if s.get("category") == "technical"]
    soft_skills = [s for s in skills if s.get("category") == "soft"]

    if len(tech_skills) < 5:
        suggestions.append({
            "type": "skill",
            "priority": "high",
            "title": "Add More Technical Skills",
            "description": "Only %d technical skills detected. Include specific technologies, frameworks, and tools. Aim for at least 8-12 relevant technical skills." % len(tech_skills),
        })

    if len(soft_skills) < 2:
        suggestions.append({
            "type": "skill",
            "priority": "medium",
            "title": "Include Soft Skills",
            "description": "Add soft skills like leadership, communication, and teamwork. Many job descriptions require these, and ATS systems look for them.",
        })

    # ── Content quality suggestions ───────────────────────────────────────
    action_verbs = ["achieved", "built", "created", "delivered", "designed", "developed",
                    "implemented", "improved", "launched", "led", "managed", "optimized"]
    used_verbs = sum(1 for v in action_verbs if v in text_lower)
    if used_verbs < 4:
        suggestions.append({
            "type": "content",
            "priority": "high",
            "title": "Use More Action Verbs",
            "description": "Start bullet points with strong action verbs like 'Developed', 'Implemented', 'Optimized', 'Led'. This makes your contributions clearer and more impactful.",
        })

    # Check for measurable achievements
    metrics = re.findall(r"\d+%|\$[\d,]+|\d+\+?\s*(users?|clients?|projects?|team|revenue)", text_lower)
    if len(metrics) < 2:
        suggestions.append({
            "type": "content",
            "priority": "high",
            "title": "Include Measurable Achievements",
            "description": "Add quantifiable results like 'Increased performance by 40%', 'Managed team of 8', or 'Reduced costs by $50K'. Numbers make your impact concrete.",
        })

    # Check word count
    word_count = len(raw_text.split())
    if word_count < 200:
        suggestions.append({
            "type": "formatting",
            "priority": "high",
            "title": "Resume is Too Short",
            "description": "Your resume has only ~%d words. A strong resume typically has 400-800 words. Add more detail about your experience and accomplishments." % word_count,
        })
    elif word_count > 1200:
        suggestions.append({
            "type": "formatting",
            "priority": "medium",
            "title": "Resume May Be Too Long",
            "description": "Your resume has ~%d words. Consider condensing to 1-2 pages. Focus on the most recent and relevant experience." % word_count,
        })

    # Check for email
    if not re.search(r"[\w.-]+@[\w.-]+\.\w+", raw_text):
        suggestions.append({
            "type": "contact",
            "priority": "high",
            "title": "Add Email Address",
            "description": "No email address detected. Ensure your contact information is clearly visible at the top of your resume.",
        })

    # Check for bullet points
    if not re.search(r"[•\-\*▪►]", raw_text):
        suggestions.append({
            "type": "formatting",
            "priority": "medium",
            "title": "Use Bullet Points",
            "description": "Structure your experience with bullet points instead of paragraphs. This improves readability and ATS parsing.",
        })

    # ── Score-based suggestions ───────────────────────────────────────────
    total = score.get("total_score", 0)
    if total >= 80:
        suggestions.insert(0, {
            "type": "overall",
            "priority": "info",
            "title": "Strong Resume!",
            "description": "Your ATS score is %d/100. Your resume is well-structured. Fine-tune the suggestions below to push for a perfect score." % total,
        })
    elif total >= 50:
        suggestions.insert(0, {
            "type": "overall",
            "priority": "medium",
            "title": "Good Foundation, Room for Improvement",
            "description": "Your ATS score is %d/100. Address the high-priority suggestions below to significantly improve your chances." % total,
        })
    else:
        suggestions.insert(0, {
            "type": "overall",
            "priority": "high",
            "title": "Resume Needs Significant Improvement",
            "description": "Your ATS score is %d/100. Focus on adding missing sections, more skills, and quantifiable achievements." % total,
        })

    return suggestions
