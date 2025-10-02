"""PDF text extraction and metadata parsing helpers."""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, Optional

try:
    from PyPDF2 import PdfReader  # type: ignore
except Exception:  # pragma: no cover - handled via text extraction fallbacks
    PdfReader = None  # type: ignore

HEADER_PATTERN = re.compile(
    r"^\s*([A-Z0-9]{2,})\s*[\u2013\u2014\-]\s*([A-Za-zÀ-ÖØ-öø-ÿ\s\.'\-/&]+?)\s*/\s*(\d{4})\s*$",
    re.MULTILINE,
)
SEMESTER_PATTERN = re.compile(r"(\d)\.\s*º\s*semestre", re.IGNORECASE)
NUMBER_PATTERN = re.compile(r"N[\.ºo]*\s*[:.]?\s*(\d{1,4})\s*$", re.IGNORECASE | re.MULTILINE)

LOGGER = logging.getLogger(__name__)


def _read_pdf_text(pdf_path: Path) -> str:
    """Extract text from ``pdf_path`` using PyPDF2."""
    if PdfReader is None:
        LOGGER.warning("PyPDF2 is unavailable; cannot extract text from %s", pdf_path)
        return ""
    try:
        reader = PdfReader(str(pdf_path))
    except Exception as exc:  # pragma: no cover - depends on file corruption
        LOGGER.error("Erro ao abrir PDF %s: %s", pdf_path, exc)
        return ""

    parts = []
    for index, page in enumerate(getattr(reader, "pages", [])):
        try:
            extracted = page.extract_text() or ""
        except Exception as exc:  # pragma: no cover - depends on PyPDF2 internals
            LOGGER.error("Erro ao extrair texto da página %s de %s: %s", index, pdf_path, exc)
            extracted = ""
        parts.append(extracted)
    return "\n".join(parts)


def _normalise_whitespace(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return " ".join(value.split())


def extract_metadata(pdf_path: Path) -> Dict[str, Optional[str]]:
    """Extract metadata fields from a PDF.

    Parameters
    ----------
    pdf_path:
        Path to the PDF to inspect.

    Returns
    -------
    dict
        A dictionary with ``number``, ``acronym``, ``fullname``, ``year``, ``semester``,
        ``number_source`` (``"pdf"`` or ``"filename"`` or ``"missing"``) and ``text_extracted``
        indicating whether any textual content was extracted from the PDF.
    """

    text = _read_pdf_text(pdf_path)

    header_match = HEADER_PATTERN.search(text)
    acronym = _normalise_whitespace(header_match.group(1)) if header_match else None
    fullname = _normalise_whitespace(header_match.group(2)) if header_match else None
    year = header_match.group(3) if header_match else None

    semester_match = SEMESTER_PATTERN.search(text)
    semester = semester_match.group(1) if semester_match else "1"

    number_match = NUMBER_PATTERN.search(text)
    number = number_match.group(1) if number_match else None
    number_source = "pdf" if number else "missing"

    if not number:
        from .filename_fallback import extract_number_from_filename

        fallback = extract_number_from_filename(pdf_path.stem)
        if fallback:
            number = fallback
            number_source = "filename"

    return {
        "number": number,
        "acronym": acronym,
        "fullname": fullname,
        "year": year,
        "semester": semester,
        "number_source": number_source,
        "text_extracted": bool(text.strip()),
    }
