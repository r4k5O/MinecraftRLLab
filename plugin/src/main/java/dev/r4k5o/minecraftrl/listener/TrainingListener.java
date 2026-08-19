package dev.r4k5o.minecraftrl.listener;

import dev.r4k5o.minecraftrl.session.TrainingSession;
import org.bukkit.entity.Player;
import org.bukkit.entity.Zombie;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.EntityDeathEvent;
import org.bukkit.event.entity.PlayerDeathEvent;

public final class TrainingListener implements Listener {
    private final TrainingSession session;

    public TrainingListener(TrainingSession session) {
        this.session = session;
    }

    @EventHandler(ignoreCancelled = true)
    public void onDamage(EntityDamageByEntityEvent event) {
        if (event.getDamager() instanceof Player player && event.getEntity() instanceof Zombie && session.isBound(player)) {
            session.noteZombieDamaged();
        }
    }

    @EventHandler
    public void onDeath(EntityDeathEvent event) {
        if (!(event.getEntity() instanceof Zombie zombie)) return;
        Player killer = zombie.getKiller();
        if (killer != null && session.isBound(killer)) session.noteZombieKilled();
    }

    @EventHandler
    public void onPlayerDeath(PlayerDeathEvent event) {
        if (session.isBound(event.getEntity())) session.noteDeath();
    }
}
