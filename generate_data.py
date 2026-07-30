"""
generate_data.py
-----------------
One-time script used to build data/foods.csv and data/substitutions.csv.

Nutrition values are per 100g (or 100ml for liquids) and are curated,
representative values in the style of the USDA FoodData Central (FDC)
database. They are meant for demonstration/learning purposes rather than
clinical use -- see README.md for notes on wiring up the real USDA FDC API.

Running this script regenerates both CSV files from the FOODS / SUBS
python structures below, so the dataset is easy to extend: add a row to
FOODS, add an edge to SUBS, rerun.
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Each food: (name, category, calories, fiber_g, sugar_g, protein_g, sodium_mg, carbs_g)
# All values per 100 g / 100 ml.
FOODS = [
    # ---- Grains & breads ----
    ("White bread", "Grains", 265, 2.7, 5.0, 9.0, 491, 49.0),
    ("White rice, cooked", "Grains", 130, 0.4, 0.1, 2.7, 1, 28.0),
    ("Regular pasta, cooked", "Grains", 158, 1.8, 0.6, 5.8, 1, 31.0),
    ("Instant ramen noodles", "Grains", 436, 2.0, 2.0, 10.0, 1731, 62.0),
    ("Frosted corn flakes cereal", "Grains", 375, 1.0, 37.0, 4.0, 460, 88.0),
    ("Plain bagel", "Grains", 250, 2.0, 5.0, 10.0, 460, 49.0),
    ("Pancakes, from mix", "Grains", 227, 1.4, 6.0, 6.0, 439, 28.0),
    ("Butter croissant", "Grains", 406, 2.6, 8.0, 8.0, 447, 46.0),
    ("Flour tortilla", "Grains", 304, 2.7, 2.0, 8.0, 641, 51.0),
    ("Whole wheat bread", "Grains", 247, 6.8, 6.0, 13.0, 400, 41.0),
    ("Brown rice, cooked", "Grains", 112, 1.8, 0.2, 2.6, 5, 24.0),
    ("Whole wheat pasta, cooked", "Grains", 124, 3.9, 0.8, 5.3, 4, 26.0),
    ("Quinoa, cooked", "Grains", 120, 2.8, 0.9, 4.4, 7, 21.0),
    ("Whole grain noodle soup, low sodium broth", "Grains", 190, 3.0, 1.0, 8.0, 380, 34.0),
    ("Bran flakes cereal", "Grains", 320, 18.0, 12.0, 9.0, 590, 81.0),
    ("Whole wheat bagel", "Grains", 245, 5.0, 5.0, 10.0, 430, 47.0),
    ("Whole wheat pancakes", "Grains", 178, 3.0, 4.0, 7.0, 380, 22.0),
    ("Whole grain English muffin", "Grains", 155, 4.4, 2.0, 6.0, 320, 30.0),
    ("Whole wheat tortilla", "Grains", 250, 6.0, 1.0, 8.0, 380, 42.0),

    # ---- Dairy ----
    ("Whole milk", "Dairy", 61, 0.0, 5.0, 3.2, 40, 4.8),
    ("Vanilla ice cream", "Dairy", 207, 0.7, 21.0, 3.5, 80, 24.0),
    ("Sour cream", "Dairy", 193, 0.0, 2.9, 2.4, 47, 4.6),
    ("Cream cheese", "Dairy", 342, 0.0, 3.2, 6.0, 321, 4.0),
    ("American cheese slices", "Dairy", 375, 0.0, 6.0, 18.0, 1560, 8.0),
    ("Sweetened whole milk yogurt", "Dairy", 122, 0.0, 17.0, 5.0, 70, 19.0),
    ("Skim milk", "Dairy", 34, 0.0, 5.0, 3.4, 42, 5.0),
    ("Low-fat frozen yogurt", "Dairy", 127, 0.0, 21.0, 3.0, 63, 24.0),
    ("Plain nonfat Greek yogurt", "Dairy", 59, 0.0, 3.6, 10.0, 36, 3.6),
    ("Light cream cheese", "Dairy", 220, 0.0, 4.0, 8.0, 380, 6.0),
    ("Reduced-sodium Swiss cheese", "Dairy", 380, 0.0, 1.0, 27.0, 710, 5.0),

    # ---- Protein / meats ----
    ("Ground beef (80/20)", "Protein", 254, 0.0, 0.0, 17.0, 75, 0.0),
    ("Bacon", "Protein", 541, 0.0, 0.0, 37.0, 1717, 1.4),
    ("Breaded fried chicken", "Protein", 246, 0.5, 0.8, 19.0, 480, 8.0),
    ("Hot dog", "Protein", 290, 0.0, 2.0, 10.0, 970, 4.0),
    ("Deli ham, processed", "Protein", 145, 0.0, 1.6, 18.0, 1200, 2.0),
    ("Salami", "Protein", 336, 0.0, 0.3, 22.0, 1890, 1.6),
    ("Regular pork sausage", "Protein", 301, 0.0, 1.0, 12.0, 890, 3.0),
    ("Ground turkey (93/7)", "Protein", 176, 0.0, 0.0, 20.0, 70, 0.0),
    ("Turkey bacon", "Protein", 271, 0.0, 1.0, 22.0, 1350, 3.0),
    ("Grilled chicken breast", "Protein", 165, 0.0, 0.0, 31.0, 74, 0.0),
    ("Chicken sausage", "Protein", 160, 0.0, 1.0, 15.0, 550, 3.0),
    ("Low-sodium deli turkey", "Protein", 104, 0.0, 1.0, 17.0, 450, 2.0),
    ("Lean turkey deli slices", "Protein", 130, 0.0, 0.5, 20.0, 700, 2.0),

    # ---- Snacks ----
    ("Potato chips", "Snacks", 536, 4.4, 0.3, 7.0, 525, 53.0),
    ("Buttered movie popcorn", "Snacks", 431, 8.0, 0.5, 6.0, 590, 48.0),
    ("Milk chocolate candy bar", "Snacks", 535, 3.0, 51.0, 7.6, 79, 59.0),
    ("Salted pretzels", "Snacks", 380, 2.6, 2.0, 10.0, 1240, 79.0),
    ("Chocolate chip cookies", "Snacks", 488, 2.6, 34.0, 5.5, 348, 68.0),
    ("Glazed donut", "Snacks", 452, 1.4, 22.0, 5.0, 373, 51.0),
    ("Nacho cheese tortilla chips", "Snacks", 498, 3.9, 2.0, 7.0, 700, 60.0),
    ("Baked potato chips", "Snacks", 469, 4.0, 3.0, 7.0, 450, 71.0),
    ("Air-popped popcorn", "Snacks", 387, 14.5, 0.6, 13.0, 8, 78.0),
    ("Dark chocolate (70%+)", "Snacks", 598, 11.0, 24.0, 7.8, 20, 46.0),
    ("Whole wheat pretzels", "Snacks", 350, 6.0, 2.0, 11.0, 750, 75.0),
    ("Low-sugar oatmeal cookies", "Snacks", 435, 3.8, 20.0, 6.0, 280, 68.0),
    ("Baked cinnamon apple slices", "Snacks", 60, 2.4, 10.0, 0.3, 1, 16.0),
    ("Baked tortilla chips with salsa", "Snacks", 440, 6.0, 2.0, 8.0, 380, 73.0),

    # ---- Beverages ----
    ("Cola soda", "Beverages", 42, 0.0, 10.6, 0.0, 4, 10.6),
    ("Sweetened orange juice", "Beverages", 45, 0.2, 8.4, 0.7, 1, 10.4),
    ("Whole milk latte", "Beverages", 61, 0.0, 5.0, 3.2, 40, 4.8),
    ("Energy drink", "Beverages", 45, 0.0, 11.0, 0.0, 20, 11.0),
    ("Sweet tea", "Beverages", 34, 0.0, 9.0, 0.0, 5, 9.0),
    ("Regular beer", "Beverages", 43, 0.0, 0.0, 0.5, 4, 3.6),
    ("Sparkling water, unsweetened", "Beverages", 0, 0.0, 0.0, 0.0, 7, 0.0),
    ("Fresh whole orange", "Beverages", 47, 2.4, 9.4, 0.9, 0, 12.0),
    ("Skim milk latte", "Beverages", 35, 0.0, 5.0, 3.4, 42, 5.0),
    ("Unsweetened herbal tea", "Beverages", 1, 0.0, 0.0, 0.0, 2, 0.3),
    ("Unsweetened iced tea", "Beverages", 1, 0.0, 0.0, 0.0, 3, 0.3),
    ("Light beer", "Beverages", 29, 0.0, 0.3, 0.2, 5, 1.6),

    # ---- Condiments & fats ----
    ("Mayonnaise", "Condiments", 680, 0.0, 1.0, 1.0, 635, 0.6),
    ("Butter", "Condiments", 643, 0.0, 0.1, 0.9, 11, 0.1),
    ("Ranch dressing", "Condiments", 460, 0.0, 3.0, 1.0, 800, 5.0),
    ("Regular ketchup", "Condiments", 112, 0.3, 22.0, 1.2, 907, 27.0),
    ("Sweetened peanut butter", "Condiments", 588, 6.0, 9.0, 25.0, 429, 20.0),
    ("BBQ sauce", "Condiments", 172, 0.5, 33.0, 1.0, 985, 41.0),
    ("Regular soy sauce", "Condiments", 60, 0.8, 4.9, 10.5, 5493, 6.0),
    ("Greek-yogurt based mayo alternative", "Condiments", 130, 0.0, 3.0, 9.0, 300, 4.0),
    ("Olive oil", "Condiments", 884, 0.0, 0.0, 0.0, 2, 0.0),
    ("Greek yogurt ranch dressing", "Condiments", 150, 0.5, 3.0, 6.0, 380, 6.0),
    ("No-sugar-added ketchup", "Condiments", 60, 0.5, 8.0, 1.0, 400, 15.0),
    ("Natural peanut butter, no added sugar", "Condiments", 588, 8.0, 4.0, 25.0, 5, 16.0),
    ("Low-sugar BBQ sauce", "Condiments", 100, 0.5, 15.0, 1.0, 550, 22.0),
    ("Low-sodium soy sauce", "Condiments", 53, 0.8, 4.0, 8.0, 2700, 6.0),

    # ---- Fast food / meals ----
    ("Fast food cheeseburger", "Fast Food", 303, 1.5, 6.0, 15.0, 680, 30.0),
    ("French fries", "Fast Food", 312, 3.8, 0.3, 3.4, 210, 41.0),
    ("Fried fish sandwich", "Fast Food", 240, 1.0, 3.0, 11.0, 570, 26.0),
    ("Pepperoni pizza", "Fast Food", 298, 2.1, 3.8, 13.0, 640, 33.0),
    ("Boxed mac and cheese", "Fast Food", 164, 0.9, 2.0, 6.0, 380, 20.0),
    ("Fast food chicken nuggets", "Fast Food", 296, 1.4, 0.5, 15.0, 540, 18.0),
    ("Beef burrito, fast food", "Fast Food", 206, 3.0, 2.0, 9.0, 500, 24.0),
    ("Grilled chicken burger", "Fast Food", 165, 0.5, 2.0, 25.0, 380, 5.0),
    ("Baked sweet potato fries", "Fast Food", 150, 3.6, 5.0, 2.0, 60, 26.0),
    ("Grilled fish sandwich, whole wheat bun", "Fast Food", 190, 3.0, 3.0, 18.0, 380, 22.0),
    ("Veggie thin-crust pizza", "Fast Food", 220, 2.8, 3.0, 10.0, 420, 28.0),
    ("Whole wheat mac and cheese, light", "Fast Food", 140, 3.0, 2.0, 7.0, 280, 18.0),
    ("Baked chicken tenders, homemade", "Fast Food", 195, 0.8, 0.5, 22.0, 320, 10.0),
    ("Burrito bowl, no tortilla", "Fast Food", 150, 5.0, 2.0, 10.0, 350, 18.0),

    # ---- Breakfast & sweets ----
    ("Granola bar, chocolate", "Breakfast", 471, 4.0, 30.0, 7.0, 260, 65.0),
    ("Bakery blueberry muffin", "Breakfast", 377, 1.5, 26.0, 5.6, 320, 55.0),
    ("Gummy fruit snacks", "Breakfast", 344, 0.0, 43.0, 0.0, 45, 84.0),
    ("Sweetened instant oatmeal", "Breakfast", 375, 5.0, 27.0, 8.0, 320, 73.0),
    ("Table sugar", "Breakfast", 387, 0.0, 100.0, 0.0, 0, 100.0),
    ("Canned fruit in syrup", "Breakfast", 74, 1.0, 17.0, 0.4, 5, 19.0),
    ("Plain oatmeal with fresh fruit", "Breakfast", 68, 1.7, 3.0, 2.4, 4, 12.0),
    ("Homemade granola bar, low sugar", "Breakfast", 400, 6.0, 12.0, 9.0, 120, 55.0),
    ("Whole wheat mini muffin, low sugar", "Breakfast", 280, 3.5, 12.0, 6.0, 250, 40.0),
    ("Fresh mixed berries", "Breakfast", 57, 2.4, 10.0, 0.7, 1, 14.0),
    ("Honey", "Breakfast", 304, 0.2, 82.0, 0.3, 4, 82.0),
    ("Fresh apple slices", "Breakfast", 52, 2.4, 10.0, 0.3, 1, 14.0),
]

# Substitutions: (original_name, substitute_name, base_certainty 0-100, rationale)
SUBS = [
    ("White bread", "Whole wheat bread", 82, "More fiber and protein, similar calories, less added sugar."),
    ("White rice, cooked", "Brown rice, cooked", 78, "More fiber, fewer calories, similar protein."),
    ("Regular pasta, cooked", "Whole wheat pasta, cooked", 76, "Roughly double the fiber for fewer calories."),
    ("Regular pasta, cooked", "Quinoa, cooked", 70, "Complete plant protein with more fiber."),
    ("Instant ramen noodles", "Whole grain noodle soup, low sodium broth", 88, "Cuts sodium by more than 75% and adds fiber."),
    ("Frosted corn flakes cereal", "Bran flakes cereal", 83, "Far more fiber, meaningfully less sugar per serving."),
    ("Plain bagel", "Whole wheat bagel", 72, "More fiber and protein at a similar calorie count."),
    ("Pancakes, from mix", "Whole wheat pancakes", 74, "More fiber and protein, fewer refined carbs."),
    ("Butter croissant", "Whole grain English muffin", 85, "Less than half the calories and fat, more fiber."),
    ("Flour tortilla", "Whole wheat tortilla", 70, "More fiber, less sodium."),
    ("Whole milk", "Skim milk", 68, "Same protein, far less saturated fat and fewer calories."),
    ("Vanilla ice cream", "Low-fat frozen yogurt", 55, "Lower fat, though sugar stays similar -- moderate improvement."),
    ("Sour cream", "Plain nonfat Greek yogurt", 84, "Roughly triple the protein at a third of the calories."),
    ("Cream cheese", "Light cream cheese", 65, "Meaningfully fewer calories and less fat, similar taste."),
    ("American cheese slices", "Reduced-sodium Swiss cheese", 73, "More protein and over 50% less sodium."),
    ("Sweetened whole milk yogurt", "Plain nonfat Greek yogurt", 87, "Roughly double the protein, far less sugar."),
    ("Ground beef (80/20)", "Ground turkey (93/7)", 80, "Less saturated fat, similar protein."),
    ("Bacon", "Turkey bacon", 62, "Less fat overall, though sodium stays high -- modest improvement."),
    ("Breaded fried chicken", "Grilled chicken breast", 90, "Much less sodium and fat, far more protein per calorie."),
    ("Hot dog", "Chicken sausage", 75, "Meaningfully less sodium and more protein."),
    ("Deli ham, processed", "Low-sodium deli turkey", 79, "About 60% less sodium, similar protein."),
    ("Salami", "Lean turkey deli slices", 81, "Less sodium and fat, similar protein content."),
    ("Regular pork sausage", "Chicken sausage", 74, "Less saturated fat, similar protein."),
    ("Potato chips", "Baked potato chips", 60, "Lower fat, similar sodium -- a moderate swap."),
    ("Potato chips", "Air-popped popcorn", 85, "Far more fiber and protein for fewer calories per serving."),
    ("Buttered movie popcorn", "Air-popped popcorn", 88, "Cuts sodium dramatically while keeping the fiber."),
    ("Milk chocolate candy bar", "Dark chocolate (70%+)", 66, "Less sugar and more fiber, similar calories."),
    ("Salted pretzels", "Whole wheat pretzels", 63, "More fiber and protein, sodium is still notable."),
    ("Chocolate chip cookies", "Low-sugar oatmeal cookies", 71, "Meaningfully less sugar, more fiber."),
    ("Glazed donut", "Baked cinnamon apple slices", 93, "A fraction of the calories and sugar, real fiber."),
    ("Nacho cheese tortilla chips", "Baked tortilla chips with salsa", 68, "Lower fat and more fiber, similar sodium."),
    ("Cola soda", "Sparkling water, unsweetened", 95, "Removes all added sugar and calories."),
    ("Sweetened orange juice", "Fresh whole orange", 82, "Real fiber and fewer concentrated sugars."),
    ("Whole milk latte", "Skim milk latte", 66, "Same protein, notably less saturated fat."),
    ("Energy drink", "Sparkling water, unsweetened", 87, "Removes added sugar and stimulant-linked additives."),
    ("Sweet tea", "Unsweetened iced tea", 90, "Same base drink, virtually all the sugar removed."),
    ("Regular beer", "Light beer", 58, "Fewer calories and carbs, alcohol content still applies."),
    ("Mayonnaise", "Greek-yogurt based mayo alternative", 78, "More protein, a fraction of the fat and calories."),
    ("Butter", "Olive oil", 60, "Unsaturated fat profile, though calorie-dense -- use in moderation."),
    ("Ranch dressing", "Greek yogurt ranch dressing", 76, "More protein, notably less fat."),
    ("Regular ketchup", "No-sugar-added ketchup", 72, "About two-thirds less sugar, similar flavor."),
    ("Sweetened peanut butter", "Natural peanut butter, no added sugar", 70, "Less than half the sugar, more fiber."),
    ("BBQ sauce", "Low-sugar BBQ sauce", 69, "Over half the sugar removed."),
    ("Regular soy sauce", "Low-sodium soy sauce", 65, "Roughly half the sodium, same flavor profile."),
    ("Fast food cheeseburger", "Grilled chicken burger", 84, "Far more protein per calorie, less sodium and fat."),
    ("French fries", "Baked sweet potato fries", 73, "More fiber and vitamin A, less fat."),
    ("Fried fish sandwich", "Grilled fish sandwich, whole wheat bun", 79, "Less fat and sodium, more fiber from the bun."),
    ("Pepperoni pizza", "Veggie thin-crust pizza", 68, "Less sodium and fat, similar protein."),
    ("Boxed mac and cheese", "Whole wheat mac and cheese, light", 70, "More fiber, less sodium and fat."),
    ("Fast food chicken nuggets", "Baked chicken tenders, homemade", 81, "Less sodium and fat, more protein per calorie."),
    ("Beef burrito, fast food", "Burrito bowl, no tortilla", 74, "More fiber, less sodium and refined carbs."),
    ("Granola bar, chocolate", "Homemade granola bar, low sugar", 67, "Notably less sugar, more fiber and protein."),
    ("Bakery blueberry muffin", "Whole wheat mini muffin, low sugar", 75, "Roughly half the sugar, more fiber."),
    ("Gummy fruit snacks", "Fresh mixed berries", 91, "Real fiber and vitamins, a fraction of the sugar."),
    ("Sweetened instant oatmeal", "Plain oatmeal with fresh fruit", 80, "Far less added sugar and sodium, same fiber."),
    ("Table sugar", "Honey", 45, "Some trace nutrients, but sugar content is still very high -- use sparingly."),
    ("Canned fruit in syrup", "Fresh apple slices", 86, "No added syrup, real fiber, far less sugar."),
]

with open(DATA_DIR / "foods.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["food_id", "name", "category", "calories", "fiber_g", "sugar_g", "protein_g", "sodium_mg", "carbs_g"])
    for i, (name, cat, cal, fib, sug, pro, sod, carb) in enumerate(FOODS, start=1):
        writer.writerow([i, name, cat, cal, fib, sug, pro, sod, carb])

name_to_id = {name: i for i, (name, *_rest) in enumerate(FOODS, start=1)}

missing = [orig for orig, sub, *_ in SUBS if orig not in name_to_id or sub not in name_to_id]
if missing:
    raise SystemExit(f"Names referenced in SUBS not found in FOODS: {missing}")

with open(DATA_DIR / "substitutions.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["sub_id", "original_food_id", "substitute_food_id", "base_certainty", "rationale"])
    for i, (orig, sub, certainty, rationale) in enumerate(SUBS, start=1):
        writer.writerow([i, name_to_id[orig], name_to_id[sub], certainty, rationale])

print(f"Wrote {len(FOODS)} foods to data/foods.csv")
print(f"Wrote {len(SUBS)} substitution links to data/substitutions.csv")
print(f"Unique foods used as originals: {len(set(o for o,s,*_ in SUBS))}")
print(f"Unique foods used as substitutes: {len(set(s for o,s,*_ in SUBS))}")
