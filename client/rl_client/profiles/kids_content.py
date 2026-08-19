from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol


class TextProvider(Protocol):
    def text(self, key: str, default: str | None = None, **values) -> str: ...


@dataclass(frozen=True)
class KidsGoalCard:
    goal: str
    emoji: str
    title: str
    description: str


def kids_goal_cards(tr: TextProvider) -> tuple[KidsGoalCard, ...]:
    specs = (
        ("DIAMOND", "💎", "kids.goal.diamond.title", "kids.goal.diamond.description"),
        ("NETHER_PORTAL", "🟪", "kids.goal.portal.title", "kids.goal.portal.description"),
        ("WOODEN_SWORD", "🗡️", "kids.goal.sword.title", "kids.goal.sword.description"),
        ("KILL_ZOMBIE", "🧟", "kids.goal.zombie.title", "kids.goal.zombie.description"),
    )
    return tuple(KidsGoalCard(goal, emoji, tr.text(title), tr.text(description)) for goal, emoji, title, description in specs)
