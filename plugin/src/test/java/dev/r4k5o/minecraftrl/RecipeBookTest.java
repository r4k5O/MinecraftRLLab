package dev.r4k5o.minecraftrl;

import dev.r4k5o.minecraftrl.model.Action;
import dev.r4k5o.minecraftrl.session.IngredientKind;
import dev.r4k5o.minecraftrl.session.MaterialGroups;
import dev.r4k5o.minecraftrl.session.RecipeBook;
import dev.r4k5o.minecraftrl.session.RecipeSpec;
import org.bukkit.Material;

final class RecipeBookTest {
    static void run() {
        RecipeSpec sword = RecipeBook.forAction(Action.CRAFT_WOODEN_SWORD);
        TestSuite.check(sword != null, "wooden sword recipe must exist");
        TestSuite.check(sword.output() == Material.WOODEN_SWORD, "wooden sword recipe output");
        TestSuite.check(sword.outputCount() == 1, "wooden sword output count");
        TestSuite.check(sword.amountOf(IngredientKind.PLANKS) == 2, "wooden sword needs two planks");
        TestSuite.check(sword.amountOf(IngredientKind.STICK) == 1, "wooden sword needs one stick");

        RecipeSpec smelt = RecipeBook.forAction(Action.SMELT_IRON);
        TestSuite.check(smelt.output() == Material.IRON_INGOT, "smelting outputs iron ingot");
        TestSuite.check(smelt.amountOf(IngredientKind.RAW_IRON) == 1, "smelting needs raw iron");
        TestSuite.check(smelt.amountOf(IngredientKind.FUEL) == 1, "smelting needs fuel");

        TestSuite.check(MaterialGroups.matches(IngredientKind.LOG, Material.OAK_LOG), "oak log should count as log");
        TestSuite.check(MaterialGroups.matches(IngredientKind.PLANKS, Material.SPRUCE_PLANKS), "spruce planks should count as planks");
        TestSuite.check(MaterialGroups.matches(IngredientKind.FUEL, Material.COAL), "coal should count as fuel");
        TestSuite.check(!MaterialGroups.matches(IngredientKind.PLANKS, Material.STONE), "stone is not planks");
    }
}
