# Progress Update — INKR Automation

Full development log: what's built, how important each piece is, and what's next. Read this before starting new work so we don't re-litigate decisions already made.

## Session log

- **2026-09-13:** No code changes. Session was purely explanatory — walked through what "real chapter selectors" means (i.e. what filling in `find_title_on_inkr` in `scraper.py` actually requires: inspecting the live dashboard's title links, language picker, chapter rows, and status text once logged in). No blockers resolved, no decisions changed. Everything below is unchanged from the last update.

## What's built (runs today via `python main.py`, mock data)

Flow: read title list from a sheet → exact-match lookup on INKR → aggregate chapter status → update back into 3 sheets → print "needs new chapter" summary. Verified end-to-end, including both failure paths (a title missing from INKR; a title missing from one of the 3 sheets).

- [scraper.py](scraper.py) — `Chapter`, `ChapterStatus` (Done/In Progress/Draft), `TitleChapters`. `get_mock_titles()` returns the placeholder "what's on INKR" catalog. `find_title(catalog, title)` is an exact-match lookup (no fuzzy matching — sheet titles are expected to match INKR's naming exactly). Real lookup (`find_title_on_inkr`) is a stub — selectors unverified.
- [status.py](status.py) — `summarize()` turns a title's chapter list into: latest Done chapter #, latest In Progress chapter #, Draft count, and `needs_new_chapter` (true when the highest-numbered chapter is Done, i.e. nothing queued after it).
- [sheets_writer.py](sheets_writer.py) — `MockSheetClient` (in-memory, used now) and `GspreadSheetClient` (real, unverified) behind a shared `SheetClient` interface with `read_titles()` and `update_row()` (exact-match update, never auto-create — raises `TitleNotFoundError` if a sheet has no row for that title). `update_statuses()` writes each report back into all 3 sheets and collects any per-sheet failures instead of raising.
- [report.py](report.py) — plain-text summary table. No LLM/AI — see "Confirmed decisions."
- [main.py](main.py) — orchestrates the above; seeds a mock "source" sheet (the title list) plus `team_2`/`team_3`, deliberately includes one title not on INKR and one title missing from `team_2` to exercise both failure paths.
- [config.py](config.py) — `GOOGLE_SHEET_IDS` dict (`team_1`/`team_2`/`team_3`), read from 3 `.env` placeholder keys. `team_1` is intended to be the "source" title-list sheet once real sheet IDs are known.
- [auth.py](auth.py) — login flow verified up to the email + Continue step only (see "Blocked" below). Saves/reuses session cookies via `session.json` once a real login succeeds.
- [READ_ME.md](READ_ME.md) — setup and usage instructions for a new reader.

## Feature importance

What matters most to least, so effort is spent in the right order:

| Priority | Feature | Status |
|---|---|---|
| **Critical** | Log into INKR | Partial — verified only through email+Continue |
| **Critical** | Find an exact title on INKR and read its chapters' status | Stubbed — logic ready, real selectors missing |
| **Critical** | Decide "needs new chapter" correctly | Done and verified |
| **High** | Read the title list from a sheet | Done (mock); real Sheets access blocked |
| **High** | Write status back into the 3 sheets | Done (mock); real Sheets access blocked |
| **High** | Report titles needing a new chapter | Done |
| **Medium** | Handle a title not found on INKR / not found in a given sheet without crashing | Done and verified |
| **Medium** | Multi-language chapters per title | Done (data model supports it; untested against real multi-language titles) |
| **Low** | Scheduled/recurring runs | Not built — `apscheduler`/`TIMEZONE` reserved for this, intentionally kept unused for now |
| **Low** | AI/LLM-based summarization | Deliberately rejected — see below |

## Confirmed decisions

- Title list lives in one of the 3 Google Sheets (not a local file) — the tool reads titles from it, then updates status back into that same sheet.
- Matching sheet titles against INKR is **exact match only** — no fuzzy matching. A mismatch (typo, different casing) is reported as "not found," not guessed.
- **No LLM/AI in this tool** — deliberate, not a placeholder decision. Every step (title matching, status aggregation, report formatting) is deterministic, so plain code is the correct fit: exact-match lookups and fixed status labels have nothing for an LLM to interpret, and using one would add cost, latency, and a real risk of a hallucinated chapter count feeding into shared team sheets. `GEMINI_API_KEY` and `google-generativeai` have been removed from `config.py`/`.env`/`requirements.txt`.
- `apscheduler`/`config.TIMEZONE` are kept despite being currently unused — reserved for a planned future scheduling feature, not dead code.

## Security review (completed)

- `.env` has only ever held placeholder values — confirmed via git history search across all local and remote-tracking refs.
- The whole `INKR_automation_private/` folder is excluded from the parent repo's `.gitignore`, plus a global `*.env` rule and this project's own `.gitignore` — triple redundant.
- Confirmed via `git log --all --full-history`, `git ls-remote`, and a fresh `git fetch` that this project has **never** been committed or pushed to GitHub, at any point.
- Fixed one latent gap: `service_account.json` was missing from this project's own `.gitignore` (it was only safe because the parent repo blanket-excluded the whole folder — a real risk if this project is ever moved to its own repo). Added.
- No hardcoded secrets or credential-leaking log/print statements found anywhere in the source.

## Open logic questions (documented, not yet resolved)

1. `needs_new_chapter` assumes chapters are numbered in the order they're worked on; a lower-numbered chapter still In Progress/Draft *after* a higher-numbered Done chapter would misfire this.
2. `draft_count` counts all Draft chapters anywhere, not just ones queued after the latest Done chapter.
3. A title with zero chapters never shows up as needing a new chapter.
4. All 3 sheets currently get the identical mirrored row — real per-sheet field mapping unknown until each team sheet's purpose is confirmed.
5. `GspreadSheetClient` assumes title is in column A and always targets `.sheet1` (first tab) — unverified.

## Blocked / needs real input before going live

1. **Real INKR credentials** — `.env` still has placeholders. Needed to verify login past the email step and to inspect the actual studio dashboard.
2. **Title/chapter selectors** — `find_title_on_inkr` is unimplemented. Needs a logged-in session to inspect: title link markup, language picker, chapter row + status text.
3. **3 real Google Sheet IDs + what each team's sheet is for** — currently placeholder env vars (`team_1`/`team_2`/`team_3`). Once known, `update_statuses()` likely needs to send different fields per sheet instead of mirroring the same row to all three, and confirm which sheet is actually the title-list "source."
4. **`service_account.json`** — not present in the folder. Required for `GspreadSheetClient` to authenticate.

## Next steps

1. Get real INKR credentials into `.env` → verify login past the email step, confirm `DASHBOARD_SELECTOR`.
2. With a logged-in session, inspect the real dashboard and fill in `scraper.py`'s selectors (title link, language picker, chapter row, chapter status) → implement `find_title_on_inkr`.
3. Get the 3 real Google Sheet URLs/IDs, confirm which is the title-list "source," and what each team sheet actually tracks (may change `update_statuses()` to send different fields per sheet instead of mirroring).
4. Get `service_account.json` → wire up `GspreadSheetClient` in place of `MockSheetClient`.
5. Once live, revisit the 5 open logic questions above against real data before trusting the "needs new chapter" output.

Steps 1–2 (INKR access) and 3–4 (Sheets access) are independent — whichever is ready first can proceed on its own.
