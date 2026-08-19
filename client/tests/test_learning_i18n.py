from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from rl_client.settings import Settings, SettingsStore


class I18nContractTest(unittest.TestCase):
    def test_translator_supports_four_complete_locales_and_fallback(self):
        from rl_client.i18n import REQUIRED_KEYS, SUPPORTED_LOCALES, Translator
        self.assertEqual({"en", "de", "fr", "es"}, set(SUPPORTED_LOCALES))
        for locale in SUPPORTED_LOCALES:
            tr = Translator(locale)
            missing = [key for key in REQUIRED_KEYS if tr.has_native(key) is False]
            self.assertEqual([], missing, f"{locale} missing: {missing}")
        self.assertEqual("Unknown key", Translator("de").text("missing.key", default="Unknown key"))
        self.assertEqual("Folge 7", Translator("de").text("kids.episode", number=7))

    def test_settings_round_trip_learning_preferences(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            store = SettingsStore(path)
            expected = Settings(language="de", experience_mode="kids", onboarding_complete=True, kid_name="Alex")
            store.save(expected)
            actual = store.load()
            self.assertEqual("de", actual.language)
            self.assertEqual("kids", actual.experience_mode)
            self.assertTrue(actual.onboarding_complete)
            self.assertEqual("Alex", actual.kid_name)


class ExperienceProfileTest(unittest.TestCase):
    def test_profiles_route_to_separate_kids_shell(self):
        from rl_client.profiles import ExperienceMode, get_profile, select_shell
        kids = get_profile(ExperienceMode.KIDS)
        research = get_profile(ExperienceMode.RESEARCH)
        self.assertEqual("kids", kids.shell)
        self.assertEqual("research", research.shell)
        self.assertFalse(kids.show_raw_observations)
        self.assertTrue(research.show_raw_observations)
        self.assertEqual("onboarding", select_shell(onboarding_complete=False, mode="kids"))
        self.assertEqual("kids", select_shell(onboarding_complete=True, mode="kids"))
        self.assertEqual("research", select_shell(onboarding_complete=True, mode="beginner"))

    def test_kids_goal_cards_are_child_friendly_and_translated(self):
        from rl_client.i18n import Translator
        from rl_client.profiles.kids_content import kids_goal_cards
        cards = kids_goal_cards(Translator("de"))
        self.assertEqual(4, len(cards))
        self.assertEqual({"DIAMOND", "NETHER_PORTAL", "WOODEN_SWORD", "KILL_ZOMBIE"}, {c.goal for c in cards})
        self.assertTrue(all(c.title and c.description and c.emoji for c in cards))
        self.assertIn("Diamant", next(c.title for c in cards if c.goal == "DIAMOND"))


class TutorialCoreTest(unittest.TestCase):
    def test_tutorial_advances_only_on_expected_event_and_persists(self):
        from rl_client.learning import ProgressStore, TutorialEngine, default_tutorials
        with tempfile.TemporaryDirectory() as tmp:
            store = ProgressStore(Path(tmp) / "progress.json")
            engine = TutorialEngine(default_tutorials(), store)
            tutorial_id = "first_training"
            self.assertEqual(0, engine.current_index(tutorial_id))
            self.assertFalse(engine.handle_event(tutorial_id, "wrong.event"))
            self.assertEqual(0, engine.current_index(tutorial_id))
            expected_event = engine.current_step(tutorial_id).event
            self.assertTrue(expected_event)
            self.assertTrue(engine.handle_event(tutorial_id, expected_event))
            self.assertEqual(1, engine.current_index(tutorial_id))
            reloaded = TutorialEngine(default_tutorials(), ProgressStore(Path(tmp) / "progress.json"))
            self.assertEqual(1, reloaded.current_index(tutorial_id))

    def test_achievements_unlock_from_real_events(self):
        from rl_client.learning.achievements import AchievementTracker
        tracker = AchievementTracker()
        unlocked = tracker.consume("episode.completed", {"success": True, "goal": "DIAMOND"})
        self.assertIn("first_episode", unlocked)
        self.assertIn("first_success", unlocked)
        self.assertIn("diamond_mind", unlocked)
        self.assertEqual([], tracker.consume("episode.completed", {"success": True, "goal": "DIAMOND"}))

    def test_demo_environment_is_deterministic_and_marked_demo(self):
        from rl_client.learning.demo_environment import DemoEnvironment
        a = DemoEnvironment(seed=42)
        b = DemoEnvironment(seed=42)
        self.assertEqual(a.reset("WOODEN_SWORD"), b.reset("WOODEN_SWORD"))
        first = [a.step() for _ in range(4)]
        second = [b.step() for _ in range(4)]
        self.assertEqual(first, second)
        self.assertTrue(all(item["demo"] for item in first))
        self.assertTrue(all("reward" in item and "action" in item for item in first))

    def test_manual_next_advances_explanatory_tutorial_steps(self):
        from rl_client.learning import ProgressStore, TutorialEngine, default_tutorials
        with tempfile.TemporaryDirectory() as tmp:
            engine = TutorialEngine(default_tutorials(), ProgressStore(Path(tmp) / "progress.json"))
            tutorial_id = "agent_basics"
            self.assertGreater(len(engine.tutorials[tutorial_id].steps), 1)
            before = engine.current_index(tutorial_id)
            self.assertTrue(engine.next(tutorial_id))
            self.assertEqual(before + 1, engine.current_index(tutorial_id))


class GlossaryTest(unittest.TestCase):
    def test_glossary_has_standard_and_kids_explanations(self):
        from rl_client.i18n import Translator
        from rl_client.learning.glossary import glossary_entries
        entries = {item.term_id: item for item in glossary_entries(Translator("en"))}
        self.assertIn("epsilon", entries)
        self.assertIn("reward", entries)
        self.assertNotEqual(entries["epsilon"].explanation, entries["epsilon"].kids_explanation)


class KidsSessionModelTest(unittest.TestCase):
    def test_real_episode_updates_stars_and_achievements_but_demo_does_not(self):
        from rl_client.profiles.kids_session import KidsSessionModel
        model = KidsSessionModel()
        model.select_goal("DIAMOND")
        demo = model.consume_training_event({"type":"episode","reward":3.0,"success":True,"goal":"DIAMOND","demo":True})
        self.assertEqual([], demo.unlocked)
        self.assertEqual(0, model.real_successes)
        real = model.consume_training_event({"type":"episode","reward":4.0,"success":True,"goal":"DIAMOND"})
        self.assertIn("diamond_mind", real.unlocked)
        self.assertEqual(1, model.real_successes)
        self.assertEqual("DIAMOND", model.goal)


if __name__ == "__main__":
    unittest.main()
