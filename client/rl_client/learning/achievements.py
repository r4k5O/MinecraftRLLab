from __future__ import annotations


class AchievementTracker:
    def __init__(self, unlocked: set[str] | None = None) -> None:
        self.unlocked = set(unlocked or ())

    def consume(self, event: str, payload: dict | None = None) -> list[str]:
        payload = payload or {}
        candidates: list[str] = []
        if event == "tutorial.completed": candidates.append("first_tutorial")
        if event == "episode.completed":
            candidates.append("first_episode")
            if payload.get("success"):
                candidates.append("first_success")
                goal = payload.get("goal")
                if goal == "DIAMOND": candidates.append("diamond_mind")
                elif goal == "NETHER_PORTAL": candidates.append("portal_master")
                elif goal == "KILL_ZOMBIE": candidates.append("zombie_hunter")
        if event == "model.saved": candidates.append("model_keeper")
        if event == "experiment.compared": candidates.append("scientist")
        new = [item for item in candidates if item not in self.unlocked]
        self.unlocked.update(new)
        return new
