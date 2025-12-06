"""
eProstor data fetcher.

Currently returns structured demo parcel data and a placeholder HTTP path
that can be replaced with a real eProstor/WFS integration.
"""

from typing import Any, Dict, Optional

import requests


def _dummy_parcel(address: Optional[str], parcel: Optional[str]) -> Dict[str, Any]:
    return {
        "parcel_id": "1234/5",
        "ko": "123 K.O. Center",
        "namenska_raba": "SSse – Stanovanjske površine",
        "area_m2": 512,
        "other": "demo placeholder",
        "address_query": address,
        "parcel_query": parcel,
    }


def fetch_parcel_data_from_http(address: Optional[str] = None, parcel: Optional[str] = None) -> Dict[str, Any]:
    """
    Test connectivity against a public Slovenian WFS endpoint.
    This is the placeholder spot where a real eProstor/WFS call would parse live parcel data.
    """
    url = (
        "https://gis.arso.gov.si/arcgis/services/OPS/vodna_telesa/MapServer/"
        "WFSServer?service=WFS&request=GetCapabilities&version=2.0.0"
    )
    try:
        resp = requests.get(url, timeout=10)
        data = _dummy_parcel(address, parcel)
        if resp.status_code == 200:
            data["wfs_status"] = "connected"
            data["wfs_length"] = len(resp.text)
        else:
            data["wfs_status"] = f"error_status_{resp.status_code}"
            data["wfs_length"] = 0
        return data
    except Exception as exc:  # pragma: no cover - network exception path
        data = _dummy_parcel(address, parcel)
        data["wfs_status"] = f"error_status_{exc.__class__.__name__}"
        data["wfs_length"] = 0
        return data


def fetch_parcel_data(address: Optional[str] = None, parcel: Optional[str] = None) -> Dict[str, Any]:
    """Return parcel data, using HTTP test with safe fallback to dummy."""
    return fetch_parcel_data_from_http(address, parcel)


