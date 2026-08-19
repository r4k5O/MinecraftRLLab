package dev.r4k5o.minecraftrl.session;

import dev.r4k5o.minecraftrl.MinecraftRLLabPlugin;
import dev.r4k5o.minecraftrl.model.Action;
import dev.r4k5o.minecraftrl.model.Goal;
import dev.r4k5o.minecraftrl.model.Profile;
import org.bukkit.Bukkit;
import org.bukkit.GameMode;
import org.bukkit.HeightMap;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.World;
import org.bukkit.WorldCreator;
import org.bukkit.entity.Player;
import org.bukkit.entity.Zombie;
import org.bukkit.event.entity.CreatureSpawnEvent;
import org.bukkit.inventory.ItemStack;
import org.bukkit.util.Vector;

import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

public final class TrainingSession {
    private final MinecraftRLLabPlugin plugin;
    private final ActionExecutor actionExecutor;
    private final ObservationBuilder observationBuilder = new ObservationBuilder();
    private final Set<String> visitedCells = new HashSet<>();
    private final int maxSteps;
    private final int episodeStride;
    private final String worldName;
    private final long worldSeed;

    private UUID boundPlayer;
    private Goal goal = Goal.WOODEN_SWORD;
    private Profile profile = Profile.SURVIVAL;
    private int episode;
    private int step;
    private double totalReward;
    private boolean done;
    private boolean success;
    private String terminalReason = "";
    private int placedObsidian;
    private int zombieDamageEvents;
    private int zombieKills;
    private boolean died;
    private ProgressSnapshot previousProgress;

    public TrainingSession(MinecraftRLLabPlugin plugin) {
        this.plugin = plugin;
        this.maxSteps = plugin.getConfig().getInt("training.max-steps", 2000);
        this.episodeStride = plugin.getConfig().getInt("training.episode-stride", 2048);
        this.worldName = plugin.getConfig().getString("training.world", "rl_training");
        this.worldSeed = plugin.getConfig().getLong("training.seed", 7349215L);
        this.actionExecutor = new ActionExecutor(
                plugin.getConfig().getDouble("training.move-speed", 0.28),
                plugin.getConfig().getDouble("training.turn-degrees", 15.0),
                plugin.getConfig().getDouble("training.look-degrees", 10.0)
        );
    }

    public Map<String, Object> bind(String playerName) {
        Player player = Bukkit.getPlayerExact(playerName);
        if (player == null) throw new IllegalArgumentException("Player is not online: " + playerName);
        boundPlayer = player.getUniqueId();
        return Map.of("ok", true, "player", player.getName());
    }

    public Map<String, Object> reset(Goal newGoal, Profile newProfile, int newEpisode) {
        Player player = requirePlayer();
        this.goal = newGoal;
        this.profile = newProfile;
        this.episode = Math.max(0, newEpisode);
        this.step = 0;
        this.totalReward = 0.0;
        this.done = false;
        this.success = false;
        this.terminalReason = "";
        this.placedObsidian = 0;
        this.zombieDamageEvents = 0;
        this.zombieKills = 0;
        this.died = false;
        this.visitedCells.clear();

        if (player.isDead()) player.spigot().respawn();
        World world = trainingWorld();
        Location spawn = episodeSpawn(world, this.episode);
        resetPlayer(player, spawn);
        if (profile == Profile.CURRICULUM) applyCurriculum(player);
        visitedCells.add(cellKey(player.getLocation()));
        previousProgress = observationBuilder.progress(player, 0, maxSteps, 0, 0, 0, false, false);
        return state();
    }

    public void apply(Action action) {
        if (done) throw new IllegalStateException("Episode is done; call reset first");
        Player player = requirePlayer();
        step++;
        actionExecutor.execute(action, player, this);
    }

    public Map<String, Object> finishStep() {
        Player player = requirePlayer();
        boolean newCell = visitedCells.add(cellKey(player.getLocation()));
        ProgressSnapshot current = observationBuilder.progress(
                player, step, maxSteps, placedObsidian, zombieDamageEvents, zombieKills, newCell, died
        );
        if (previousProgress == null) previousProgress = current;
        RewardDecision decision = RewardEngine.evaluate(goal, previousProgress, current);
        totalReward += decision.reward();
        done = decision.done();
        success = decision.success();
        terminalReason = decision.terminalReason();
        previousProgress = current;

        LinkedHashMap<String, Object> out = new LinkedHashMap<>();
        out.put("reward", decision.reward());
        out.put("done", done);
        out.put("success", success);
        out.put("terminal_reason", terminalReason);
        out.put("observation", observationBuilder.observation(player, goal, step, totalReward, done, success, terminalReason));
        return out;
    }

    public Map<String, Object> state() {
        Player player = requirePlayer();
        LinkedHashMap<String, Object> out = new LinkedHashMap<>();
        out.put("bound_player", player.getName());
        out.put("goal", goal.name());
        out.put("profile", profile.name());
        out.put("episode", episode);
        out.put("step", step);
        out.put("max_steps", maxSteps);
        out.put("total_reward", totalReward);
        out.put("done", done);
        out.put("success", success);
        out.put("terminal_reason", terminalReason);
        out.put("observation", observationBuilder.observation(player, goal, step, totalReward, done, success, terminalReason));
        return out;
    }

