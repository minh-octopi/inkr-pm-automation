# INKR Automation

## How To Use

### 1. Install dependencies

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 2. Configure `.env`

Copy your real values into `.env` (already gitignored):

```
INKR_EMAIL=...
INKR_PASSWORD=...
GOOGLE_SHEET_ID_TEAM_1=...
GOOGLE_SHEET_ID_TEAM_2=...
GOOGLE_SHEET_ID_TEAM_3=...
GSPREAD_SERVICE_ACCOUNT_FILE=service_account.json
```

`GOOGLE_SHEET_ID_TEAM_1` is intended to be the "source" sheet holding the title list; `TEAM_2`/`TEAM_3` are the other two team sheets that get status mirrored into them. `service_account.json` (a Google service account key with edit access to all 3 sheets) needs to be placed in this folder — not included in the repo.

### 3. Run the status pipeline

```bash
python main.py
```

This runs the full flow: read the title list from the source sheet → look up each title on INKR (exact match) → read each chapter's status (Done / In Progress / Draft) → update the status back into all 3 sheets → print a summary of titles needing a new chapter.

**Current state: this runs against placeholder (mock) data, not the real site or real sheets.** `main.py` seeds an in-memory mock sheet client and an in-memory mock INKR catalog so the pipeline logic can be exercised end-to-end. Nothing is written to real Google Sheets and no real page is scraped yet — see "Known limitations" below.

### 4. Test the INKR login separately

```bash
python auth.py
```

Runs just the login flow in isolation (opens a visible browser). Useful for checking credentials and watching the login steps without running the full pipeline. On success it saves session cookies to `session.json` so future runs can skip logging in again.

### Known limitations (not yet live)

- **Login is only verified up to the email + Continue step.** The password step, submit button, and the selector that confirms a successful login (`DASHBOARD_SELECTOR` in `auth.py`) are unverified placeholders — real INKR credentials are needed to confirm them.
- **Chapter scraping is not implemented.** `find_title_on_inkr()` in `scraper.py` is a stub; it needs real selectors for the title link, language picker, chapter rows, and chapter status text, found by inspecting the live dashboard after logging in.
- **Sheets access is not implemented.** `GspreadSheetClient` in `sheets_writer.py` needs `service_account.json` and the 3 real sheet IDs before it can replace the mock client.

See `claude_update.md` for the full running log of what's built, what's verified, and what's still open.
