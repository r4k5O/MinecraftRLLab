package dev.r4k5o.minecraftrl;

import dev.r4k5o.minecraftrl.model.Goal;
import dev.r4k5o.minecraftrl.session.ProgressSnapshot;
import dev.r4k5o.minecraftrl.session.RewardDecision;
import dev.r4k5o.minecraftrl.session.RewardEngine;

final class RewardEngineTest {
    static void run() {
        ProgressSnapshot base = ProgressSnapshot.empty(20.0, 1, 2000);

        ProgressSnapshot sword = new ProgressSnapshot(
            20.0, 0, 0, 0, 1, 0, 0, 0, 0,
            0, 0, 0, false, false, false, true, false, 2, 2000
        );
        RewardDecision swordDecision = RewardEngine.evaluate(Goal.WOODEN_SWORD, base, sword);
        TestSuite.check(swordDecision.success(), "wooden sword should complete its goal");
        TestSuite.check(swordDecision.done(), "success should terminate the episode");
        TestSuite.check(swordDecision.reward() > 1.0, "wooden sword success needs a strong positive reward");

        ProgressSnapshot diamond = new ProgressSnapshot(
            20.0, 0, 0, 0, 0, 1, 1, 0, 0,
            0, 0, 0, true, false, false, false, false, 2, 2000
        );
        TestSuite.check(RewardEngine.evaluate(Goal.DIAMOND, base, diamond).success(), "diamond inventory should complete diamond goal");

        ProgressSnapshot portal = new ProgressSnapshot(
            20.0, 0, 0, 0, 0, 0, 0, 3, 1,
            3, 0, 0, false, false, true, false, false, 2, 2000
        );
        TestSuite.check(RewardEngine.evaluate(Goal.NETHER_PORTAL, base, portal).success(), "nearby portal block should complete portal goal");

        ProgressSnapshot zombie = new ProgressSnapshot(
            20.0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 1, 1, false, true, false, false, false, 2, 2000
        );
        TestSuite.check(RewardEngine.evaluate(Goal.KILL_ZOMBIE, base, zombie).success(), "zombie kill should complete zombie goal");

        ProgressSnapshot dead = new ProgressSnapshot(
            0.0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, false, false, false, false, true, 2, 2000
        );
        RewardDecision deadDecision = RewardEngine.evaluate(Goal.DIAMOND, base, dead);
        TestSuite.check(deadDecision.done() && !deadDecision.success(), "death must terminate as failure");
        TestSuite.check(deadDecision.reward() < -0.9, "death must be strongly penalized");

        ProgressSnapshot timeout = ProgressSnapshot.empty(20.0, 2000, 2000);
        RewardDecision timeoutDecision = RewardEngine.evaluate(Goal.DIAMOND, base, timeout);
        TestSuite.check(timeoutDecision.done() && !timeoutDecision.success(), "max steps must terminate as failure");
    }
}
