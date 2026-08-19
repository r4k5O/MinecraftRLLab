import unittest
import numpy as np

from rl_client.encoder import ObservationEncoder
from rl_client.replay import ReplayBuffer
from rl_client.environment import MinecraftRLEnv
from rl_client.agent import DQNAgent
from rl_client.trainer import Trainer, TrainingConfig


class FakeApi:
    def __init__(self):
        self.actions = ["NOOP", "MOVE_FORWARD"]
        self.last = None

    def info(self):
        return {"actions": self.actions, "goals": ["WOODEN_SWORD"], "profiles": ["SURVIVAL"]}

    def reset(self, goal, profile, episode):
        self.last = (goal, profile, episode)
        return {"observation": sample_observation(goal)}

    def step(self, action):
        self.last = action
        return {"reward": 1.25, "done": True, "success": True, "terminal_reason": "success",
                "observation": sample_observation("WOODEN_SWORD")}


def sample_observation(goal="WOODEN_SWORD"):
    return {
        "goal": goal, "health": 20.0, "food": 20, "air": 300, "max_air": 300,
        "y": 64.0, "yaw": 90.0, "pitch": 0.0, "on_ground": True,
        "dimension": "NORMAL", "selected_slot": 0,
        "inventory": {key: 0 for key in ObservationEncoder.INVENTORY_KEYS},
        "local_grid": [0] * 75,
        "target_block_category": 0, "target_block_distance": -1.0,
        "target_entity_category": 0, "target_entity_distance": -1.0,
        "nearby_zombies": 0,
    }


class EncoderTest(unittest.TestCase):
    def test_fixed_shape_and_finite_values(self):
        encoded = ObservationEncoder().encode(sample_observation())
        self.assertEqual((111,), encoded.shape)
        self.assertEqual(np.float32, encoded.dtype)
        self.assertTrue(np.isfinite(encoded).all())

    def test_goal_changes_one_hot(self):
        encoder = ObservationEncoder()
        a = encoder.encode(sample_observation("WOODEN_SWORD"))
        b = encoder.encode(sample_observation("DIAMOND"))
        self.assertFalse(np.array_equal(a, b))


class ReplayTest(unittest.TestCase):
    def test_capacity_and_sample_shapes(self):
        replay = ReplayBuffer(3, seed=7)
        for i in range(5):
            state = np.full(111, i, dtype=np.float32)
            replay.add(state, 1, float(i), state + 1, i % 2 == 0)
        self.assertEqual(3, len(replay))
        batch = replay.sample(2)
        self.assertEqual((2, 111), batch.states.shape)
        self.assertEqual((2,), batch.actions.shape)


class EnvironmentTest(unittest.TestCase):
    def test_reset_and_step(self):
        api = FakeApi()
        env = MinecraftRLEnv(api)
        state, obs = env.reset("WOODEN_SWORD", "SURVIVAL", 4)
        self.assertEqual((111,), state.shape)
        self.assertEqual(("WOODEN_SWORD", "SURVIVAL", 4), api.last)
        result = env.step(1)
        self.assertEqual("MOVE_FORWARD", api.last)
        self.assertEqual(1.25, result.reward)
        self.assertTrue(result.done)
        self.assertTrue(result.success)
        self.assertEqual((111,), result.state.shape)


class AgentTest(unittest.TestCase):
    def test_act_and_learn_smoke(self):
        agent = DQNAgent(111, 3, seed=5, batch_size=4, replay_capacity=32, target_update_interval=2)
        state = np.zeros(111, dtype=np.float32)
        action = agent.act(state, training=False)
        self.assertIn(action, range(3))
        for i in range(8):
            agent.observe(state, i % 3, 0.1, state, i % 4 == 0)
        loss = agent.learn()
        self.assertIsInstance(loss, float)
        self.assertTrue(np.isfinite(loss))


class TrainerTest(unittest.TestCase):
    def test_single_episode_emits_metrics(self):
        env = MinecraftRLEnv(FakeApi())
        agent = DQNAgent(111, len(env.actions), seed=3, batch_size=2, replay_capacity=16)
        events = []
        trainer = Trainer(env, agent, on_event=events.append)
        trainer.run(TrainingConfig(goal="WOODEN_SWORD", profile="SURVIVAL", episodes=1, episode_offset=2))
        completed = [e for e in events if e.get("type") == "episode"]
        self.assertEqual(1, len(completed))
        self.assertTrue(completed[0]["success"])
        self.assertEqual(1, completed[0]["steps"])


if __name__ == "__main__":
    unittest.main()
