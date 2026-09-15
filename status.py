"""Turns a title's raw chapter list into the summary fields used for the
Sheet updates and the 'needs new chapter' report:
- latest chapter number with status Done
- latest chapter number with status In Progress
- count of chapters in Draft
- needs_new_chapter: true when the highest-numbered chapter is Done, meaning
  nothing is queued behind it (a chapter In Progress or Draft after it means
  the title is still being worked on, so it does not need a new chapter yet)
"""
from dataclasses import dataclass

from scraper import ChapterStatus, TitleChapters


@dataclass
class TitleReport:
    title: str
    language: str
    latest_done_chapter: int | None
    latest_in_progress_chapter: int | None
    draft_count: int
    needs_new_chapter: bool


def summarize(title_chapters: TitleChapters) -> TitleReport:
    chapters = sorted(title_chapters.chapters, key=lambda c: c.number)

    done_numbers = [c.number for c in chapters if c.status == ChapterStatus.DONE]
    in_progress_numbers = [c.number for c in chapters if c.status == ChapterStatus.IN_PROGRESS]
    draft_count = sum(1 for c in chapters if c.status == ChapterStatus.DRAFT)

    latest_chapter = chapters[-1] if chapters else None
    needs_new_chapter = latest_chapter is not None and latest_chapter.status == ChapterStatus.DONE

    return TitleReport(
        title=title_chapters.title,
        language=title_chapters.language,
        latest_done_chapter=max(done_numbers, default=None),
        latest_in_progress_chapter=max(in_progress_numbers, default=None),
        draft_count=draft_count,
        needs_new_chapter=needs_new_chapter,
    )
