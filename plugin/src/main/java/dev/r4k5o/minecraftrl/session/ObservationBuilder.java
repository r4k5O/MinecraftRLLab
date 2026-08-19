package dev.r4k5o.minecraftrl.session;

import dev.r4k5o.minecraftrl.model.Goal;
import org.bukkit.FluidCollisionMode;
import org.bukkit.Material;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Player;
import org.bukkit.entity.Zombie;
import org.bukkit.inventory.PlayerInventory;
import org.bukkit.util.RayTraceResult;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class ObservationBuilder {
    public Map<String, Object> observation(Player player, Goal goal, int step, double totalReward,
                                           boolean done, boolean success, String terminalReason) {
        LinkedHashMap<String, Object> out = new LinkedHashMap<>();
        var loc = player.getLocation();
        var inv = player.getInventory();
        RayTraceResult blockHit = player.rayTraceBlocks(8.0, FluidCollisionMode.NEVER);
        RayTraceResult entityHit = player.rayTraceEntities(8);

        out.put("goal", goal.name());
        out.put("step", step);
        out.put("total_reward", totalReward);
        out.put("done", done);
        out.put("success", success);
        out.put("terminal_reason", terminalReason);
        out.put("health", player.getHealth());
        out.put("food", player.getFoodLevel());
        out.put("air", player.getRemainingAir());
        out.put("max_air", player.getMaximumAir());
        out.put("x", loc.getX());
        out.put("y", loc.getY());
        out.put("z", loc.getZ());
        out.put("yaw", loc.getYaw());
        out.put("pitch", loc.getPitch());
        out.put("on_ground", player.isOnGround());
        out.put("dimension", player.getWorld().getEnvironment().name());
        out.put("selected_slot", inv.getHeldItemSlot());
        out.put("inventory", inventoryMap(inv));
        out.put("local_grid", localGrid(player));
        out.put("target_block_category", blockCategory(blockHit));
        out.put("target_block_distance", blockDistance(player, blockHit));
        out.put("target_entity_category", entityCategory(entityHit));
        out.put("target_entity_distance", entityDistance(player, entityHit));
        out.put("nearby_zombies", player.getWorld().getNearbyEntitiesByType(Zombie.class, loc, 12.0).size());
        return out;
    }

    public ProgressSnapshot progress(Player player, int step, int maxSteps, int placedObsidian,
                                     int zombieDamageEvents, int zombieKills, boolean newCell, boolean died) {
        PlayerInventory inv = player.getInventory();
        RayTraceResult blockHit = player.rayTraceBlocks(8.0, FluidCollisionMode.NEVER);
        RayTraceResult entityHit = player.rayTraceEntities(8);
        return new ProgressSnapshot(
                player.getHealth(),
                InventoryOps.count(inv, IngredientKind.LOG),
                InventoryOps.count(inv, IngredientKind.PLANKS),
                InventoryOps.count(inv, Material.STICK),
                InventoryOps.count(inv, Material.WOODEN_SWORD),
                InventoryOps.count(inv, Material.IRON_PICKAXE),
                InventoryOps.count(inv, Material.DIAMOND),
                InventoryOps.count(inv, Material.OBSIDIAN),
                InventoryOps.count(inv, Material.FLINT_AND_STEEL),
                placedObsidian,
                zombieDamageEvents,
                zombieKills,
                blockHit != null && blockHit.getHitBlock() != null && BlockCategory.id(blockHit.getHitBlock().getType()) == BlockCategory.DIAMOND_ORE,
                entityHit != null && entityHit.getHitEntity() instanceof Zombie,
                portalNearby(player),
                newCell,
                died,
                step,
                maxSteps
        );
    }

    public boolean portalNearby(Player player) {
        var loc = player.getLocation();
        World world = player.getWorld();
        int bx = loc.getBlockX();
        int by = loc.getBlockY();
        int bz = loc.getBlockZ();
        for (int x = bx - 6; x <= bx + 6; x++) {
            for (int y = Math.max(world.getMinHeight(), by - 5); y <= Math.min(world.getMaxHeight() - 1, by + 5); y++) {
                for (int z = bz - 6; z <= bz + 6; z++) {
                    if (world.getBlockAt(x, y, z).getType() == Material.NETHER_PORTAL) return true;
                }
            }
        }
        return false;
    }

    private Map<String, Object> inventoryMap(PlayerInventory inv) {
        LinkedHashMap<String, Object> map = new LinkedHashMap<>();
        map.put("logs", InventoryOps.count(inv, IngredientKind.LOG));
        map.put("planks", InventoryOps.count(inv, IngredientKind.PLANKS));
        map.put("sticks", InventoryOps.count(inv, Material.STICK));
        map.put("crafting_table", InventoryOps.count(inv, Material.CRAFTING_TABLE));
        map.put("wooden_pickaxe", InventoryOps.count(inv, Material.WOODEN_PICKAXE));
        map.put("stone_pickaxe", InventoryOps.count(inv, Material.STONE_PICKAXE));
        map.put("cobblestone", InventoryOps.count(inv, IngredientKind.COBBLESTONE));
        map.put("raw_iron", InventoryOps.count(inv, Material.RAW_IRON));
        map.put("iron_ingot", InventoryOps.count(inv, Material.IRON_INGOT));
        map.put("iron_pickaxe", InventoryOps.count(inv, Material.IRON_PICKAXE));
        map.put("wooden_sword", InventoryOps.count(inv, Material.WOODEN_SWORD));
        map.put("diamond", InventoryOps.count(inv, Material.DIAMOND));
        map.put("obsidian", InventoryOps.count(inv, Material.OBSIDIAN));
        map.put("flint", InventoryOps.count(inv, Material.FLINT));
        map.put("flint_and_steel", InventoryOps.count(inv, Material.FLINT_AND_STEEL));
        return map;
    }

    private List<Integer> localGrid(Player player) {
        List<Integer> grid = new ArrayList<>(75);
        var loc = player.getLocation();
        World world = player.getWorld();
        int ox = loc.getBlockX();
        int oy = loc.getBlockY();
        int oz = loc.getBlockZ();
        for (int dy = -1; dy <= 1; dy++) {
            for (int dz = -2; dz <= 2; dz++) {
                for (int dx = -2; dx <= 2; dx++) {
                    int y = oy + dy;
                    if (y < world.getMinHeight() || y >= world.getMaxHeight()) grid.add(BlockCategory.SOLID);
                    else grid.add(BlockCategory.id(world.getBlockAt(ox + dx, y, oz + dz).getType()));
                }
            }
        }
        return grid;
    }

    private int blockCategory(RayTraceResult hit) {
        Block block = hit == null ? null : hit.getHitBlock();
        return block == null ? BlockCategory.AIR : BlockCategory.id(block.getType());
    }

    private double blockDistance(Player player, RayTraceResult hit) {
        if (hit == null || hit.getHitPosition() == null) return -1.0;
        return hit.getHitPosition().distance(player.getEyeLocation().toVector());
    }

    private int entityCategory(RayTraceResult hit) {
        Entity entity = hit == null ? null : hit.getHitEntity();
        if (entity == null) return 0;
        if (entity instanceof Zombie) return 1;
        if (entity instanceof Player) return 2;
        return 3;
    }

    private double entityDistance(Player player, RayTraceResult hit) {
        Entity entity = hit == null ? null : hit.getHitEntity();
        if (entity == null) return -1.0;
        return entity.getLocation().distance(player.getEyeLocation());
    }
}
