"""Navigation and scraping of title/chapter status from mystudio.inkr.com.

Real navigation (title list -> language picker -> chapter list) is not yet
verified: it requires a logged-in session, which itself needs real INKR
credentials (see auth.py). Until then, get_mock_titles() supplies placeholder
data with the same shape so the rest of the pipeline can be built and tested.
"""
from dataclasses import dataclass
from enum import Enum


class ChapterStatus(str, Enum):
    DONE = "Done"
    IN_PROGRESS = "In Progress"
    DRAFT = "Draft"


@dataclass
class Chapter:
    number: int
    status: ChapterStatus


@dataclass
class TitleChapters:
    title: str
    language: str
    chapters: list[Chapter]


# TODO: UNVERIFIED. Fill in once logged in with real credentials and the
# studio dashboard can actually be inspected.
TITLE_LINK_SELECTOR = "TODO"
LANGUAGE_PICKER_SELECTOR = "TODO"
CHAPTER_ROW_SELECTOR = "TODO"
CHAPTER_STATUS_SELECTOR = "TODO"


def get_mock_titles() -> list[TitleChapters]:
    """Placeholder chapter data standing in for a real scrape."""
    return [
        TitleChapters("Solo Leveling", "English", [
            Chapter(1, ChapterStatus.DONE),
            Chapter(2, ChapterStatus.DONE),
            Chapter(3, ChapterStatus.DONE),
        ]),
        TitleChapters("Tower of God", "English", [
            Chapter(1, ChapterStatus.DONE),
            Chapter(2, ChapterStatus.DONE),
            Chapter(3, ChapterStatus.IN_PROGRESS),
        ]),
        TitleChapters("Omniscient Reader", "Spanish", [
            Chapter(1, ChapterStatus.DONE),
            Chapter(2, ChapterStatus.DRAFT),
            Chapter(3, ChapterStatus.DRAFT),
        ]),
        TitleChapters("The Beginning After The End", "English", [
            Chapter(1, ChapterStatus.DONE),
        ]),
    ]


def find_title(catalog: list[TitleChapters], title: str) -> list[TitleChapters]:
    """Exact-match lookup: every entry (one per language) for this exact title.

    Empty list if the title isn't on INKR at all. No fuzzy matching — the title
    list (from a Google Sheet) is expected to already use INKR's exact naming.
    """
    return [tc for tc in catalog if tc.title == title]


async def find_title_on_inkr(page, title: str) -> list[TitleChapters]:
    """Search/click the exact title on the studio dashboard and read chapter
    statuses for each language it has.

    UNVERIFIED: needs real selectors once login works end-to-end. Once built,
    this replaces find_title(get_mock_titles(), title) as the real lookup.
    """
    raise NotImplementedError("Real scraping not implemented yet; use find_title(get_mock_titles(), title).")
