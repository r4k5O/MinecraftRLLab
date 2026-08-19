package dev.r4k5o.minecraftrl.session;

import org.bukkit.Material;
import java.util.List;

public record RecipeSpec(List<Ingredient> ingredients, Material output, int outputCount) {
    public RecipeSpec {
        ingredients = List.copyOf(ingredients);
        if (outputCount <= 0) throw new IllegalArgumentException("Output count must be positive");
    }

    public int amountOf(IngredientKind kind) {
        return ingredients.stream()
                .filter(i -> i.kind() == kind)
                .mapToInt(Ingredient::amount)
                .sum();
    }
}
