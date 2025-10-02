"""Filename and path normalisation utilities."""
from __future__ import annotations

import string
from pathlib import Path
from typing import Dict, Optional


def _clean_digits(value: Optional[str]) -> str:
    return "".join(ch for ch in (value or "") if ch.isdigit())


def _clean_acronym(value: Optional[str]) -> str:
    return "".join(ch for ch in (value or "").upper() if ch.isalnum())


def sanitize_metadata(metadata) -> Dict[str, str]:
    """Return a sanitized copy of ``metadata`` with number/acronym/year cleaned."""
    clean = dict(metadata)
    clean["number"] = _clean_digits(metadata.get("number"))
    clean["acronym"] = _clean_acronym(metadata.get("acronym"))
    clean["year"] = _clean_digits(metadata.get("year"))
    return clean


def build_target_name(metadata) -> str:
    """Return ``NUM-SIGLA-ANO.pdf`` based on ``metadata``."""
    clean = sanitize_metadata(metadata)
    number = clean.get("number")
    acronym = clean.get("acronym")
    year = clean.get("year")

    if not (number and acronym and year):
        raise ValueError("Metadados insuficientes para gerar o nome do arquivo")
    return f"{number}-{acronym}-{year}.pdf"


def ensure_destination(year: str, root: Path = Path("assets/download/informativos")) -> Path:
    """Ensure the destination folder exists and return it."""
    clean_year = _clean_digits(year)
    if not clean_year:
        raise ValueError("Ano inválido para criar destino")
    destination = root / clean_year
    destination.mkdir(parents=True, exist_ok=True)
    return destination


def ensure_unique_filename(folder: Path, filename: str) -> Path:
    """Return a unique path in ``folder`` by appending suffixes if necessary."""
    candidate = folder / filename
    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix

    for letter in string.ascii_uppercase:
        candidate = folder / f"{stem}-{letter}{suffix}"
        if not candidate.exists():
            return candidate

    counter = 1
    while True:
        candidate = folder / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1
