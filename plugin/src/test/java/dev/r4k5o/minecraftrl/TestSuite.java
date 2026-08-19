package dev.r4k5o.minecraftrl;

public final class TestSuite {
    private static int passed = 0;

    public static void main(String[] args) {
        run("MiniJson", MiniJsonTest::run);
        run("DomainEnums", DomainEnumsTest::run);
        run("RewardEngine", RewardEngineTest::run);
        run("RecipeBook", RecipeBookTest::run);
        run("BlockCategory", BlockCategoryTest::run);
        run("RequestData", RequestDataTest::run);
        System.out.println("Java tests passed: " + passed);
    }

    private static void run(String name, Runnable test) {
        try {
            test.run();
            passed++;
            System.out.println("PASS " + name);
        } catch (Throwable t) {
            System.err.println("FAIL " + name + ": " + t.getMessage());
            t.printStackTrace();
            System.exit(1);
        }
    }

    public static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
}
