"""Processing utilities for Informativos Builder."""
from .pdf_extract import extract_metadata
from .filename_fallback import extract_number_from_filename
from .normalizer import (
    build_target_name,
    ensure_destination,
    ensure_unique_filename,
    sanitize_metadata,
)
from .html_builder import build_li

__all__ = [
    "extract_metadata",
    "extract_number_from_filename",
    "build_target_name",
    "ensure_destination",
    "ensure_unique_filename",
    "sanitize_metadata",
    "build_li",
]
