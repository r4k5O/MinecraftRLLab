package dev.r4k5o.minecraftrl.session;

public record RewardDecision(double reward, boolean done, boolean success, String terminalReason) {}
