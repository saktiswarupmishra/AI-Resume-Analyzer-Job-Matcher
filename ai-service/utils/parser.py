"""Resume file parser — extracts text from PDF and DOCX files."""
from __future__ import annotations

# PyMuPDF changed its import name in newer versions
try:
    import fitz  # PyMuPDF < 1.24
except ImportError:
    try:
        import pymupdf as fitz  # PyMuPDF >= 1.24
    except ImportError:
        fitz = None
        print("[parser] WARNING: PyMuPDF not installed. PDF parsing will not work.")

try:
    from docx import Document
except ImportError:
    Document = None
    print("[parser] WARNING: python-docx not installed. DOCX parsing will not work.")


def extract_text(file_path: str, ext: str) -> str:
    """Extract text from a resume file."""
    ext = ext.lower()
    if ext == ".pdf":
        return _extract_pdf(file_path)
    elif ext == ".docx":
        return _extract_docx(file_path)
    else:
        raise ValueError("Unsupported file type: %s" % ext)


def _extract_pdf(file_path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    if fitz is None:
        raise ValueError("PyMuPDF is not installed. Run: pip install PyMuPDF")
    text_parts = []
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
    except Exception as e:
        raise ValueError("Failed to parse PDF: %s" % str(e))
    return "\n".join(text_parts).strip()


def _extract_docx(file_path: str) -> str:
    """Extract text from DOCX using python-docx."""
    if Document is None:
        raise ValueError("python-docx is not installed. Run: pip install python-docx")
    try:
        doc = Document(file_path)
        text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
    except Exception as e:
        raise ValueError("Failed to parse DOCX: %s" % str(e))
    return "\n".join(text_parts).strip()
