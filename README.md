# DataScraper_Prototype

Prototype web app for **AI-assisted parcel & zoning pre-check**.  
Built as a technical exercise for Arhionik d.o.o.

The tool accepts:

- **Address** (e.g. `Mestni trg 1, Ljubljana`)  
- **Parcel number** (e.g. `1234/5 k.o. Center`)

…then:

1. Normalises the input (spacing, commas, casing).
2. Fetches **parcel, zoning and legal regulation data** via a small set of scraper/fetcher functions.
3. Sends the structured `raw_data` to an **AI summariser** (Cloudflare Worker + OpenAI), or falls back to a local demo summariser.
4. Renders a clean UI with sections:
   - Parcel info
   - Building (type / intended use)
   - Zoning & layers
   - Relevant regulations
   - Summary
   - Sources used
5. Allows exporting a **plain-text report** for quick sharing.

> 💡 The goal is to show **architecture, approach and modularity**, not a fully production-ready integration with all official systems.

---

## 1. Architecture Overview

### 1.1 High-level

- **Flask app (`app.py`)**
  - Handles HTTP requests, form inputs and routing.
  - Orchestrates:
    - input normalisation
    - data fetchers (`scrapers/*`)
    - AI summarisation (`ai/summarizer.py`)
    - simple report export (`report/*`)

- **Scrapers / data fetchers (`scrapers/*`)**
  - `eprostor_api.py`  
    - Stub/demo parcel data; HTTP helper illustrating where a real eProstor/WFS call would be.
  - `eprostor_browser.py`  
    - Playwright-based **advanced browser fallback** for scenarios with no public API.
    - Demonstrates how to automate an official viewer and still return structured parcel data.
  - `pisrs_api.py`  
    - Fetches and lightly cleans PISRS HTML for selected regulations (e.g. GZ-1, Uredba o razvrščanju objektov).
    - Extracts short text snippets that are then passed to AI.
  - `urbinfo_api.py` / `urbinfo_browser.py`  
    - Demo/stub zoning data and layers to illustrate where Urbinfo / municipal GIS calls would plug in.

- **AI summariser (`ai/summarizer.py`)**
  - Builds a **structured summary** from `raw_data`:
    - `parcel_section` (short/long)
    - `building_section` (short/long)
    - `zoning_section` (short/long)
    - `regulations_section` (list of laws, each with short/long + source)
    - `summary_section` (short/long)
    - `sources` (list)
  - Two pathways:
    - **Cloudflare Worker proxy** (OpenAI, model e.g. `gpt-4.1-mini`)
    - **Local demo summariser** (no external calls, used as fallback)

- **Input normalisation (`utils/input_normalization.py`)**
  - Normalises address and parcel input:
    - trims whitespace
    - fixes basic spacing
    - inserts commas after street number where reasonable
    - simple title-casing
  - Keeps the app robust even with imperfect user input (e.g. `mestni trg 1 ljubljna`).

- **Report builder (`report/*`)**
  - Builds a simple `.txt` file containing:
    - parcel / location line
    - building/use info
    - zoning conditions
    - regulations list
    - summary/conclusion

- **Frontend (Flask template + CSS)**
  - `templates/index.html` and `static/main.css`
  - Clean, minimal UI:
    - English section titles
    - Slovenian content (AI output)
    - Rounded cards, spacing, expand/collapse toggles
    - Buttons: Get data, Advanced web lookup, Download report
    - Info/help cards with explanation of the prototype

---

## 2. Data Flow

1. **User input → `/` (POST)**  
   - Address and parcel fields submitted from the form.
   - Normalised via `normalize_address()` and `normalize_parcel()`.

2. **Data fetchers**  
   - `fetch_parcel_data()` → parcel info (currently structured demo + HTTP stub).
   - `fetch_regulations()` → regulation metadata/snippets from PISRS.
   - `fetch_zoning_layers()` → zoning + layers (demo).

3. **`raw_data` assembly**  
   - `raw_data = { input: {...}, parcel: {...}, regulations: [...], zoning: {...} }`

4. **AI summarisation**  
   - `ai_summary = summarizer.summarize(raw_data)`
   - If a user-provided key is set in the session, a future direct-OpenAI path is available.
   - Otherwise:
     - If `CF_WORKER_PROXY_URL` is set → POST to Cloudflare Worker → OpenAI → structured JSON.
     - If proxy is unreachable or errors → fall back to local demo summariser.

5. **Rendering**  
   - `index.html` renders:
     - header (tool title, model info, author name)
     - input card
     - result cards:
       - Parcel info (short/long toggle)
       - Building (short/long toggle)
       - Zoning & layers (short/long toggle)
       - Relevant regulations (each law with its own expand)
       - Summary (short/long toggle)
       - Sources used
     - Report preview + Download button.

---

## 3. Setup & Running (Local)

### 3.1 Requirements

- Python 3.9+  
- `pip`  
- [Playwright CLI](https://playwright.dev/python/docs/intro) (installed via `pip` + `playwright install`)
- (Optional but recommended) Git, if cloning instead of ZIP.

### 3.2 Installation (example for macOS / Linux)

```bash
git clone https://github.com/lanko321/DataScraper_Prototype.git
cd DataScraper_Prototype

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
playwright install

cp .env.example .env
# Then edit .env to set:
#   FLASK_SECRET_KEY=your-secret
#   CF_WORKER_PROXY_URL=https://your-worker-id.workers.dev/

flask --app app.py run
```

## Troubleshooting

- On some Windows machines, Cloudflare `*.workers.dev` domains might not resolve because of DNS settings. In that case the app will automatically fall back to the local demo summariser, and results will still be shown, just not via the remote AI proxy.
- Make sure to create a `.env` file from `.env.example` and set `CF_WORKER_PROXY_URL` to the deployed Cloudflare Worker URL. Without this, the proxy path will also fall back to the local demo summariser.
