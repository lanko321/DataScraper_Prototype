"""
Browser-based fallback for eProstor using Playwright.

Demonstrates how to automate an official viewer when no public API is available.
Currently opens a test page and returns demo parcel data.
"""

import logging
from typing import Any, Dict, Optional

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)
TEST_URL = "https://www.google.com"  # Placeholder target to verify Playwright works


def fetch_parcel_data_browser(address: Optional[str] = None, parcel: Optional[str] = None) -> Dict[str, Any]:
    """
    Demo browser-based fallback for eProstor.
    In a real integration, this would navigate to the official eProstor viewer and scrape parcel data.
    """
    browser = None
    context = None
    page = None
    try:
        with sync_playwright() as p:
            # In a full integration, navigate to the official eProstor viewer and scrape parcel details.
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(TEST_URL, wait_until="domcontentloaded", timeout=15000)
            page_title = page.title()
            # Intentionally return empty parcel fields so the AI treats this as
            # "no parcel data available" instead of exposing technical IDs.
            return {
                "parcel_id": "",
                "ko": "",
                "namenska_raba": "",
                "area_m2": None,
                "other": f"Advanced browser lookup (demo) used. Page title: {page_title}. Parcel details were not available.",
                "address_query": address,
                "parcel_query": parcel,
            }
    except Exception as exc:  # pragma: no cover - runtime/browser errors
        logger.warning("Browser fallback error: %s", exc)
        # Intentionally return empty parcel fields so the AI treats this as missing data.
        return {
            "parcel_id": "",
            "ko": "",
            "namenska_raba": "",
            "area_m2": None,
            "other": "Advanced browser lookup (demo) failed. Parcel details are not available.",
            "address_query": address,
            "parcel_query": parcel,
        }
    finally:
        try:
            if page:
                page.close()
        except Exception:
            pass
        try:
            if context:
                context.close()
        except Exception:
            pass
        try:
            if browser:
                browser.close()
        except Exception:
            pass


