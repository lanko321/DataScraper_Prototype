# DataScraper_Prototype

Prototype Flask app for Arhionik d.o.o. to fetch parcel, zoning, and regulation data, then summarize results with AI. This version provides the initial skeleton and UI shell; data fetching and summarization will be wired next.

## Getting started
1. Create a virtual environment (Python 3.11+ recommended).
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. (When Playwright is needed) install browsers:
   ```
   playwright install
   ```
4. Set `FLASK_SECRET_KEY` in your environment (export or .env).
5. Run the app:
   ```
   flask --app app run
   ```

## Project layout
- `app.py` – Flask app and routes.
- `scrapers/` – API and Playwright clients (stubs for now).
- `ai/` – Summarization logic and prompts (stubs for now).
- `report/` – Formatting/build helpers (stubs for now).
- `utils/` – Input normalization utilities (stub for now).
- `templates/` – Jinja templates (main UI in `index.html`).
- `static/` – Custom styles.


