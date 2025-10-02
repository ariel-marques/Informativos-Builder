"""Fallback helpers for deriving values from filenames."""
from __future__ import annotations

import re
from typing import Optional

NUMBER_FROM_FILENAME_PATTERN = re.compile(r".*?[^0-9](\d{1,4})$")


def extract_number_from_filename(name: str) -> Optional[str]:
    """Extract the trailing number from ``name`` if present."""
    match = NUMBER_FROM_FILENAME_PATTERN.match(name)
    if match:
        return match.group(1)
    return None
