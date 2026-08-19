package dev.r4k5o.minecraftrl;

import dev.r4k5o.minecraftrl.model.Goal;
import dev.r4k5o.minecraftrl.protocol.RequestData;

import java.util.Map;

public final class RequestDataTest {
    static void run() {
        var data = new RequestData(Map.of("player", "Oskar", "episode", 7, "goal", "DIAMOND"));
        TestSuite.check(data.requiredString("player").equals("Oskar"), "required string");
        TestSuite.check(data.optionalInt("episode", 0) == 7, "optional int");
        TestSuite.check(data.optionalInt("missing", 3) == 3, "default int");
        TestSuite.check(data.requiredEnum("goal", Goal.class) == Goal.DIAMOND, "enum parse");

        boolean missing = false;
        try { new RequestData(Map.of()).requiredString("player"); }
        catch (IllegalArgumentException e) { missing = e.getMessage().contains("player"); }
        TestSuite.check(missing, "missing field rejected");

        boolean badEnum = false;
        try { new RequestData(Map.of("goal", "NOPE")).requiredEnum("goal", Goal.class); }
        catch (IllegalArgumentException e) { badEnum = e.getMessage().contains("goal"); }
        TestSuite.check(badEnum, "bad enum rejected");
    }
}
