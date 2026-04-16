"""Quick test — run this to check if the AI service can start."""
import sys
print("Python version:", sys.version)

errors = []

# Test 1: FastAPI
try:
    import fastapi
    print("[OK] fastapi %s" % fastapi.__version__)
except ImportError:
    errors.append("fastapi NOT installed. Run: pip install fastapi")
    print("[FAIL] fastapi")

# Test 2: Uvicorn
try:
    import uvicorn
    print("[OK] uvicorn")
except ImportError:
    errors.append("uvicorn NOT installed. Run: pip install uvicorn[standard]")
    print("[FAIL] uvicorn")

# Test 3: PyMuPDF
try:
    import fitz
    print("[OK] PyMuPDF (fitz) %s" % fitz.__doc__[:30] if fitz.__doc__ else "[OK] PyMuPDF")
except ImportError:
    try:
        import pymupdf
        print("[OK] PyMuPDF (pymupdf)")
    except ImportError:
        errors.append("PyMuPDF NOT installed. Run: pip install PyMuPDF")
        print("[FAIL] PyMuPDF")

# Test 4: python-docx
try:
    from docx import Document
    print("[OK] python-docx")
except ImportError:
    errors.append("python-docx NOT installed. Run: pip install python-docx")
    print("[FAIL] python-docx")

# Test 5: spaCy (optional — incompatible with Python 3.14+)
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    print("[OK] spacy + en_core_web_sm")
except ImportError:
    print("[WARN] spacy not installed — AI service will work in fallback mode (regex-based extraction)")
except OSError:
    print("[WARN] spacy installed but en_core_web_sm model missing — AI service will work in fallback mode")
except Exception as e:
    print("[WARN] spacy failed to load (%s) — this is expected on Python 3.14+" % type(e).__name__)
    print("       AI service will work perfectly in fallback mode (all features except NER-based name extraction)")

# Test 6: scikit-learn
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    print("[OK] scikit-learn")
except ImportError:
    errors.append("scikit-learn NOT installed. Run: pip install scikit-learn")
    print("[WARN] scikit-learn missing (job matching will use keyword-only fallback)")

# Test 7: Jobs data
import os
jobs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "jobs.json")
if os.path.exists(jobs_path):
    import json
    with open(jobs_path, "r") as f:
        jobs = json.load(f)
    print("[OK] jobs.json loaded (%d jobs)" % len(jobs))
else:
    errors.append("jobs.json not found at: %s" % jobs_path)
    print("[FAIL] jobs.json not found")

# Test 8: python-multipart (required by FastAPI for file uploads)
try:
    import multipart
    print("[OK] python-multipart")
except ImportError:
    errors.append("python-multipart NOT installed. Run: pip install python-multipart")
    print("[FAIL] python-multipart")

print("\n" + "=" * 50)
if errors:
    print("ISSUES FOUND (%d):" % len(errors))
    for e in errors:
        print("  - %s" % e)
    print("\nFix these and run this test again.")
else:
    print("ALL CHECKS PASSED! You can start the service:")
    print("  uvicorn main:app --reload --port 8000")
