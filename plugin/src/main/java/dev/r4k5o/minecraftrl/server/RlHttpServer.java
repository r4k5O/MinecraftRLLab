package dev.r4k5o.minecraftrl.server;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import dev.r4k5o.minecraftrl.MinecraftRLLabPlugin;
import dev.r4k5o.minecraftrl.model.Action;
import dev.r4k5o.minecraftrl.model.Goal;
import dev.r4k5o.minecraftrl.model.Profile;
import dev.r4k5o.minecraftrl.protocol.MiniJson;
import dev.r4k5o.minecraftrl.protocol.RequestData;
import dev.r4k5o.minecraftrl.session.TrainingSession;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class RlHttpServer implements AutoCloseable {
    private static final int MAX_BODY_BYTES = 64 * 1024;
    private final MinecraftRLLabPlugin plugin;
    private final TrainingSession session;
    private final MainThread mainThread;
    private final long stepDelayTicks;
    private HttpServer server;
    private ExecutorService executor;

    public RlHttpServer(MinecraftRLLabPlugin plugin, TrainingSession session) {
        this.plugin = plugin;
        this.session = session;
        this.mainThread = new MainThread(plugin, plugin.getConfig().getLong("bridge.request-timeout-seconds", 10));
        this.stepDelayTicks = plugin.getConfig().getLong("training.step-delay-ticks", 3);
    }

    public void start() throws IOException {
        String host = plugin.getConfig().getString("bridge.host", "127.0.0.1");
        int port = plugin.getConfig().getInt("bridge.port", 8765);
        server = HttpServer.create(new InetSocketAddress(host, port), 16);
        server.createContext("/api/v1/", this::handle);
        executor = Executors.newFixedThreadPool(2, runnable -> {
            Thread thread = new Thread(runnable, "minecraft-rl-http");
            thread.setDaemon(true);
            return thread;
        });
        server.setExecutor(executor);
        server.start();
        plugin.getLogger().info("RL bridge listening on http://" + host + ":" + port + "/api/v1/");
    }

    private void handle(HttpExchange exchange) throws IOException {
        try {
            String path = exchange.getRequestURI().getPath();
            String method = exchange.getRequestMethod();
            if (path.equals("/api/v1/health")) {
                requireMethod(method, "GET");
                send(exchange, 200, Map.of("ok", true, "plugin", "MinecraftRLLab", "version", plugin.getPluginMeta().getVersion()));
                return;
            }
            if (!authorized(exchange)) {
                send(exchange, 401, Map.of("ok", false, "error", "unauthorized"));
                return;
            }
            Map<String, Object> response = switch (path) {
                case "/api/v1/info" -> {
                    requireMethod(method, "GET");
                    yield mainThread.call(this::info);
                }
                case "/api/v1/bind" -> {
                    requireMethod(method, "POST");
                    RequestData data = request(exchange);
                    yield mainThread.call(() -> session.bind(data.requiredString("player")));
                }
                case "/api/v1/reset" -> {
                    requireMethod(method, "POST");
                    RequestData data = request(exchange);
                    Goal goal = data.optionalEnum("goal", Goal.WOODEN_SWORD, Goal.class);
                    Profile profile = data.optionalEnum("profile", Profile.SURVIVAL, Profile.class);
                    int episode = data.optionalInt("episode", 0);
                    yield mainThread.call(() -> session.reset(goal, profile, episode));
                }
                case "/api/v1/state" -> {
                    requireMethod(method, "GET");
                    yield mainThread.call(session::state);
                }
                case "/api/v1/step" -> {
                    requireMethod(method, "POST");
                    RequestData data = request(exchange);
                    Action action = data.requiredEnum("action", Action.class);
                    yield mainThread.step(() -> session.apply(action), session::finishStep, stepDelayTicks);
                }
                default -> throw new HttpProblem(404, "not_found");
            };
            send(exchange, 200, response);
        } catch (HttpProblem e) {
            send(exchange, e.status, Map.of("ok", false, "error", e.getMessage()));
        } catch (IllegalArgumentException | IllegalStateException e) {
            send(exchange, 400, Map.of("ok", false, "error", safeMessage(e)));
        } catch (Throwable t) {
            plugin.getLogger().warning("RL HTTP error: " + t);
            send(exchange, 500, Map.of("ok", false, "error", "internal_error"));
        } finally {
            exchange.close();
        }
    }

    private Map<String, Object> info() {
        LinkedHashMap<String, Object> out = new LinkedHashMap<>();
        out.put("plugin", "MinecraftRLLab");
        out.put("version", plugin.getPluginMeta().getVersion());
        out.put("minecraft", "26.2");
        out.put("goals", Arrays.stream(Goal.values()).map(Enum::name).toList());
        out.put("profiles", Arrays.stream(Profile.values()).map(Enum::name).toList());
        out.put("actions", Arrays.stream(Action.values()).map(Enum::name).toList());
        out.put("status", session.status());
        return out;
    }

    private RequestData request(HttpExchange exchange) throws IOException {
        byte[] bytes = exchange.getRequestBody().readNBytes(MAX_BODY_BYTES + 1);
        if (bytes.length > MAX_BODY_BYTES) throw new HttpProblem(413, "request_too_large");
        String text = new String(bytes, StandardCharsets.UTF_8);
        Map<String, Object> object = text.isBlank() ? Map.of() : MiniJson.parseObject(text);
        return new RequestData(object);
    }

    private boolean authorized(HttpExchange exchange) {
        String supplied = exchange.getRequestHeaders().getFirst("X-RL-Token");
        if (supplied == null) return false;
        byte[] expected = plugin.bridgeToken().getBytes(StandardCharsets.UTF_8);
        byte[] actual = supplied.getBytes(StandardCharsets.UTF_8);
        return MessageDigest.isEqual(expected, actual);
    }

    private void requireMethod(String actual, String expected) {
        if (!expected.equals(actual)) throw new HttpProblem(405, "method_not_allowed");
    }

    private static String safeMessage(Throwable t) {
        return t.getMessage() == null || t.getMessage().isBlank() ? "bad_request" : t.getMessage();
    }

    private void send(HttpExchange exchange, int status, Map<String, Object> body) throws IOException {
        byte[] bytes = MiniJson.stringify(body).getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        exchange.getResponseHeaders().set("Cache-Control", "no-store");
        exchange.sendResponseHeaders(status, bytes.length);
        exchange.getResponseBody().write(bytes);
    }

    @Override
    public void close() {
        if (server != null) server.stop(0);
        if (executor != null) executor.shutdownNow();
    }

    private static final class HttpProblem extends RuntimeException {
        private final int status;
        private HttpProblem(int status, String message) {
            super(message);
            this.status = status;
        }
    }
}
