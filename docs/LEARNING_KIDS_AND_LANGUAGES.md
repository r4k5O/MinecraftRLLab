# Learning, Kids Mode, and Languages

MinecraftRLLab 0.3 adds a learning layer on top of the research client. It does not change the Paper protocol or pretend demo progress is real Minecraft training.

## First-run onboarding

On the first launch, choose:

- language: English, Deutsch, Français, or Español;
- experience: Kids / First Steps, Beginner, Research, or Advanced;
- a display name for the Kids UI.

The choice is stored in `~/.minecraftrllab/settings.json`. Language and experience mode can later be changed from Settings; reopen the app to rebuild the correct shell.

## Kids / First Steps

Kids mode is a separate `KidsMainWindow`, not a skin on the research dashboard. It has its own navigation and stylesheet:

- **Home** — one large training button, connection state, current mission, reward and stars;
- **Missions** — four large child-friendly Minecraft goal cards;
- **Learn** — interactive RL lessons with progress bars;
- **My Progress** — stars, completed lessons and unlocked achievements;
- **Server** — simplified connection and bundled Paper-plugin installation.

Research-only concepts such as replay buffers, raw JSON observations, manual action stepping, loss diagnostics and checkpoint internals are intentionally absent from Kids navigation.

## Tutorials

Tutorials are data-driven and stored in `client/rl_client/learning/catalog.py`. Explanatory steps use a **Next** button. Action steps wait for a real app event before advancing.

Included courses:

1. What is an agent?
2. Goals & rewards
3. Your first training run
4. Read the reward graph
5. Exploration vs. exploitation
6. Your first experiment

The first-training tutorial waits for actual events in order: selecting Wooden Sword, connecting the Paper server, starting training, receiving a reward, and completing an episode.

## Demo mode

Kids mode includes a deterministic demonstration environment. It is visibly marked **DEMO** and is intended to explain actions/rewards without requiring a Paper server. Demo episodes do **not** unlock real Minecraft-goal achievements.

## Achievements and stars

Learning steps grant stars. Real training events can unlock badges such as First Episode, It Learned!, Diamond Mind, Portal Master, and Zombie Hunter. Progress is stored in `~/.minecraftrllab/learning-progress.json`.

## Translation architecture

UI copy uses stable translation keys and `Translator`. English is always the fallback. First-party dictionaries live under:

```text
client/rl_client/i18n/locales/
├── en.py
├── de.py
├── fr.py
└── es.py
```

`REQUIRED_KEYS` is tested against every shipped locale. Adding a first-party language therefore fails CI until every required key is present. Raw protocol identifiers (`WOODEN_SWORD`, `CURRICULUM`, action IDs, JSON keys) stay canonical so logs and research data remain comparable across languages.

## Adding another language

1. Copy an existing locale module.
2. Translate every key listed in `i18n/keys.py`.
3. Register the locale in `i18n/locales/__init__.py` and `SUPPORTED_LOCALES`.
4. Run `python -m unittest client.tests.test_learning_i18n -v`.

The locale-completeness test reports every missing key.
