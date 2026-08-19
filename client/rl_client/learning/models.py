from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class TutorialStep:
    step_id: str
    title_key: str
    body_key: str
    event: str | None = None


@dataclass(frozen=True)
class TutorialDefinition:
    tutorial_id: str
    title_key: str
    description_key: str
    emoji: str
    steps: tuple[TutorialStep, ...]


@dataclass(frozen=True)
class GlossaryEntry:
    term_id: str
    term: str
    explanation: str
    kids_explanation: str
