"""The PM layer: takes this run's title reports (plus how long each has been
stalled, from urgency.py) and produces a prioritized, human-readable report.

This is the one place in the whole tool that calls an LLM, and on purpose:
ranking "what matters most right now" and writing it up clearly is a judgment
call, not a lookup. Everything upstream (title matching, status aggregation)
stays plain, deterministic code. Cost stays low because this call only runs
once per scheduled pipeline run (not continuously, unlike an always-on agent)
and its input is a small structured table, not raw page content.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from status import TitleReport


@dataclass
class TitleUrgency:
    report: TitleReport
    days_stalled: int | None  # None if this title doesn't need a new chapter


class LLMClient(ABC):
    @abstractmethod
    def summarize(self, urgencies: list[TitleUrgency]) -> str:
        """Returns a short, prioritized, human-readable report."""
        ...


class MockLLMClient(LLMClient):
    """Deterministic stand-in: sorts by days stalled (most urgent first) and
    formats plainly, so the PM layer can be exercised without a real API key
    or any API cost."""

    def summarize(self, urgencies: list[TitleUrgency]) -> str:
        needing = sorted(
            (u for u in urgencies if u.days_stalled is not None),
            key=lambda u: u.days_stalled,
            reverse=True,
        )
        if not needing:
            return "No titles currently need a new chapter."

        lines = ["Titles needing a new chapter, most urgent first:", ""]
        for u in needing:
            lines.append(
                f"- {u.report.title} ({u.report.language}): stalled {u.days_stalled} day(s) "
                f"since chapter {u.report.latest_done_chapter} was marked Done."
            )
        return "\n".join(lines)


class RealLLMClient(LLMClient):
    """Real client. UNVERIFIED — needs an API key (config.ANTHROPIC_API_KEY).

    Deliberately uses a small/cheap model: the input here is a short
    structured table, not raw page content, so a bigger model buys nothing.
    Keeping this call small and infrequent is what keeps the tool cheap
    compared to an always-on agent.
    """

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001"):
        import anthropic  # imported here so mock-only runs don't need it installed
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def summarize(self, urgencies: list[TitleUrgency]) -> str:
        table = "\n".join(
            f"{u.report.title} | {u.report.language} | stalled {u.days_stalled} day(s) "
            f"| latest done ch.{u.report.latest_done_chapter} | drafts in progress: {u.report.draft_count}"
            for u in urgencies
            if u.days_stalled is not None
        )
        prompt = (
            "You are a project manager for a comics localization team. Given this "
            "table of titles that need a new chapter, write a short, prioritized "
            "report (most urgent first) a manager can act on in under a minute.\n\n"
            f"{table or '(no titles currently need a new chapter)'}"
        )
        response = self._client.messages.create(
            model=self._model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