    public Map<String, Object> status() {
        Player player = boundPlayer == null ? null : Bukkit.getPlayer(boundPlayer);
        return Map.of(
                "bound", player != null,
                "player", player == null ? "" : player.getName(),
                "goal", goal.name(),
                "profile", profile.name(),
                "step", step,
                "done", done
        );
    }

    public boolean isBound(Player player) {
        return boundPlayer != null && boundPlayer.equals(player.getUniqueId());
    }

    public void noteObsidianPlaced() {
        placedObsidian++;
    }

    public void noteZombieDamaged() {
        zombieDamageEvents++;
    }

    public void noteZombieKilled() {
        zombieKills++;
    }

    public void noteDeath() {
        died = true;
    }

    public int maxSteps() {
        return maxSteps;
    }

    private Player requirePlayer() {
        if (boundPlayer == null) throw new IllegalStateException("No player bound. Use /api/v1/bind or /rl bind <player>");
        Player player = Bukkit.getPlayer(boundPlayer);
        if (player == null || !player.isOnline()) throw new IllegalStateException("Bound player is not online");
        return player;
    }

    private World trainingWorld() {
        World existing = Bukkit.getWorld(worldName);
        if (existing != null) return existing;
        World created = Bukkit.createWorld(new WorldCreator(worldName).seed(worldSeed).generateStructures(true));
        if (created == null) throw new IllegalStateException("Could not create training world " + worldName);
        return created;
    }

    private Location episodeSpawn(World world, int episodeNumber) {
        int column = Math.floorMod(episodeNumber, 64);
        int row = Math.floorDiv(episodeNumber, 64);
        int baseX = column * episodeStride;
        int baseZ = row * episodeStride;
        for (int radius = 0; radius <= 64; radius += 8) {
            for (int dx = -radius; dx <= radius; dx += Math.max(8, radius * 2)) {
                for (int dz = -radius; dz <= radius; dz += Math.max(8, radius * 2)) {
                    int x = baseX + dx;
                    int z = baseZ + dz;
                    var ground = world.getHighestBlockAt(x, z, HeightMap.MOTION_BLOCKING_NO_LEAVES);
                    Material type = ground.getType();
                    if (type != Material.WATER && type != Material.LAVA && type != Material.MAGMA_BLOCK) {
                        return ground.getLocation().add(0.5, 1.0, 0.5);
                    }
                }
            }
        }
        var ground = world.getHighestBlockAt(baseX, baseZ, HeightMap.MOTION_BLOCKING_NO_LEAVES);
        return ground.getLocation().add(0.5, 1.0, 0.5);
    }

    private void resetPlayer(Player player, Location spawn) {
        player.getInventory().clear();
        player.setGameMode(GameMode.SURVIVAL);
        player.setHealth(20.0);
        player.setFoodLevel(20);
        player.setSaturation(5.0f);
        player.setExhaustion(0.0f);
        player.setRemainingAir(player.getMaximumAir());
        player.setFireTicks(0);
        player.setFallDistance(0.0f);
        player.setVelocity(new Vector(0, 0, 0));
        player.setLevel(0);
        player.setExp(0.0f);
        player.setTotalExperience(0);
        for (var effect : player.getActivePotionEffects()) player.removePotionEffect(effect.getType());
        player.teleport(spawn);
        player.setRespawnLocation(spawn, true);
    }

    private void applyCurriculum(Player player) {
        switch (goal) {
            case WOODEN_SWORD -> player.getInventory().addItem(new ItemStack(Material.OAK_LOG, 1));
            case DIAMOND -> player.getInventory().addItem(
                    new ItemStack(Material.IRON_PICKAXE, 1),
                    new ItemStack(Material.TORCH, 32),
                    new ItemStack(Material.BREAD, 8)
            );
            case NETHER_PORTAL -> player.getInventory().addItem(
                    new ItemStack(Material.OBSIDIAN, 10),
                    new ItemStack(Material.FLINT_AND_STEEL, 1)
            );
            case KILL_ZOMBIE -> {
                player.getInventory().addItem(new ItemStack(Material.WOODEN_SWORD, 1));
                Location probe = player.getLocation().clone().add(player.getLocation().getDirection().setY(0).normalize().multiply(6));
                var ground = player.getWorld().getHighestBlockAt(probe.getBlockX(), probe.getBlockZ(), HeightMap.MOTION_BLOCKING_NO_LEAVES);
                Location spawn = ground.getLocation().add(0.5, 1.0, 0.5);
                player.getWorld().spawn(spawn, Zombie.class, CreatureSpawnEvent.SpawnReason.CUSTOM, false, zombie -> { });
            }
        }
    }

    private String cellKey(Location location) {
        return Math.floorDiv(location.getBlockX(), 4) + ":" + Math.floorDiv(location.getBlockY(), 4) + ":" + Math.floorDiv(location.getBlockZ(), 4);
    }
}
