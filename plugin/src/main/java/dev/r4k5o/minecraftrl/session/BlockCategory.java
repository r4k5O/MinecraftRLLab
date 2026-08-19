package dev.r4k5o.minecraftrl.session;

import org.bukkit.Material;

public final class BlockCategory {
    public static final int AIR = 0;
    public static final int SOLID = 1;
    public static final int LOG = 2;
    public static final int LEAVES = 3;
    public static final int DIRT_GRASS = 4;
    public static final int STONE = 5;
    public static final int COAL_ORE = 6;
    public static final int IRON_ORE = 7;
    public static final int DIAMOND_ORE = 8;
    public static final int WATER = 9;
    public static final int LAVA = 10;
    public static final int OBSIDIAN = 11;
    public static final int CRAFTING_TABLE = 12;
    public static final int NETHER_PORTAL = 13;
    public static final int OTHER_ORE = 14;
    public static final int OTHER = 15;
    public static final int MAX_ID = OTHER;

    private BlockCategory() {}

    public static int id(Material material) {
        if (material == null) return AIR;
        String name = material.name();
        if (name.equals("AIR") || name.equals("CAVE_AIR") || name.equals("VOID_AIR")) return AIR;
        if (name.endsWith("_LOG") || name.endsWith("_STEM") || name.endsWith("_HYPHAE")) return LOG;
        if (name.endsWith("_LEAVES") || name.equals("NETHER_WART_BLOCK") || name.equals("WARPED_WART_BLOCK")) return LEAVES;
        if (name.equals("GRASS_BLOCK") || name.equals("DIRT") || name.equals("COARSE_DIRT") || name.equals("ROOTED_DIRT") || name.equals("PODZOL")) return DIRT_GRASS;
        if (name.equals("STONE") || name.equals("DEEPSLATE") || name.equals("TUFF") || name.equals("GRANITE") || name.equals("DIORITE") || name.equals("ANDESITE")) return STONE;
        if (name.equals("COAL_ORE") || name.equals("DEEPSLATE_COAL_ORE")) return COAL_ORE;
        if (name.equals("IRON_ORE") || name.equals("DEEPSLATE_IRON_ORE")) return IRON_ORE;
        if (name.equals("DIAMOND_ORE") || name.equals("DEEPSLATE_DIAMOND_ORE")) return DIAMOND_ORE;
        if (name.equals("WATER")) return WATER;
        if (name.equals("LAVA")) return LAVA;
        if (name.equals("OBSIDIAN") || name.equals("CRYING_OBSIDIAN")) return OBSIDIAN;
        if (name.equals("CRAFTING_TABLE")) return CRAFTING_TABLE;
        if (name.equals("NETHER_PORTAL")) return NETHER_PORTAL;
        if (name.endsWith("_ORE")) return OTHER_ORE;
        if (material.isBlock()) return SOLID;
        return OTHER;
    }
}
