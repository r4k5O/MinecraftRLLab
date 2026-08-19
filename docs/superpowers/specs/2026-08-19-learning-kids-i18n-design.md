# Learning Hub, Kids UI, and Internationalization Design

## Goal
MinecraftRLLab gains a first-run onboarding flow, a separate child-friendly desktop experience, interactive tutorials, saved learning progress, achievements, a demo environment, and runtime-selectable translations.

## Experience modes
- `kids`: separate KidsMainWindow with large cards, friendly wording, guided missions, visual rewards, and hidden research-only metrics.
- `beginner`: normal desktop shell with tutorial prompts and simplified explanations.
- `research`: current full research dashboard.
- `advanced`: research UI plus raw/debug tooling.

The selected mode is persisted. Users can switch modes from Settings; changing language or mode takes effect after reopening the app.

## Internationalization
The client uses key-based locale dictionaries under `rl_client/i18n/locales/`. English is the fallback. German, French, and Spanish ship as complete first-party locales for the new onboarding, learning, kids, shared navigation, goals, common settings, and status text. `Translator` supports placeholder formatting and locale display names.

## Learning system
Tutorials are data-driven models. The engine tracks completion, current step, and event-based advancement. Initial tutorials cover agent basics, goals/rewards, first training run, reward graphs, exploration vs exploitation, and first experiment. Progress is stored separately from application settings.

Achievements are deterministic rules derived from learning/training events. Initial badges cover first tutorial, first episode, first success, diamond goal, portal goal, zombie goal, model save, and experiment comparison.

## Kids UI
Kids mode has an independent QMainWindow and screens:
- Home: connection status, current mission, one large train button, latest reward.
- Missions: four Minecraft goal cards with child-friendly descriptions.
- Learn: lesson/tutorial cards with progress.
- Progress: stars, completed lessons, achievements, recent episodes.
- Server: simple server connection and bundled-plugin installation.

Kids mode intentionally omits raw observation JSON, loss, replay memory details, manual low-level actions, and model internals from primary navigation.

## Demo mode
A deterministic demo environment can emit example training episodes without a running Minecraft server. It exists for learning/tutorial demonstrations and is visibly labeled demo data.

## Onboarding
First run selects language and experience mode. Kids mode is described as a simplified learning interface, not as an age gate. The result is stored in settings and routes the next launch to the selected shell.

## Tests
Unit tests cover translator fallback/formatting, locale completeness for required keys, profile definitions, tutorial advancement and persistence, achievements, demo episode determinism, and new settings serialization. UI source is syntax-compiled in CI; platform UI behavior is exercised by the release smoke-test workflow where Qt is installed.
