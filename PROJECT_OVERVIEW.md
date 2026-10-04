# INKR PM Automation

## Introduction

This tool automates a manual chapter-tracking workflow on INKR's studio dashboard (mystudio.inkr.com). The manual process today: open each comic title, pick a language, check every chapter's status (Done / In Progress / Draft), and record that in spreadsheets multiple teams rely on — then figure out which titles are ready for a new chapter.

The tool's job is to do that automatically: read a list of titles to track from a Google Sheet, look each one up on INKR by exact name, read its chapters' status per language, write that status back into three team Google Sheets, and produce a summary of which titles need a new chapter next.

It is deliberately a plain, deterministic code tool — no AI/LLM involved. Every step (exact-name matching, reading a fixed status label, counting/comparing chapter numbers, formatting a table) has a single correct answer, so there's nothing for an AI model to interpret or add value on. Using one would only add cost, latency, and a real risk of a wrong number landing in a shared team sheet.

## Plan

1. **Build the core logic against mock data first** — title matching, chapter-status aggregation, the "needs new chapter" rule, sheet read/update, and the summary report — so the decision logic could be fully designed, tested, and trusted before any real site or spreadsheet access existed. *(Done.)*
2. **Verify the real INKR login flow** by inspecting the actual site — find the real selectors for signing in, confirm the dashboard loads afterward. *(Partially done — see Current Status.)*
3. **Capture the real dashboard selectors** (title links, language picker, chapter rows, status text) once logged in, and implement the real title/chapter lookup in place of the mock catalog. *(Not started — blocked on step 2.)*
4. **Wire up real Google Sheets** — get the 3 real sheet IDs (one is the title-list "source," the other two are team sheets), confirm what each team's sheet actually tracks, and get a Google service account credential with edit access. *(Not started.)*
5. **Go live** — swap the mock sheet client and mock INKR catalog for the real ones; run the full pipeline against real data for the first time.
6. **(Optional, later) Add scheduling** — run the pipeline automatically on a timer (e.g. via `apscheduler`, already reserved for this) instead of manually, with file-based logging so unattended failures are visible after the fact. Considered and deliberately *not* handed to an agentic AI system — the routine check-and-update work has no ambiguity for an AI to resolve; scheduling is the actual gap, not intelligence.

## Current Status

**Built and verified (runs today against mock/placeholder data via `python main.py`):**
- Reading a title list from a (mock) sheet
- Exact-match lookup against a (mock) INKR catalog — including correctly reporting a title that isn't found, rather than guessing
- The chapter-status aggregation logic: latest Done chapter, latest In Progress chapter, Draft count, and the "needs new chapter" rule (true when the highest-numbered chapter is Done, meaning nothing is queued behind it)
- Writing status back into 3 (mock) sheets by updating existing rows — never auto-creating one — including correctly reporting when a sheet is missing a row for a title
- The plain-text "needs new chapter" summary report

**Verified against the real site (mystudio.inkr.com):**
- The first two steps of login: clicking "Sign In" redirects to `account.inkr.com/login`, and the real selector for the email field and "Continue" button are confirmed and in the code

**Not yet verified / blocked on real access:**
- Login past the email step (password field, submit button, and the dashboard-loaded confirmation) — `.env` still has placeholder INKR credentials
- Any real dashboard selectors (title links, language picker, chapter rows, status text) — requires being logged in first
- Real Google Sheets access — `service_account.json` doesn't exist yet, and the 3 real sheet IDs (plus which one is the title-list source, and what each team sheet is for) are still unknown

**Repo / security status:**
- Now lives in its own git repository, pushed to `github.com/minh-octopi/inkr-pm-automation` — verified clean (only source code and docs committed; `.env`, `session.json`, and `service_account.json` are all gitignored and were never committed)

**Bottom line:** the decision-making logic is finished and trustworthy. What's left is entirely about getting real access — real INKR credentials, real dashboard selectors, and real Google Sheets credentials/IDs — not more logic to design.

See [claude_update.md](claude_update.md) for the full line-by-line development log (file-by-file breakdown, feature importance ranking, open edge-case questions, and security review details), and [READ_ME.md](READ_ME.md) for setup/usage instructions.
