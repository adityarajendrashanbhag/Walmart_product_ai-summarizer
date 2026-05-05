"""Domain utilities for review-text normalization and cleanup."""

import re
import unicodedata


def clean_review_text(text: str) -> str:
    """Normalize a raw review string into a simple ASCII-safe text form."""

    if not isinstance(text, str):
        return ""

    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"[^A-Za-z0-9' ]+", " ", text)
    text = re.sub(r"\B'|'(?!\w)", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
