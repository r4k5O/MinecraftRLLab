package dev.r4k5o.minecraftrl;

import dev.r4k5o.minecraftrl.session.BlockCategory;
import org.bukkit.Material;

final class BlockCategoryTest {
    static void run() {
        TestSuite.check(BlockCategory.id(Material.AIR) == BlockCategory.AIR, "air category");
        TestSuite.check(BlockCategory.id(Material.DIAMOND_ORE) == BlockCategory.DIAMOND_ORE, "diamond ore category");
        TestSuite.check(BlockCategory.id(Material.DEEPSLATE_DIAMOND_ORE) == BlockCategory.DIAMOND_ORE, "deepslate diamond category");
        TestSuite.check(BlockCategory.id(Material.NETHER_PORTAL) == BlockCategory.NETHER_PORTAL, "portal category");
        TestSuite.check(BlockCategory.id(Material.OAK_LOG) == BlockCategory.LOG, "log category");
    }
}
