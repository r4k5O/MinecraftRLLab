package dev.r4k5o.minecraftrl.session;

import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.PlayerInventory;

import java.util.Collection;

public final class InventoryOps {
    private InventoryOps() {}

    public static int count(PlayerInventory inventory, Material material) {
        int total = 0;
        for (ItemStack stack : inventory.getStorageContents()) {
            if (stack != null && stack.getType() == material) total += stack.getAmount();
        }
        return total;
    }

    public static int count(PlayerInventory inventory, IngredientKind kind) {
        int total = 0;
        for (ItemStack stack : inventory.getStorageContents()) {
            if (stack != null && MaterialGroups.matches(kind, stack.getType())) total += stack.getAmount();
        }
        return total;
    }

    public static boolean craft(Player player, RecipeSpec recipe) {
        PlayerInventory inventory = player.getInventory();
        for (Ingredient ingredient : recipe.ingredients()) {
            if (count(inventory, ingredient.kind()) < ingredient.amount()) return false;
        }
        for (Ingredient ingredient : recipe.ingredients()) {
            consume(inventory, ingredient.kind(), ingredient.amount());
        }
        inventory.addItem(new ItemStack(recipe.output(), recipe.outputCount()));
        return true;
    }

    public static void addDrops(Player player, Collection<ItemStack> drops) {
        for (ItemStack stack : drops) {
            if (stack == null || stack.getAmount() <= 0) continue;
            var leftovers = player.getInventory().addItem(stack);
            for (ItemStack leftover : leftovers.values()) {
                player.getWorld().dropItemNaturally(player.getLocation(), leftover);
            }
        }
    }

    private static void consume(PlayerInventory inventory, IngredientKind kind, int amount) {
        int remaining = amount;
        ItemStack[] contents = inventory.getStorageContents();
        for (int slot = 0; slot < contents.length && remaining > 0; slot++) {
            ItemStack stack = contents[slot];
            if (stack == null || !MaterialGroups.matches(kind, stack.getType())) continue;
            int take = Math.min(remaining, stack.getAmount());
            int left = stack.getAmount() - take;
            remaining -= take;
            if (left <= 0) inventory.setItem(slot, null);
            else stack.setAmount(left);
        }
        if (remaining != 0) throw new IllegalStateException("Ingredient accounting changed while crafting");
    }
}
