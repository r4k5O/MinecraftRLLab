package dev.r4k5o.minecraftrl;

import dev.r4k5o.minecraftrl.model.Action;
import dev.r4k5o.minecraftrl.model.Goal;
import dev.r4k5o.minecraftrl.model.Profile;

final class DomainEnumsTest {
    static void run() {
        TestSuite.check(Goal.valueOf("DIAMOND") == Goal.DIAMOND, "diamond goal name must be stable");
        TestSuite.check(Goal.valueOf("NETHER_PORTAL") == Goal.NETHER_PORTAL, "portal goal name must be stable");
        TestSuite.check(Goal.valueOf("WOODEN_SWORD") == Goal.WOODEN_SWORD, "wooden sword goal name must be stable");
        TestSuite.check(Goal.valueOf("KILL_ZOMBIE") == Goal.KILL_ZOMBIE, "zombie goal name must be stable");
        TestSuite.check(Profile.valueOf("SURVIVAL") == Profile.SURVIVAL, "survival profile must exist");
        TestSuite.check(Action.valueOf("BREAK_BLOCK") == Action.BREAK_BLOCK, "break action must exist");
        TestSuite.check(Action.valueOf("CRAFT_WOODEN_SWORD") == Action.CRAFT_WOODEN_SWORD, "craft sword action must exist");
        TestSuite.check(Action.valueOf("HOTBAR_8") == Action.HOTBAR_8, "hotbar action set must include slot 8");
    }
}
