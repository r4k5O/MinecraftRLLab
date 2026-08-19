package dev.r4k5o.minecraftrl.session;

import dev.r4k5o.minecraftrl.model.Action;
import org.bukkit.FluidCollisionMode;
import org.bukkit.Material;
import org.bukkit.block.Block;
import org.bukkit.block.BlockFace;
import org.bukkit.entity.Entity;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.util.RayTraceResult;
import org.bukkit.util.Vector;

import java.util.Collection;
import java.util.Set;

public final class ActionExecutor {
    private static final Set<Material> NEVER_BREAK = Set.of(Material.BEDROCK, Material.BARRIER, Material.END_PORTAL, Material.END_PORTAL_FRAME);
    private final double moveSpeed;
    private final float turnDegrees;
    private final float lookDegrees;

    public ActionExecutor(double moveSpeed, double turnDegrees, double lookDegrees) {
        this.moveSpeed = moveSpeed;
        this.turnDegrees = (float) turnDegrees;
        this.lookDegrees = (float) lookDegrees;
    }

    public void execute(Action action, Player player, TrainingSession session) {
        RecipeSpec recipe = RecipeBook.forAction(action);
        if (recipe != null) {
            InventoryOps.craft(player, recipe);
            return;
        }
        switch (action) {
            case NOOP -> { }
            case MOVE_FORWARD -> move(player, 1.0, 0.0);
            case MOVE_BACKWARD -> move(player, -1.0, 0.0);
            case MOVE_LEFT -> move(player, 0.0, -1.0);
            case MOVE_RIGHT -> move(player, 0.0, 1.0);
            case JUMP -> jump(player);
            case TURN_LEFT -> rotate(player, -turnDegrees, 0.0f);
            case TURN_RIGHT -> rotate(player, turnDegrees, 0.0f);
            case LOOK_UP -> rotate(player, 0.0f, -lookDegrees);
            case LOOK_DOWN -> rotate(player, 0.0f, lookDegrees);
            case BREAK_BLOCK -> breakBlock(player);
            case PLACE_BLOCK -> placeBlock(player, session);
            case ATTACK -> attack(player);
            case USE -> use(player);
            case HOTBAR_0, HOTBAR_1, HOTBAR_2, HOTBAR_3, HOTBAR_4,
                    HOTBAR_5, HOTBAR_6, HOTBAR_7, HOTBAR_8 -> selectHotbar(player, action);
            default -> { }
        }
    }

    private void move(Player player, double forward, double strafe) {
        Vector look = player.getLocation().getDirection().setY(0);
        if (look.lengthSquared() < 1.0e-6) return;
        look.normalize();
        Vector right = new Vector(-look.getZ(), 0, look.getX());
        Vector horizontal = look.multiply(forward).add(right.multiply(strafe));
        if (horizontal.lengthSquared() > 1.0) horizontal.normalize();
        horizontal.multiply(moveSpeed);
        horizontal.setY(player.getVelocity().getY());
        player.setVelocity(horizontal);
    }

    private void jump(Player player) {
        if (!player.isOnGround()) return;
        Vector velocity = player.getVelocity();
        velocity.setY(0.42);
        player.setVelocity(velocity);
    }

    private void rotate(Player player, float yawDelta, float pitchDelta) {
        var loc = player.getLocation();
        float pitch = Math.max(-89.0f, Math.min(89.0f, loc.getPitch() + pitchDelta));
        player.setRotation(loc.getYaw() + yawDelta, pitch);
    }

    private void breakBlock(Player player) {
        RayTraceResult hit = player.rayTraceBlocks(6.0, FluidCollisionMode.NEVER);
        if (hit == null || hit.getHitBlock() == null) return;
        Block block = hit.getHitBlock();
        if (NEVER_BREAK.contains(block.getType()) || block.getType() == Material.AIR) return;
        ItemStack tool = player.getInventory().getItemInMainHand();
        Collection<ItemStack> drops = block.getDrops(tool, player);
        block.setType(Material.AIR, true);
        InventoryOps.addDrops(player, drops);
    }

    private void placeBlock(Player player, TrainingSession session) {
        ItemStack hand = player.getInventory().getItemInMainHand();
        if (hand == null || hand.getAmount() <= 0 || !hand.getType().isBlock()) return;
        RayTraceResult hit = player.rayTraceBlocks(6.0, FluidCollisionMode.NEVER);
        if (hit == null || hit.getHitBlock() == null || hit.getHitBlockFace() == null) return;
        Block place = hit.getHitBlock().getRelative(hit.getHitBlockFace());
        if (!place.isReplaceable()) return;
        Material type = hand.getType();
        place.setType(type, true);
        decrementMainHand(player);
        if (type == Material.OBSIDIAN) session.noteObsidianPlaced();
    }

    private void attack(Player player) {
        RayTraceResult hit = player.rayTraceEntities(4);
        if (hit == null) return;
        Entity entity = hit.getHitEntity();
        if (entity instanceof LivingEntity living && entity != player && !living.isDead()) {
            player.attack(living);
            player.swingMainHand();
        }
    }

    private void use(Player player) {
        ItemStack hand = player.getInventory().getItemInMainHand();
        if (hand == null || hand.getAmount() <= 0) return;
        if (hand.getType() == Material.FLINT_AND_STEEL) {
            RayTraceResult hit = player.rayTraceBlocks(6.0, FluidCollisionMode.NEVER);
            if (hit == null || hit.getHitBlock() == null) return;
            BlockFace face = hit.getHitBlockFace();
            if (face == null) return;
            Block fire = hit.getHitBlock().getRelative(face);
            if (fire.isReplaceable()) fire.setType(Material.FIRE, true);
            player.swingMainHand();
        }
    }

    private void selectHotbar(Player player, Action action) {
        int slot = Integer.parseInt(action.name().substring("HOTBAR_".length()));
        player.getInventory().setHeldItemSlot(slot);
    }

    private void decrementMainHand(Player player) {
        ItemStack hand = player.getInventory().getItemInMainHand();
        if (hand == null) return;
        if (hand.getAmount() <= 1) player.getInventory().setItemInMainHand(null);
        else hand.setAmount(hand.getAmount() - 1);
    }
}
