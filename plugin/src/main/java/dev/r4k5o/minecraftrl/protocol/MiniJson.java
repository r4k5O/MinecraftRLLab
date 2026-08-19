package dev.r4k5o.minecraftrl.protocol;

import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class MiniJson {
    private MiniJson() {}

    public static Object parse(String json) {
        if (json == null) throw new IllegalArgumentException("JSON must not be null");
        Parser parser = new Parser(json);
        Object value = parser.parseValue();
        parser.skipWhitespace();
        if (!parser.atEnd()) throw parser.error("Trailing data");
        return value;
    }

    @SuppressWarnings("unchecked")
    public static Map<String, Object> parseObject(String json) {
        Object value = parse(json);
        if (!(value instanceof Map<?, ?> map)) {
            throw new IllegalArgumentException("JSON root must be an object");
        }
        return (Map<String, Object>) map;
    }

    public static String stringify(Object value) {
        StringBuilder out = new StringBuilder();
        writeValue(out, value);
        return out.toString();
    }

    private static void writeValue(StringBuilder out, Object value) {
        if (value == null) {
            out.append("null");
        } else if (value instanceof String s) {
            writeString(out, s);
        } else if (value instanceof Character c) {
            writeString(out, c.toString());
        } else if (value instanceof Boolean || value instanceof Byte || value instanceof Short
                || value instanceof Integer || value instanceof Long) {
            out.append(value);
        } else if (value instanceof Number n) {
            double d = n.doubleValue();
            if (!Double.isFinite(d)) throw new IllegalArgumentException("Non-finite numbers are not JSON");
            out.append(value);
        } else if (value instanceof Enum<?> e) {
            writeString(out, e.name());
        } else if (value instanceof Map<?, ?> map) {
            out.append('{');
            boolean first = true;
            for (Map.Entry<?, ?> entry : map.entrySet()) {
                if (!(entry.getKey() instanceof String key)) {
                    throw new IllegalArgumentException("JSON object keys must be strings");
                }
                if (!first) out.append(',');
                first = false;
                writeString(out, key);
                out.append(':');
                writeValue(out, entry.getValue());
            }
            out.append('}');
        } else if (value instanceof Iterable<?> iterable) {
            out.append('[');
            boolean first = true;
            for (Object item : iterable) {
                if (!first) out.append(',');
                first = false;
                writeValue(out, item);
            }
            out.append(']');
        } else if (value.getClass().isArray()) {
            out.append('[');
            int length = Array.getLength(value);
            for (int i = 0; i < length; i++) {
                if (i > 0) out.append(',');
                writeValue(out, Array.get(value, i));
            }
            out.append(']');
        } else {
            throw new IllegalArgumentException("Unsupported JSON type: " + value.getClass().getName());
        }
    }

    private static void writeString(StringBuilder out, String value) {
        out.append('"');
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            switch (c) {
                case '"' -> out.append("\\\"");
                case '\\' -> out.append("\\\\");
                case '\b' -> out.append("\\b");
                case '\f' -> out.append("\\f");
                case '\n' -> out.append("\\n");
                case '\r' -> out.append("\\r");
                case '\t' -> out.append("\\t");
                default -> {
                    if (c < 0x20) out.append(String.format("\\u%04x", (int) c));
                    else out.append(c);
                }
            }
        }
        out.append('"');
    }

    private static final class Parser {
        private final String text;
        private int index;

        private Parser(String text) {
            this.text = text;
        }

        private Object parseValue() {
            skipWhitespace();
            if (atEnd()) throw error("Expected value");
            return switch (text.charAt(index)) {
                case '{' -> parseObject();
                case '[' -> parseArray();
                case '"' -> parseString();
                case 't' -> parseLiteral("true", Boolean.TRUE);
                case 'f' -> parseLiteral("false", Boolean.FALSE);
                case 'n' -> parseLiteral("null", null);
                default -> parseNumber();
            };
        }

        private Map<String, Object> parseObject() {
            expect('{');
            LinkedHashMap<String, Object> map = new LinkedHashMap<>();
            skipWhitespace();
            if (consume('}')) return map;
            while (true) {
                skipWhitespace();
                if (atEnd() || text.charAt(index) != '"') throw error("Expected string key");
                String key = parseString();
                skipWhitespace();
                expect(':');
                map.put(key, parseValue());
                skipWhitespace();
                if (consume('}')) return map;
                expect(',');
            }
        }

        private List<Object> parseArray() {
            expect('[');
            ArrayList<Object> list = new ArrayList<>();
            skipWhitespace();
            if (consume(']')) return list;
            while (true) {
                list.add(parseValue());
                skipWhitespace();
                if (consume(']')) return list;
                expect(',');
            }
        }

        private String parseString() {
            expect('"');
            StringBuilder out = new StringBuilder();
            while (!atEnd()) {
                char c = text.charAt(index++);
                if (c == '"') return out.toString();
                if (c == '\\') {
                    if (atEnd()) throw error("Unterminated escape");
                    char e = text.charAt(index++);
                    switch (e) {
                        case '"' -> out.append('"');
                        case '\\' -> out.append('\\');
                        case '/' -> out.append('/');
                        case 'b' -> out.append('\b');
                        case 'f' -> out.append('\f');
                        case 'n' -> out.append('\n');
                        case 'r' -> out.append('\r');
                        case 't' -> out.append('\t');
                        case 'u' -> out.append(parseUnicode());
                        default -> throw error("Invalid escape: \\" + e);
                    }
                } else {
                    if (c < 0x20) throw error("Control character in string");
                    out.append(c);
                }
            }
            throw error("Unterminated string");
        }

        private char parseUnicode() {
            if (index + 4 > text.length()) throw error("Short unicode escape");
            String hex = text.substring(index, index + 4);
            index += 4;
            try {
                return (char) Integer.parseInt(hex, 16);
            } catch (NumberFormatException e) {
                throw error("Invalid unicode escape");
            }
        }

        private Object parseLiteral(String literal, Object value) {
            if (!text.startsWith(literal, index)) throw error("Expected " + literal);
            index += literal.length();
            return value;
        }

        private Number parseNumber() {
            int start = index;
            if (consume('-')) {}
            int digits = 0;
            while (!atEnd() && Character.isDigit(text.charAt(index))) {
                index++;
                digits++;
            }
            if (digits == 0) throw error("Expected number");
            boolean decimal = false;
            if (consume('.')) {
                decimal = true;
                int fractionDigits = 0;
                while (!atEnd() && Character.isDigit(text.charAt(index))) {
                    index++;
                    fractionDigits++;
                }
                if (fractionDigits == 0) throw error("Expected digits after decimal point");
            }
            if (!atEnd() && (text.charAt(index) == 'e' || text.charAt(index) == 'E')) {
                decimal = true;
                index++;
                if (!atEnd() && (text.charAt(index) == '+' || text.charAt(index) == '-')) index++;
                int exponentDigits = 0;
                while (!atEnd() && Character.isDigit(text.charAt(index))) {
                    index++;
                    exponentDigits++;
                }
                if (exponentDigits == 0) throw error("Expected exponent digits");
            }
            String raw = text.substring(start, index);
            try {
                if (!decimal) {
                    long l = Long.parseLong(raw);
                    if (l >= Integer.MIN_VALUE && l <= Integer.MAX_VALUE) return (int) l;
                    return l;
                }
                double d = Double.parseDouble(raw);
                if (!Double.isFinite(d)) throw error("Non-finite number");
                return d;
            } catch (NumberFormatException e) {
                throw error("Invalid number");
            }
        }

        private void expect(char expected) {
            skipWhitespace();
            if (atEnd() || text.charAt(index) != expected) throw error("Expected '" + expected + "'");
            index++;
        }

        private boolean consume(char c) {
            if (!atEnd() && text.charAt(index) == c) {
                index++;
                return true;
            }
            return false;
        }

        private void skipWhitespace() {
            while (!atEnd()) {
                char c = text.charAt(index);
                if (c == ' ' || c == '\n' || c == '\r' || c == '\t') index++;
                else break;
            }
        }

        private boolean atEnd() {
            return index >= text.length();
        }

        private IllegalArgumentException error(String message) {
            return new IllegalArgumentException(message + " at index " + index);
        }
    }
}
