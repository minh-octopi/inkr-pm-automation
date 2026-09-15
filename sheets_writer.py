"""Reads the title list from, and writes chapter status back into, the 3
team Google Sheets.

The title list itself lives in one of the 3 sheets (the "source" of titles to
track). Writing back is an exact-match update against an existing row per
title -- never an append/auto-create -- since the sheets are the source of
truth for which titles exist; a title present in the file but not on INKR
(or a sheet missing a row for a title we do have INKR data for) is reported
as a failure rather than silently created.

Real Sheets access needs `service_account.json` (not present yet) and the 3
real sheet IDs in .env (currently placeholders — see config.GOOGLE_SHEET_IDS).
Until those exist, MockSheetClient stands in so this can be exercised
end-to-end without touching real Sheets.
"""
from abc import ABC, abstractmethod
from typing import Iterable

from status import TitleReport


class TitleNotFoundError(Exception):
    """Raised by update_row when no row for that title exists in the sheet."""


class SheetClient(ABC):
    @abstractmethod
    def read_titles(self, sheet_name: str) -> list[str]:
        ...

    @abstractmethod
    def update_row(self, sheet_name: str, title: str, updates: dict) -> None:
        """Update the existing row for `title` in place. Raises
        TitleNotFoundError if no row for that exact title exists."""
        ...


class MockSheetClient(SheetClient):
    """In-memory stand-in for gspread, seeded with rows per sheet, so the
    read-titles / find-on-inkr / update-row flow can be exercised without
    real Google credentials or network access."""

    def __init__(self, seed: dict[str, list[dict]] | None = None):
        self.sheets: dict[str, list[dict]] = {
            name: [dict(row) for row in rows] for name, rows in (seed or {}).items()
        }

    def read_titles(self, sheet_name: str) -> list[str]:
        return [row["title"] for row in self.sheets.get(sheet_name, [])]

    def update_row(self, sheet_name: str, title: str, updates: dict) -> None:
        for row in self.sheets.get(sheet_name, []):
            if row.get("title") == title:
                row.update(updates)
                return
        raise TitleNotFoundError(f"{title!r} not found in sheet {sheet_name!r}")


class GspreadSheetClient(SheetClient):
    """Real Google Sheets client.

    UNVERIFIED: needs service_account.json and real sheet IDs before use.
    """

    def __init__(self, sheet_ids: dict[str, str], credentials_file: str):
        import gspread  # imported here so mock-only runs don't need it installed/configured
        self._gc = gspread.service_account(filename=credentials_file)
        self._sheet_ids = sheet_ids

    def _worksheet(self, sheet_name: str):
        sheet_id = self._sheet_ids[sheet_name]
        return self._gc.open_by_key(sheet_id).sheet1

    def read_titles(self, sheet_name: str) -> list[str]:
        return [row["title"] for row in self._worksheet(sheet_name).get_all_records()]

    def update_row(self, sheet_name: str, title: str, updates: dict) -> None:
        worksheet = self._worksheet(sheet_name)
        cell = worksheet.find(title, in_column=1)  # TODO: UNVERIFIED — assumes title is column A
        if cell is None:
            raise TitleNotFoundError(f"{title!r} not found in sheet {sheet_name!r}")
        header = worksheet.row_values(1)
        for field, value in updates.items():
            if field in header:
                worksheet.update_cell(cell.row, header.index(field) + 1, value)


def report_to_row(report: TitleReport) -> dict:
    return {
        "title": report.title,
        "language": report.language,
        "latest_done_chapter": report.latest_done_chapter,
        "latest_in_progress_chapter": report.latest_in_progress_chapter,
        "draft_count": report.draft_count,
        "needs_new_chapter": report.needs_new_chapter,
    }


def update_statuses(
    client: SheetClient, sheet_names: Iterable[str], reports: Iterable[TitleReport]
) -> list[tuple[str, str]]:
    """Writes each report back into the given sheets via update_row.

    TODO: once each team sheet's actual purpose is known, this may need to
    send different fields to each rather than mirroring the same row to all
    three, which is what it does for now.

    Returns (sheet_name, title) pairs that couldn't be updated because that
    sheet has no existing row for that title.
    """
    reports = list(reports)
    failures = []
    for sheet_name in sheet_names:
        for r in reports:
            try:
                client.update_row(sheet_name, r.title, report_to_row(r))
            except TitleNotFoundError:
                failures.append((sheet_name, r.title))
    return failures
