"""
Helpers for normalising address and parcel input.

Normalisation makes user input more robust for downstream HTTP or scraping calls.
"""

import re
from typing import Optional, Tuple


def _capitalize_segment(segment: str) -> str:
    """Capitalize a word segment, preserving hyphen-separated parts."""
    parts = []
    for part in segment.split("-"):
        if not part:
            parts.append(part)
            continue
        parts.append(part[0].upper() + part[1:].lower())
    return "-".join(parts)


def _title_phrase(text: str) -> str:
    """Title-case words while preserving commas and hyphens."""
    pieces = []
    for piece in text.split(","):
        cleaned = " ".join(piece.strip().split())
        words = [_capitalize_segment(w) for w in cleaned.split(" ") if w]
        pieces.append(" ".join(words))
    return ", ".join(pieces)


def normalize_address(address: Optional[str]) -> str:
    """
    Normalize address: trim/collapse spaces, insert comma before city when missing,
    and title-case words. Simple by design; extend if needed.
    """
    if not address:
        return ""

    text = " ".join(address.strip().split())
    # Normalize comma spacing if already present.
    text = re.sub(r"\s*,\s*", ", ", text)

    if "," not in text:
        tokens = text.split(" ")
        city_start = None
        for idx, token in enumerate(tokens):
            if any(ch.isdigit() for ch in token):
                if idx + 1 < len(tokens):
                    city_start = idx + 1
                break
        if city_start is not None:
            street_part = " ".join(tokens[:city_start])
            city_part = " ".join(tokens[city_start:])
            text = f"{street_part}, {city_part}"

    return _title_phrase(text)


def normalize_parcel(parcel: Optional[str]) -> str:
    """
    Normalize parcel: trim/collapse spaces, tighten slash spacing,
    standardize 'k.o.', and capitalize words. Extend for locale-specific rules.
    """
    if not parcel:
        return ""

    text = " ".join(parcel.strip().split())
    text = re.sub(r"\s*/\s*", "/", text)
    text = re.sub(r"\bk\.?o\.?\b", "k.o.", text, flags=re.IGNORECASE)
    # Ensure a space before k.o.
    text = re.sub(r"\s*(k\.o\.)", r" \1", text)
    text = " ".join(text.strip().split())

    tokens = []
    for tok in text.split(" "):
        if tok.lower() == "k.o.":
            tokens.append("k.o.")
        else:
            tokens.append(_capitalize_segment(tok))
    return " ".join(tokens)


def normalize_inputs(address: Optional[str], parcel: Optional[str]) -> Tuple[str, str]:
    return normalize_address(address), normalize_parcel(parcel)


