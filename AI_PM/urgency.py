"""Tracks how long a title has been stuck needing a new chapter, so the PM
layer (pm_layer.py) can rank urgency on a real signal instead of guessing.

The timestamp is persisted in the sheet itself (a `first_flagged_at` column)
rather than a local file, since the sheet is already the source of truth
other teams read from, and already survives between runs.
"""
from datetime import datetime, timezone

FLAGGED_AT_FIELD = "first_flagged_at"


def next_flagged_at(current_value: str | None, needs_new_chapter: bool, now: datetime | None = None) -> str | None:
    """Returns what `first_flagged_at` should hold after this run.

    - Already flagged and still needs a new chapter: keep the original timestamp.
    - Newly needs a new chapter: stamp it with now.
    - No longer needs a new chapter: clear it (a new chapter must have shipped).
    """
    if not needs_new_chapter:
        return None
    if current_value:
        return current_value
    now = now or datetime.now(timezone.utc)
    return now.isoformat()


def days_stalled(flagged_at: str | None, now: datetime | None = None) -> int | None:
    """None means the title doesn't currently need a new chapter at all."""
    if not flagged_at:
        return None
    now = now or datetime.now(timezone.utc)
    return (now - datetime.fromisoformat(flagged_at)).days
