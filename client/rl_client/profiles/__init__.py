from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class ExperienceMode(str, Enum):
    KIDS = "kids"
    BEGINNER = "beginner"
    RESEARCH = "research"
    ADVANCED = "advanced"


@dataclass(frozen=True)
class ExperienceProfile:
    mode: ExperienceMode
    shell: str
    title_key: str
    description_key: str
    show_raw_observations: bool
    show_manual_actions: bool
    show_model_internals: bool
    guided_learning: bool


_PROFILES = {
    ExperienceMode.KIDS: ExperienceProfile(ExperienceMode.KIDS, "kids", "mode.kids.title", "mode.kids.description", False, False, False, True),
    ExperienceMode.BEGINNER: ExperienceProfile(ExperienceMode.BEGINNER, "research", "mode.beginner.title", "mode.beginner.description", False, False, False, True),
    ExperienceMode.RESEARCH: ExperienceProfile(ExperienceMode.RESEARCH, "research", "mode.research.title", "mode.research.description", True, True, True, False),
    ExperienceMode.ADVANCED: ExperienceProfile(ExperienceMode.ADVANCED, "research", "mode.advanced.title", "mode.advanced.description", True, True, True, True),
}


def parse_mode(value: str | ExperienceMode) -> ExperienceMode:
    if isinstance(value, ExperienceMode):
        return value
    try:
        return ExperienceMode(str(value).lower())
    except ValueError:
        return ExperienceMode.RESEARCH


def get_profile(mode: str | ExperienceMode) -> ExperienceProfile:
    return _PROFILES[parse_mode(mode)]


def select_shell(*, onboarding_complete: bool, mode: str | ExperienceMode) -> str:
    if not onboarding_complete:
        return "onboarding"
    return get_profile(mode).shell


__all__ = ["ExperienceMode", "ExperienceProfile", "get_profile", "parse_mode", "select_shell"]
