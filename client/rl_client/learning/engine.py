from __future__ import annotations
from .models import TutorialDefinition, TutorialStep
from .progress import ProgressStore, LearningProgress


class TutorialEngine:
    def __init__(self, tutorials: tuple[TutorialDefinition, ...], store: ProgressStore | None = None) -> None:
        self.tutorials = {item.tutorial_id: item for item in tutorials}
        self.store = store or ProgressStore()
        self.progress = self.store.load()

    def current_index(self, tutorial_id: str) -> int:
        tutorial = self.tutorials[tutorial_id]
        return min(self.progress.tutorial_steps.get(tutorial_id, 0), len(tutorial.steps))

    def current_step(self, tutorial_id: str) -> TutorialStep:
        tutorial = self.tutorials[tutorial_id]
        index = self.current_index(tutorial_id)
        if index >= len(tutorial.steps):
            return tutorial.steps[-1]
        return tutorial.steps[index]

    def handle_event(self, tutorial_id: str, event: str) -> bool:
        tutorial = self.tutorials[tutorial_id]
        index = self.current_index(tutorial_id)
        if index >= len(tutorial.steps):
            return False
        expected = tutorial.steps[index].event
        if expected is None or event != expected:
            return False
        index += 1
        self.progress.tutorial_steps[tutorial_id] = index
        self.progress.stars += 1
        if index >= len(tutorial.steps) and tutorial_id not in self.progress.completed_tutorials:
            self.progress.completed_tutorials.append(tutorial_id)
            self.progress.stars += 4
        self.store.save(self.progress)
        return True

    def next(self, tutorial_id: str) -> bool:
        tutorial = self.tutorials[tutorial_id]
        index = self.current_index(tutorial_id)
        if index >= len(tutorial.steps) or tutorial.steps[index].event is not None:
            return False
        index += 1
        self.progress.tutorial_steps[tutorial_id] = index
        self.progress.stars += 1
        if index >= len(tutorial.steps) and tutorial_id not in self.progress.completed_tutorials:
            self.progress.completed_tutorials.append(tutorial_id)
            self.progress.stars += 4
        self.store.save(self.progress)
        return True

    def completion(self, tutorial_id: str) -> tuple[int, int]:
        tutorial = self.tutorials[tutorial_id]
        return self.current_index(tutorial_id), len(tutorial.steps)
