package dev.r4k5o.minecraftrl;

import dev.r4k5o.minecraftrl.command.RlCommand;
import dev.r4k5o.minecraftrl.listener.TrainingListener;
import dev.r4k5o.minecraftrl.server.RlHttpServer;
import dev.r4k5o.minecraftrl.session.TrainingSession;
import org.bukkit.command.PluginCommand;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.IOException;
import java.security.SecureRandom;
import java.util.HexFormat;

public final class MinecraftRLLabPlugin extends JavaPlugin {
    private RlHttpServer httpServer;
    private TrainingSession session;
    private String bridgeToken;

    @Override
    public void onEnable() {
        saveDefaultConfig();
        bridgeToken = ensureToken();
        session = new TrainingSession(this);
        getServer().getPluginManager().registerEvents(new TrainingListener(session), this);
        PluginCommand command = getCommand("rl");
        if (command != null) command.setExecutor(new RlCommand(this, session));
        try {
            httpServer = new RlHttpServer(this, session);
            httpServer.start();
        } catch (IOException e) {
            getLogger().severe("Could not start local RL bridge: " + e.getMessage());
            getServer().getPluginManager().disablePlugin(this);
            return;
        }
        getLogger().info("MinecraftRLLab enabled. Use /rl token to connect the Python client.");
    }

    @Override
    public void onDisable() {
        if (httpServer != null) httpServer.close();
    }

    public String bridgeToken() {
        return bridgeToken;
    }

    public TrainingSession session() {
        return session;
    }

    private String ensureToken() {
        String configured = getConfig().getString("bridge.token", "").trim();
        if (!configured.isEmpty()) return configured;
        byte[] random = new byte[24];
        new SecureRandom().nextBytes(random);
        String generated = HexFormat.of().formatHex(random);
        getConfig().set("bridge.token", generated);
        saveConfig();
        return generated;
    }
}
