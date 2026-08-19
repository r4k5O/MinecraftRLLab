package dev.r4k5o.minecraftrl.server;

import org.bukkit.Bukkit;
import org.bukkit.plugin.java.JavaPlugin;

import java.util.concurrent.Callable;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;

public final class MainThread {
    private final JavaPlugin plugin;
    private final long timeoutSeconds;

    public MainThread(JavaPlugin plugin, long timeoutSeconds) {
        this.plugin = plugin;
        this.timeoutSeconds = Math.max(1, timeoutSeconds);
    }

    public <T> T call(Callable<T> task) {
        if (Bukkit.isPrimaryThread()) return invoke(task);
        CompletableFuture<T> future = new CompletableFuture<>();
        Bukkit.getScheduler().runTask(plugin, () -> complete(future, task));
        return await(future);
    }

    public <T> T step(Runnable action, Supplier<T> capture, long delayTicks) {
        CompletableFuture<T> future = new CompletableFuture<>();
        Runnable start = () -> {
            try {
                action.run();
                Bukkit.getScheduler().runTaskLater(plugin, () -> {
                    try { future.complete(capture.get()); }
                    catch (Throwable t) { future.completeExceptionally(t); }
                }, Math.max(1, delayTicks));
            } catch (Throwable t) {
                future.completeExceptionally(t);
            }
        };
        if (Bukkit.isPrimaryThread()) start.run();
        else Bukkit.getScheduler().runTask(plugin, start);
        return await(future);
    }

    private <T> void complete(CompletableFuture<T> future, Callable<T> task) {
        try { future.complete(task.call()); }
        catch (Throwable t) { future.completeExceptionally(t); }
    }

    private <T> T invoke(Callable<T> task) {
        try { return task.call(); }
        catch (RuntimeException e) { throw e; }
        catch (Exception e) { throw new RuntimeException(e); }
    }

    private <T> T await(CompletableFuture<T> future) {
        try {
            return future.get(timeoutSeconds, TimeUnit.SECONDS);
        } catch (Exception e) {
            Throwable cause = e.getCause();
            if (cause instanceof RuntimeException runtime) throw runtime;
            throw new RuntimeException(cause == null ? e : cause);
        }
    }
}
