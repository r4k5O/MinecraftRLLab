package dev.r4k5o.minecraftrl.session;

import dev.r4k5o.minecraftrl.model.Goal;

public final class RewardEngine {
    private RewardEngine() {}

    public static RewardDecision evaluate(Goal goal, ProgressSnapshot previous, ProgressSnapshot current) {
        double reward = -0.002;

        if (current.newCell()) reward += 0.01;
        if (current.health() < previous.health()) {
            reward -= (previous.health() - current.health()) * 0.02;
        }

        reward += switch (goal) {
            case WOODEN_SWORD -> woodenSwordReward(previous, current);
            case DIAMOND -> diamondReward(previous, current);
            case NETHER_PORTAL -> portalReward(previous, current);
            case KILL_ZOMBIE -> zombieReward(previous, current);
        };

        if (current.died() || current.health() <= 0.0) {
            return new RewardDecision(reward - 1.5, true, false, "death");
        }

        boolean success = switch (goal) {
            case WOODEN_SWORD -> current.woodenSwords() > 0;
            case DIAMOND -> current.diamonds() > 0;
            case NETHER_PORTAL -> current.portalNearby();
            case KILL_ZOMBIE -> current.zombieKills() > 0;
        };
        if (success) return new RewardDecision(reward, true, true, "success");

        if (current.step() >= current.maxSteps()) {
            return new RewardDecision(reward - 0.25, true, false, "max_steps");
        }
        return new RewardDecision(reward, false, false, "");
    }

    private static double woodenSwordReward(ProgressSnapshot prev, ProgressSnapshot cur) {
        double r = 0.0;
        if (cur.logs() > prev.logs()) r += 0.05;
        if (cur.planks() > prev.planks()) r += 0.08;
        if (cur.sticks() > prev.sticks()) r += 0.10;
        if (prev.woodenSwords() == 0 && cur.woodenSwords() > 0) r += 2.0;
        return r;
    }

    private static double diamondReward(ProgressSnapshot prev, ProgressSnapshot cur) {
        double r = 0.0;
        if (prev.ironPickaxes() == 0 && cur.ironPickaxes() > 0) r += 0.25;
        if (!prev.targetingDiamondOre() && cur.targetingDiamondOre()) r += 0.05;
        if (cur.diamonds() > prev.diamonds()) r += 3.0 * (cur.diamonds() - prev.diamonds());
        return r;
    }

    private static double portalReward(ProgressSnapshot prev, ProgressSnapshot cur) {
        double r = 0.0;
        if (cur.obsidian() > prev.obsidian()) r += 0.03 * (cur.obsidian() - prev.obsidian());
        if (prev.flintAndSteel() == 0 && cur.flintAndSteel() > 0) r += 0.20;
        if (cur.placedObsidian() > prev.placedObsidian()) r += 0.08 * (cur.placedObsidian() - prev.placedObsidian());
        if (!prev.portalNearby() && cur.portalNearby()) r += 3.0;
        return r;
    }

    private static double zombieReward(ProgressSnapshot prev, ProgressSnapshot cur) {
        double r = 0.0;
        if (!prev.targetingZombie() && cur.targetingZombie()) r += 0.03;
        if (cur.zombieDamageEvents() > prev.zombieDamageEvents()) {
            r += 0.10 * (cur.zombieDamageEvents() - prev.zombieDamageEvents());
        }
        if (cur.zombieKills() > prev.zombieKills()) r += 3.0 * (cur.zombieKills() - prev.zombieKills());
        return r;
    }
}
