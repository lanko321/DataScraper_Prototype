"""
Flask web app for parcel & zoning pre-check.

Orchestrates input normalization, data fetchers (eProstor/PISRS/Urbinfo stubs),
and AI summarisation via a Cloudflare Worker proxy.
"""

import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from flask import Flask, Response, redirect, render_template, request, session, url_for

from utils.input_normalization import normalize_address, normalize_parcel
from ai import summarizer
from scrapers.eprostor_api import fetch_parcel_data
from scrapers.eprostor_browser import fetch_parcel_data_browser
from scrapers.pisrs_api import fetch_regulations
from scrapers.urbinfo_api import fetch_zoning_layers

# Load environment variables early; prototype-level configuration.
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")


def build_report_text(ai_summary: Dict[str, Any]) -> str:
    """Build a plain-text report based on the AI summary."""
    parcel_text = ai_summary.get("parcel_section", {}).get("short", "—")
    building_section = ai_summary.get("building_section") or {}
    building_text = building_section.get("short") or "Podatki o vrsti pozidave niso na voljo."
    zoning_text = ai_summary.get("zoning_section", {}).get("short", "—")
    summary_text = ai_summary.get("summary_section", {}).get("short", "—")

    regs = ai_summary.get("regulations_section") or []
    regs_lines = [f"- {r.get('law', '—')}: {r.get('short', '—')}" for r in regs] or ["- Ni navedenih predpisov."]

    parts = [
        "Lokacija / parcela:",
        parcel_text,
        "",
        "Vrsta pozidave:",
        building_text,
        "",
        "Prostorski pogoji:",
        zoning_text,
        "",
        "Relevantni predpisi:",
        "\n".join(regs_lines),
        "",
        "Sklep / povzetek:",
        summary_text,
    ]
    return "\n".join(parts)


@app.route("/", methods=["GET", "POST"])
def index():
    """Main input → fetch → summarize flow."""
    raw_data: Optional[Dict[str, Any]] = None
    ai_summary: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    if request.method == "POST":
        address = request.form.get("address", "").strip()
        parcel = request.form.get("parcel", "").strip()
        mode = request.form.get("mode", "api")

        if not address and not parcel:
            error_message = "Prosim vnesite naslov ali parcelno številko."
            return render_template(
                "index.html",
                raw_data=None,
                ai_summary=None,
                error_message=error_message,
                user_openai_key=bool(session.get("user_openai_key")),
            )

        normalized_address = normalize_address(address)
        normalized_parcel = normalize_parcel(parcel)

        # Data fetch pipeline: mix of demo/stub calls (eProstor/Urbinfo) and partial live PISRS snippets.
        if mode == "browser":
            parcel_data = fetch_parcel_data_browser(address, parcel)
        else:
            parcel_data = fetch_parcel_data(address, parcel)
        regulations_data = fetch_regulations(parcel_data)
        zoning_data = fetch_zoning_layers(parcel_data)

        raw_data = {
            "input": {
                "original_address": address,
                "normalized_address": normalized_address,
                "original_parcel": parcel,
                "normalized_parcel": normalized_parcel,
            },
            "parcel": parcel_data,
            "regulations": regulations_data,
            "zoning": zoning_data,
        }

        # AI summary (currently local/proxy demo path).
        ai_summary = summarizer.summarize(raw_data)
        session["last_ai_summary"] = ai_summary

    return render_template(
        "index.html",
        raw_data=raw_data,
        ai_summary=ai_summary,
        error_message=error_message,
        user_openai_key=bool(session.get("user_openai_key")),
    )


@app.route("/download-report", methods=["POST"])
def download_report():
    """Build and return a plain-text report from the last AI summary stored in session."""
    ai_summary = session.get("last_ai_summary")
    if not ai_summary:
        return redirect(url_for("index"))

    report_text = build_report_text(ai_summary)
    return Response(
        report_text,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment; filename=porocilo.txt"},
    )


@app.route("/set-api-key", methods=["POST"])
def set_api_key():
    """Store a user-provided OpenAI key (future direct-call path instead of proxy)."""
    api_key = request.form.get("api_key", "").strip()
    if api_key:
        session["user_openai_key"] = api_key
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)

