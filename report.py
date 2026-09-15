"""Builds the human-readable summary of titles that need a new chapter.

Plain string formatting, no LLM needed.
"""
from typing import Iterable

from status import TitleReport


def titles_needing_new_chapter(reports: Iterable[TitleReport]) -> list[TitleReport]:
    return [r for r in reports if r.needs_new_chapter]


def format_summary_table(reports: Iterable[TitleReport]) -> str:
    header = f"{'Title':<30} {'Lang':<10} {'Latest Done':<12} {'Latest In-Prog':<15} {'Draft Count':<12}"
    lines = [header, "-" * len(header)]
    for r in reports:
        lines.append(
            f"{r.title:<30} {r.language:<10} "
            f"{str(r.latest_done_chapter or '-'):<12} "
            f"{str(r.latest_in_progress_chapter or '-'):<15} "
            f"{r.draft_count:<12}"
        )
    return "\n".join(lines)
