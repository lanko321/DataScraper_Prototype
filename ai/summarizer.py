"""
AI summariser for parcel/zoning data.

Builds a structured summary (parcel, building, zoning, regulations, summary, sources)
via a Cloudflare Worker proxy or a local demo pathway.
"""

import os
import logging
from typing import Any, Dict, List

import requests
from flask import session

CF_WORKER_PROXY_URL = os.getenv("CF_WORKER_PROXY_URL", "")
logger = logging.getLogger(__name__)


def _safe(value: Any, default: str = "—") -> str:
    return default if value is None or value == "" else str(value)


def _build_demo_summary(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build the demo summary derived from raw_data."""
    parcel = raw_data.get("parcel", {}) or {}
    zoning = raw_data.get("zoning", {}) or {}
    regulations: List[Dict[str, Any]] = raw_data.get("regulations", []) or []

    parcel_id = _safe(parcel.get("parcel_id"))
    ko = _safe(parcel.get("ko"))
    raba = _safe(parcel.get("namenska_raba"))
    area = _safe(parcel.get("area_m2"), "neznano")

    zone_name = _safe(zoning.get("zone_name"))
    layers = zoning.get("layers", []) or []
    layer_count = len(layers)

    parcel_short = f"Parcela {parcel_id} v {ko} (namenska raba: {raba})."
    parcel_long = (
        f"Parcela {parcel_id} v {ko}, namensko območje: {raba}. "
        f"Površina: {area} m². Dodatno: {_safe(parcel.get('other'))}."
    )

    if raba != "—":
        building_short = f"Vrsta pozidave: {raba}."
        building_long = f"Na parceli {parcel_id} je predvidena raba '{raba}'. Podrobnejša analiza bo vključena pozneje."
    else:
        building_short = "Vrsta pozidave: podatki niso na voljo."
        building_long = f"Parcela {parcel_id} nima razpoložljivih podatkov o namenski rabi."

    zoning_short = f"Območje: {zone_name}; št. slojev: {layer_count}."
    zoning_long = (
        f"Območje {zone_name} vključuje {layer_count} slojev: {', '.join(layers) if layers else 'brez seznama'}. "
        f"Referenca na parcelo: {parcel_id}."
    )

    regs_section = []
    for reg in regulations:
        law = _safe(reg.get("law"))
        article = _safe(reg.get("article"))
        snippet = _safe(reg.get("snippet"))
        short = f"{law} (čl. {article}): {snippet}"
        long = f"{law} (člen {article}): {snippet}. Vir: PISRS."
        regs_section.append(
            {
                "law": law,
                "short": short,
                "long": long,
                "source": "PISRS",
            }
        )

    summary_short = (
        f"Parcela {parcel_id} ({raba}); območje {zone_name} z {layer_count} sloji."
    )
    summary_long = (
        f"Parcela {parcel_id} v {ko}, namenska raba {raba}, površina {area} m². "
        f"Zoniranje: {zone_name}, sloji: {', '.join(layers) if layers else '—'}. "
        "Priporočamo pregled podrobnih določil in slojev."
    )

    return {
        "parcel_section": {"short": parcel_short, "long": parcel_long},
        "zoning_section": {"short": zoning_short, "long": zoning_long},
        "regulations_section": regs_section,
        "summary_section": {"short": summary_short, "long": summary_long},
        "building_section": {"short": building_short, "long": building_long},
        "sources": ["eProstor", "PISRS", "Urbinfo"],
    }


def summarize_via_proxy(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Use the Cloudflare Worker proxy when CF_WORKER_PROXY_URL is provided; fall back to local build on error."""
    if not CF_WORKER_PROXY_URL or not CF_WORKER_PROXY_URL.strip():
        logger.info("Proxy URL not configured; using demo summariser.")
        return _build_demo_summary(raw_data)

    try:
        resp = requests.post(
            CF_WORKER_PROXY_URL,
            json={"raw_data": raw_data},
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json()
        logger.warning("Proxy status %s, falling back to demo.", resp.status_code)
        return _build_demo_summary(raw_data)
    except Exception as exc:  # pragma: no cover - network/parse errors
        logger.warning("Proxy call failed: %s, falling back to demo.", exc)
        return _build_demo_summary(raw_data)


def summarize_with_local_key(raw_data: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    """
    Placeholder for future direct OpenAI call using user-provided key.
    TODO: Use api_key with OpenAI SDK to produce structured summary.
    """
    _ = api_key
    return _build_demo_summary(raw_data)


def summarize(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry point used by Flask: choose between user-provided key (future path) and proxy.
    Always returns the same structured dict schema.
    """
    user_key = session.get("user_openai_key")
    if user_key:
        return summarize_with_local_key(raw_data, user_key)
    return summarize_via_proxy(raw_data)


