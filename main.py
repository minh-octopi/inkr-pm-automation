from datetime import datetime, timedelta, timezone

from scraper import get_mock_titles, find_title
from status import summarize
from sheets_writer import MockSheetClient, update_statuses
from report import titles_needing_new_chapter, format_summary_table
from AI_PM import urgency
from AI_PM.pm_layer import MockLLMClient, TitleUrgency
from AI_PM.notifier import MockEmailClient
import config

# Mock seed for the 3 team sheets. "source" is the master title list you
# maintain (one row per exact title name to track); team_2/team_3 stand in
# for the other two team sheets that also get status mirrored into them.
# Deliberately includes a title INKR doesn't have, and a title team_2 hasn't
# added yet, to exercise both failure paths below. Solo Leveling is seeded
# with a first_flagged_at a few days in the past, so the PM layer demo below
# shows one title that's been stalled for a while alongside one freshly
# flagged this run.
_SEEDED_FLAGGED_AT = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()

SEED_SHEETS = {
    "source": [
        {"title": "Solo Leveling", urgency.FLAGGED_AT_FIELD: _SEEDED_FLAGGED_AT},
        {"title": "Tower of God"},
        {"title": "Omniscient Reader"},
        {"title": "The Beginning After The End"},
        {"title": "Not On INKR"},
    ],
    "team_2": [
        {"title": "Solo Leveling"},
        {"title": "Tower of God"},
        {"title": "Omniscient Reader"},
    ],
    "team_3": [
        {"title": "Solo Leveling"},
        {"title": "Tower of God"},
        {"title": "Omniscient Reader"},
        {"title": "The Beginning After The End"},
    ],
}


def run_pipeline():
    """Runs the full title-list -> INKR lookup -> status -> sheet-update
    pipeline against placeholder (mock) data. Swap get_mock_titles() for
    find_title_on_inkr() and MockSheetClient for GspreadSheetClient once
    login, chapter selectors, and real sheet IDs are all verified.
    """
    print("--- INKR chapter status pipeline (MOCK DATA) ---\n")

    sheet_client = MockSheetClient(seed=SEED_SHEETS)
    inkr_catalog = get_mock_titles()

    titles_to_check = sheet_client.read_titles("source")
    print(f"Titles to check (from source sheet): {titles_to_check}\n")

    reports = []
    not_on_inkr = []
    for title in titles_to_check:
        matches = find_title(inkr_catalog, title)
        if not matches:
            not_on_inkr.append(title)
            continue
        reports.extend(summarize(tc) for tc in matches)

    print("Status report:")
    print(format_summary_table(reports))

    if not_on_inkr:
        print(f"\nNot found on INKR (exact title match failed): {not_on_inkr}")

    failures = update_statuses(sheet_client, ("source", "team_2", "team_3"), reports)
    print(f"\nUpdated {len(reports)} title(s) across 3 sheets.")
    if failures:
        print("Sheet rows that couldn't be updated (no existing row for that title):")
        for sheet_name, title in failures:
            print(f"  - {sheet_name}: {title!r}")

    needing_new = titles_needing_new_chapter(reports)
    print("\nTitles needing a new chapter:")
    print(format_summary_table(needing_new) if needing_new else "(none)")

    # --- PM layer: prioritize by how long a title has been stalled, and
    # report it. The only AI call in this whole tool happens inside
    # MockLLMClient/RealLLMClient.summarize() below — everything above this
    # line is plain code. See claude_update.md for why.
    urgencies = []
    for r in reports:
        current_row = sheet_client.get_row("source", r.title) or {}
        flagged_at = urgency.next_flagged_at(
            current_row.get(urgency.FLAGGED_AT_FIELD), r.needs_new_chapter
        )
        sheet_client.update_row("source", r.title, {urgency.FLAGGED_AT_FIELD: flagged_at})
        urgencies.append(TitleUrgency(report=r, days_stalled=urgency.days_stalled(flagged_at)))

    pm_report = MockLLMClient().summarize(urgencies)
    print("\n--- PM Report (mock LLM) ---")
    print(pm_report)

    email_client = MockEmailClient()
    email_client.send(
        to=config.PM_REPORT_RECIPIENT,
        subject="INKR chapter status — PM report",
        body=pm_report,
    )
    print(f"\n(Mock) Email queued to {config.PM_REPORT_RECIPIENT} ({len(email_client.sent)} message(s)).")


if __name__ == "__main__":
    run_pipeline()
