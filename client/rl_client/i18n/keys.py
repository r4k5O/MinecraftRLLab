REQUIRED_KEYS = (
    "app.name", "app.tagline", "app.restart_required",
    "common.continue", "common.back", "common.cancel", "common.save", "common.close", "common.start", "common.stop", "common.next", "common.done",
    "nav.dashboard", "nav.server", "nav.goals", "nav.manual", "nav.observations", "nav.history", "nav.models", "nav.updates", "nav.settings", "nav.learning",
    "onboarding.title", "onboarding.subtitle", "onboarding.language", "onboarding.mode", "onboarding.name", "onboarding.finish",
    "mode.kids.title", "mode.kids.description", "mode.beginner.title", "mode.beginner.description", "mode.research.title", "mode.research.description", "mode.advanced.title", "mode.advanced.description",
    "kids.home", "kids.missions", "kids.learn", "kids.progress", "kids.server", "kids.hello", "kids.ready", "kids.pick_mission", "kids.big_start", "kids.big_stop",
    "kids.connected", "kids.not_connected", "kids.reward", "kids.stars", "kids.episode", "kids.demo_badge", "kids.demo_start", "kids.real_start", "kids.tip",
    "goal.diamond.title", "goal.diamond.description", "goal.portal.title", "goal.portal.description", "goal.sword.title", "goal.sword.description", "goal.zombie.title", "goal.zombie.description",
    "kids.goal.diamond.title", "kids.goal.diamond.description", "kids.goal.portal.title", "kids.goal.portal.description", "kids.goal.sword.title", "kids.goal.sword.description", "kids.goal.zombie.title", "kids.goal.zombie.description",
    "learning.title", "learning.subtitle", "learning.completed", "learning.steps", "learning.try_demo", "learning.glossary", "learning.achievements", "learning.experiments",
    "tutorial.agent.title", "tutorial.agent.description", "tutorial.rewards.title", "tutorial.rewards.description", "tutorial.first_training.title", "tutorial.first_training.description",
    "tutorial.graph.title", "tutorial.graph.description", "tutorial.exploration.title", "tutorial.exploration.description", "tutorial.experiment.title", "tutorial.experiment.description",
    "tutorial.step.choose_goal", "tutorial.step.connect", "tutorial.step.start", "tutorial.step.watch_reward", "tutorial.step.finish_episode",
    "glossary.agent.term", "glossary.agent.explanation", "glossary.agent.kids", "glossary.reward.term", "glossary.reward.explanation", "glossary.reward.kids",
    "glossary.epsilon.term", "glossary.epsilon.explanation", "glossary.epsilon.kids", "glossary.episode.term", "glossary.episode.explanation", "glossary.episode.kids",
    "achievement.first_tutorial", "achievement.first_episode", "achievement.first_success", "achievement.diamond_mind", "achievement.portal_master", "achievement.zombie_hunter", "achievement.model_keeper", "achievement.scientist",
    "settings.language", "settings.experience_mode", "settings.kid_name", "settings.update_channel", "settings.auto_updates", "settings.repository", "settings.saved",
    "server.title", "server.host", "server.port", "server.player", "server.token", "server.connect", "server.install_plugin", "server.choose_folder", "server.plugin_installed",
    "status.connected", "status.connecting", "status.error", "status.training", "status.idle",
    "research.dashboard.title", "research.dashboard.subtitle", "research.goals.title", "research.goals.subtitle", "research.learning.title", "research.learning.subtitle",
)

REQUIRED_KEYS += (
    "connection.subtitle", "connection.server_setup", "connection.browse", "connection.install_hint", "connection.disconnected",
    "dashboard.episode", "dashboard.reward", "dashboard.epsilon", "dashboard.loss", "dashboard.success_rate", "dashboard.best_reward", "dashboard.chart", "dashboard.episodes", "dashboard.offset", "dashboard.last_action", "dashboard.start", "dashboard.stop",
    "goals.profile", "goals.curriculum_note",
    "manual.title", "manual.subtitle", "manual.action", "manual.execute", "manual.connect_hint", "manual.actions_count",
    "observation.title", "observation.subtitle", "observation.position", "observation.health", "observation.food", "observation.dimension", "observation.zombies", "observation.target",
    "history.title", "history.subtitle", "history.episode", "history.steps", "history.reward", "history.success", "history.reason", "history.yes", "history.no",
    "models.title", "models.subtitle", "models.none", "models.save", "models.load",
    "updates.title", "updates.subtitle", "updates.channel", "updates.check", "updates.not_checked", "updates.placeholder",
)
REQUIRED_KEYS += (
    "tutorial.agent.observe", "tutorial.agent.action", "tutorial.agent.learn",
    "tutorial.rewards.points", "tutorial.rewards.negative", "tutorial.rewards.shaping",
    "tutorial.graph.trend", "tutorial.graph.noise", "tutorial.graph.compare",
    "tutorial.exploration.explore", "tutorial.exploration.exploit", "tutorial.exploration.epsilon",
    "tutorial.experiment.question", "tutorial.experiment.change_one", "tutorial.experiment.compare", "tutorial.experiment.conclusion",
    "tutorial.wait_action",
)
REQUIRED_KEYS += (
    "dashboard.current_run", "dashboard.episode_total", "dashboard.exploration", "dashboard.latest_update", "dashboard.session",
    "error.connect_first", "error.plugin_missing", "error.stop_training_manual", "error.action_unavailable", "error.no_model", "error.connect_action_space",
    "models.saved", "models.loaded", "updates.checking", "updates.no_build",
)
