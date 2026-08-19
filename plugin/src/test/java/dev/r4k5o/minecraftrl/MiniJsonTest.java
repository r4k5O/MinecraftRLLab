package dev.r4k5o.minecraftrl;

import dev.r4k5o.minecraftrl.protocol.MiniJson;
import java.util.List;
import java.util.Map;

final class MiniJsonTest {
    static void run() {
        Map<String, Object> source = Map.of(
            "text", "hello\nworld",
            "number", 12.5,
            "flag", true,
            "list", List.of("A", 2, false)
        );
        String json = MiniJson.stringify(source);
        Object parsed = MiniJson.parse(json);
        TestSuite.check(parsed instanceof Map<?, ?>, "root should be an object");
        Map<?, ?> map = (Map<?, ?>) parsed;
        TestSuite.check("hello\nworld".equals(map.get("text")), "escaped strings round-trip");
        TestSuite.check(Math.abs(((Number) map.get("number")).doubleValue() - 12.5) < 0.00001, "numbers round-trip");
        TestSuite.check(Boolean.TRUE.equals(map.get("flag")), "booleans round-trip");
        TestSuite.check(((List<?>) map.get("list")).size() == 3, "arrays round-trip");

        boolean rejected = false;
        try {
            MiniJson.parse("{\"a\":1} trailing");
        } catch (IllegalArgumentException expected) {
            rejected = true;
        }
        TestSuite.check(rejected, "trailing garbage must be rejected");
    }
}
