package dev.r4k5o.minecraftrl.command;

import dev.r4k5o.minecraftrl.MinecraftRLLabPlugin;
import dev.r4k5o.minecraftrl.model.Goal;
import dev.r4k5o.minecraftrl.model.Profile;
import dev.r4k5o.minecraftrl.session.TrainingSession;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.jetbrains.annotations.NotNull;

import java.util.Locale;

public final class RlCommand implements CommandExecutor {
    private final MinecraftRLLabPlugin plugin;
    private final TrainingSession session;

    public RlCommand(MinecraftRLLabPlugin plugin, TrainingSession session) {
        this.plugin = plugin;
        this.session = session;
    }

    @Override
    public boolean onCommand(@NotNull CommandSender sender, @NotNull Command command, @NotNull String label, @NotNull String[] args) {
        if (args.length == 0 || args[0].equalsIgnoreCase("status")) {
            sender.sendMessage("MinecraftRLLab: " + session.status());
            return true;
        }
        try {
            switch (args[0].toLowerCase(Locale.ROOT)) {
                case "token" -> sender.sendMessage("RL bridge token: " + plugin.bridgeToken());
                case "bind" -> {
                    if (args.length < 2) return false;
                    session.bind(args[1]);
                    sender.sendMessage("Bound RL agent to " + args[1]);
                }
                case "reset" -> {
                    if (args.length < 2) return false;
                    Goal goal = Goal.valueOf(args[1].toUpperCase(Locale.ROOT));
                    Profile profile = args.length >= 3 ? Profile.valueOf(args[2].toUpperCase(Locale.ROOT)) : Profile.SURVIVAL;
                    int episode = args.length >= 4 ? Integer.parseInt(args[3]) : 0;
                    session.reset(goal, profile, episode);
                    sender.sendMessage("Reset RL episode " + episode + " for " + goal + " / " + profile);
                }
                default -> { return false; }
            }
            return true;
        } catch (RuntimeException e) {
            sender.sendMessage("RL error: " + (e.getMessage() == null ? e.getClass().getSimpleName() : e.getMessage()));
            return true;
        }
    }
}
