package dev.r4k5o.minecraftrl.session;

import dev.r4k5o.minecraftrl.model.Action;
import org.bukkit.Material;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

public final class RecipeBook {
    private static final Map<Action, RecipeSpec> RECIPES = new EnumMap<>(Action.class);

    static {
        put(Action.CRAFT_PLANKS, Material.OAK_PLANKS, 4, ing(IngredientKind.LOG, 1));
        put(Action.CRAFT_STICKS, Material.STICK, 4, ing(IngredientKind.PLANKS, 2));
        put(Action.CRAFT_CRAFTING_TABLE, Material.CRAFTING_TABLE, 1, ing(IngredientKind.PLANKS, 4));
        put(Action.CRAFT_WOODEN_PICKAXE, Material.WOODEN_PICKAXE, 1,
                ing(IngredientKind.PLANKS, 3), ing(IngredientKind.STICK, 2));
        put(Action.CRAFT_STONE_PICKAXE, Material.STONE_PICKAXE, 1,
                ing(IngredientKind.COBBLESTONE, 3), ing(IngredientKind.STICK, 2));
        put(Action.CRAFT_FURNACE, Material.FURNACE, 1, ing(IngredientKind.COBBLESTONE, 8));
        put(Action.SMELT_IRON, Material.IRON_INGOT, 1,
                ing(IngredientKind.RAW_IRON, 1), ing(IngredientKind.FUEL, 1));
        put(Action.CRAFT_IRON_PICKAXE, Material.IRON_PICKAXE, 1,
                ing(IngredientKind.IRON_INGOT, 3), ing(IngredientKind.STICK, 2));
        put(Action.CRAFT_WOODEN_SWORD, Material.WOODEN_SWORD, 1,
                ing(IngredientKind.PLANKS, 2), ing(IngredientKind.STICK, 1));
        put(Action.CRAFT_FLINT_AND_STEEL, Material.FLINT_AND_STEEL, 1,
                ing(IngredientKind.IRON_INGOT, 1), ing(IngredientKind.FLINT, 1));
    }

    private RecipeBook() {}

    public static RecipeSpec forAction(Action action) {
        return RECIPES.get(action);
    }

    private static Ingredient ing(IngredientKind kind, int amount) {
        return new Ingredient(kind, amount);
    }

    private static void put(Action action, Material output, int count, Ingredient... ingredients) {
        RECIPES.put(action, new RecipeSpec(List.of(ingredients), output, count));
    }
}
