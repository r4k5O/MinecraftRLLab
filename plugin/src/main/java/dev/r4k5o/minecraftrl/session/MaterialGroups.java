package dev.r4k5o.minecraftrl.session;

import org.bukkit.Material;
import java.util.Locale;
import java.util.Set;

public final class MaterialGroups {
    private static final Set<Material> FUELS = Set.of(
            Material.COAL, Material.CHARCOAL,
            Material.OAK_LOG, Material.SPRUCE_LOG, Material.BIRCH_LOG,
            Material.JUNGLE_LOG, Material.ACACIA_LOG, Material.DARK_OAK_LOG,
            Material.MANGROVE_LOG, Material.CHERRY_LOG,
            Material.OAK_PLANKS, Material.SPRUCE_PLANKS, Material.BIRCH_PLANKS,
            Material.JUNGLE_PLANKS, Material.ACACIA_PLANKS, Material.DARK_OAK_PLANKS,
            Material.MANGROVE_PLANKS, Material.CHERRY_PLANKS
    );

    private MaterialGroups() {}

    public static boolean matches(IngredientKind kind, Material material) {
        String name = material.name().toUpperCase(Locale.ROOT);
        return switch (kind) {
            case LOG -> name.endsWith("_LOG") || name.endsWith("_STEM") || name.endsWith("_HYPHAE");
            case PLANKS -> name.endsWith("_PLANKS");
            case STICK -> material == Material.STICK;
            case COBBLESTONE -> material == Material.COBBLESTONE || material == Material.COBBLED_DEEPSLATE;
            case RAW_IRON -> material == Material.RAW_IRON;
            case IRON_INGOT -> material == Material.IRON_INGOT;
            case FLINT -> material == Material.FLINT;
            case FUEL -> FUELS.contains(material);
        };
    }
}
