"""
PISRS scraper for legal regulations (GZ-1, Uredba o razvrščanju objektov).

Fetches HTML from PISRS pages and extracts short text snippets for AI input.
"""

import re
from typing import Any, Dict, List

import requests

PISRS_URLS = {
    "GZ-1": "https://pisrs.si/pregledPredpisa?id=ZAKO8244",
    "Uredba o razvrščanju objektov": "https://pisrs.si/pregledPredpisa?id=URED8497",
}


def _fetch_snippet(url: str, max_len: int = 400) -> str:
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return "Povzetek ni na voljo (napaka pri dostopu na PISRS)."
        html = resp.text or ""
        text = re.sub(r"<[^>]+>", " ", html)

        idx = text.find("function ()")
        if idx != -1:
            text = text[:idx]

        text = re.sub(r"\s+", " ", text).strip()

        for key in ["Gradbeni zakon", "Uredba o razvrščanju objektov"]:
            k_idx = text.find(key)
            if k_idx != -1:
                text = text[k_idx:]
                break

        # Cleaning is intentionally simple; production would parse articles/sections more precisely.
        if not text:
            return "Kratek povzetek trenutno ni na voljo."

        snippet = text[:max_len]
        if len(text) > max_len:
            snippet += "…"
        return snippet
    except Exception as exc:  # pragma: no cover - network/parse errors
        return f"Povzetek ni na voljo (napaka: {exc.__class__.__name__})."


def fetch_regulations(raw_parcel_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    demo_regs = [
        {"law": "GZ-1", "article": "16", "snippet": "Postopki za gradnjo objektov (demo)."},
        {"law": "Uredba o razvrščanju objektov", "article": "3", "snippet": "Razvrstitev objektov (demo)."},
    ]

    regs: List[Dict[str, Any]] = []
    try:
        for law_name, url in PISRS_URLS.items():
            snippet = _fetch_snippet(url)
            regs.append({"law": law_name, "article": "—", "snippet": snippet})
        return regs
    except Exception as exc:  # pragma: no cover - network/parse errors
        print(f"[pisrs_api] Error fetching PISRS, using demo regs. {exc}")
        return demo_regs


