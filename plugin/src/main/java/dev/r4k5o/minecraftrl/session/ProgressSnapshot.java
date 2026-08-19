package dev.r4k5o.minecraftrl.session;

public record ProgressSnapshot(
        double health,
        int logs,
        int planks,
        int sticks,
        int woodenSwords,
        int ironPickaxes,
        int diamonds,
        int obsidian,
        int flintAndSteel,
        int placedObsidian,
        int zombieDamageEvents,
        int zombieKills,
        boolean targetingDiamondOre,
        boolean targetingZombie,
        boolean portalNearby,
        boolean newCell,
        boolean died,
        int step,
        int maxSteps
) {
    public static ProgressSnapshot empty(double health, int step, int maxSteps) {
        return new ProgressSnapshot(
                health, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, false, false, false, false, false,
                step, maxSteps
        );
    }
}
