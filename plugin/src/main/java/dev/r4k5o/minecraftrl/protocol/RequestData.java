package dev.r4k5o.minecraftrl.protocol;

import java.util.Locale;
import java.util.Map;

public final class RequestData {
    private final Map<String, Object> values;

    public RequestData(Map<String, Object> values) {
        this.values = values == null ? Map.of() : values;
    }

    public String requiredString(String key) {
        Object value = values.get(key);
        if (!(value instanceof String text) || text.isBlank()) {
            throw new IllegalArgumentException("Field '" + key + "' must be a non-empty string");
        }
        return text;
    }

    public String optionalString(String key, String fallback) {
        Object value = values.get(key);
        if (value == null) return fallback;
        if (!(value instanceof String text)) throw new IllegalArgumentException("Field '" + key + "' must be a string");
        return text;
    }

    public int optionalInt(String key, int fallback) {
        Object value = values.get(key);
        if (value == null) return fallback;
        if (!(value instanceof Number number)) throw new IllegalArgumentException("Field '" + key + "' must be an integer");
        double asDouble = number.doubleValue();
        int asInt = number.intValue();
        if (!Double.isFinite(asDouble) || asDouble != asInt) throw new IllegalArgumentException("Field '" + key + "' must be an integer");
        return asInt;
    }

    public <E extends Enum<E>> E requiredEnum(String key, Class<E> enumType) {
        return parseEnum(key, requiredString(key), enumType);
    }

    public <E extends Enum<E>> E optionalEnum(String key, E fallback, Class<E> enumType) {
        Object value = values.get(key);
        if (value == null) return fallback;
        if (!(value instanceof String text) || text.isBlank()) throw new IllegalArgumentException("Field '" + key + "' must be an enum string");
        return parseEnum(key, text, enumType);
    }

    private static <E extends Enum<E>> E parseEnum(String key, String value, Class<E> enumType) {
        try {
            return Enum.valueOf(enumType, value.trim().toUpperCase(Locale.ROOT));
        } catch (IllegalArgumentException ex) {
            throw new IllegalArgumentException("Invalid value for '" + key + "': " + value);
        }
    }
}
