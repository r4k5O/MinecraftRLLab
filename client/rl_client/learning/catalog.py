from __future__ import annotations
from .models import TutorialDefinition,TutorialStep


def default_tutorials()->tuple[TutorialDefinition,...]:
    return (
        TutorialDefinition("agent_basics","tutorial.agent.title","tutorial.agent.description","🤖",(
            TutorialStep("observe","tutorial.agent.title","tutorial.agent.observe"),
            TutorialStep("action","tutorial.agent.title","tutorial.agent.action"),
            TutorialStep("learn","tutorial.agent.title","tutorial.agent.learn"),
        )),
        TutorialDefinition("rewards","tutorial.rewards.title","tutorial.rewards.description","⭐",(
            TutorialStep("points","tutorial.rewards.title","tutorial.rewards.points"),
            TutorialStep("negative","tutorial.rewards.title","tutorial.rewards.negative"),
            TutorialStep("shaping","tutorial.rewards.title","tutorial.rewards.shaping"),
        )),
        TutorialDefinition("first_training","tutorial.first_training.title","tutorial.first_training.description","🚀",(
            TutorialStep("choose_goal","tutorial.first_training.title","tutorial.step.choose_goal","goal.WOODEN_SWORD"),
            TutorialStep("connect","tutorial.first_training.title","tutorial.step.connect","server.connected"),
            TutorialStep("start","tutorial.first_training.title","tutorial.step.start","training.started"),
            TutorialStep("reward","tutorial.first_training.title","tutorial.step.watch_reward","training.reward"),
            TutorialStep("finish","tutorial.first_training.title","tutorial.step.finish_episode","episode.completed"),
        )),
        TutorialDefinition("reward_graph","tutorial.graph.title","tutorial.graph.description","📈",(
            TutorialStep("trend","tutorial.graph.title","tutorial.graph.trend"),
            TutorialStep("noise","tutorial.graph.title","tutorial.graph.noise"),
            TutorialStep("compare","tutorial.graph.title","tutorial.graph.compare"),
        )),
        TutorialDefinition("exploration","tutorial.exploration.title","tutorial.exploration.description","🎲",(
            TutorialStep("explore","tutorial.exploration.title","tutorial.exploration.explore"),
            TutorialStep("exploit","tutorial.exploration.title","tutorial.exploration.exploit"),
            TutorialStep("epsilon","tutorial.exploration.title","tutorial.exploration.epsilon"),
        )),
        TutorialDefinition("first_experiment","tutorial.experiment.title","tutorial.experiment.description","🧪",(
            TutorialStep("question","tutorial.experiment.title","tutorial.experiment.question"),
            TutorialStep("change","tutorial.experiment.title","tutorial.experiment.change_one"),
            TutorialStep("compare","tutorial.experiment.title","tutorial.experiment.compare"),
            TutorialStep("conclusion","tutorial.experiment.title","tutorial.experiment.conclusion"),
        )),
    )
