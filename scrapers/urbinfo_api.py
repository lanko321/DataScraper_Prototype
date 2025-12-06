"""
Urbinfo / zoning stub.

Currently returns demo zoning info and layers based on a parcel reference.
Intended to be replaced with a real municipal GIS/Urbinfo integration.
"""

from typing import Any, Dict


def fetch_zoning_layers(parcel_or_geometry: Dict[str, Any]) -> Dict[str, Any]:
    """Return dummy zoning data for the prototype pipeline."""
    # TODO: Replace with real WFS/WMS/REST queries for zoning and thematic layers.
    return {
        "zone_name": "SSse – Stanovanjska območja",
        "layers": ["Kulturna dediščina (demo)", "Poplavno območje (demo)"],
        "parcel_ref": parcel_or_geometry.get("parcel_id"),
    }


