package dev.r4k5o.minecraftrl.session;

public record Ingredient(IngredientKind kind, int amount) {
    public Ingredient {
        if (amount <= 0) throw new IllegalArgumentException("Ingredient amount must be positive");
    }
}
