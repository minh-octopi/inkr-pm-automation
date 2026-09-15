from scraper import get_mock_titles, find_title
from status import summarize
from sheets_writer import MockSheetClient, update_statuses
from report import titles_needing_new_chapter, format_summary_table

# Mock seed for the 3 team sheets. "source" is the master title list you
# maintain (one row per exact title name to track); team_2/team_3 stand in
# for the other two team sheets that also get status mirrored into them.
# Deliberately includes a title INKR doesn't have, and a title team_2 hasn't
# added yet, to exercise both failure paths below.
SEED_SHEETS = {
    "source": [
        {"title": "Solo Leveling"},
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


if __name__ == "__main__":
    run_pipeline()
