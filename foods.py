"""Nutrition database (per typical serving): name, serving, kcal, protein g, carbs g, fat g, emoji."""
FOODS = [
    ("Idli (2 pcs)", "2 pcs", 116, 4, 24, 0.4, "🍚"), ("Dosa (plain)", "1 medium", 168, 4, 29, 3.7, "🥞"), ("Masala dosa", "1 medium", 290, 6, 42, 11, "🥞"),
    ("Sambar", "1 bowl", 130, 6, 18, 4, "🍲"), ("Coconut chutney", "2 tbsp", 70, 1, 3, 6, "🥥"), ("Upma", "1 bowl", 210, 5, 32, 7, "🍛"),
    ("Poha", "1 bowl", 250, 5, 45, 6, "🍛"), ("Pongal", "1 bowl", 270, 7, 38, 10, "🍚"), ("Chapati", "1 pc", 104, 3, 18, 2.5, "🫓"),
    ("Paratha (plain)", "1 pc", 210, 4, 28, 9, "🫓"), ("Steamed rice", "1 cup", 205, 4, 45, 0.4, "🍚"), ("Brown rice", "1 cup", 216, 5, 45, 1.8, "🍚"),
    ("Dal (toor)", "1 bowl", 180, 11, 26, 4, "🍲"), ("Rajma curry", "1 bowl", 240, 13, 35, 6, "🍲"), ("Chole", "1 bowl", 270, 12, 38, 9, "🍲"),
    ("Paneer butter masala", "1 bowl", 380, 14, 14, 30, "🧀"), ("Palak paneer", "1 bowl", 290, 15, 10, 21, "🥬"), ("Chicken curry", "1 bowl", 300, 27, 8, 18, "🍗"),
    ("Grilled chicken breast", "150 g", 248, 46, 0, 5.4, "🍗"), ("Chicken biryani", "1 plate", 490, 24, 60, 17, "🍛"), ("Veg biryani", "1 plate", 380, 9, 62, 11, "🍛"),
    ("Fish curry", "1 bowl", 250, 24, 6, 14, "🐟"), ("Egg (boiled)", "1 large", 78, 6, 0.6, 5, "🥚"), ("Omelette (2 eggs)", "1", 190, 13, 2, 15, "🍳"),
    ("Curd / yogurt", "1 cup", 150, 9, 11, 8, "🥛"), ("Buttermilk", "1 glass", 40, 3, 5, 1, "🥛"), ("Milk (toned)", "1 glass", 120, 6, 10, 6, "🥛"),
    ("Masala chai", "1 cup", 105, 3, 14, 4, "☕"), ("Filter coffee", "1 cup", 90, 3, 11, 4, "☕"), ("Black coffee", "1 cup", 5, 0.3, 0, 0, "☕"),
    ("Banana", "1 medium", 105, 1.3, 27, 0.4, "🍌"), ("Apple", "1 medium", 95, 0.5, 25, 0.3, "🍎"), ("Mango", "1 cup", 99, 1.4, 25, 0.6, "🥭"),
    ("Papaya", "1 cup", 62, 0.7, 16, 0.4, "🍈"), ("Orange", "1 medium", 62, 1.2, 15, 0.2, "🍊"), ("Mixed fruit bowl", "1 bowl", 120, 2, 30, 0.5, "🍇"),
    ("Almonds", "10 pcs", 70, 2.6, 2.5, 6, "🌰"), ("Peanuts (roasted)", "30 g", 170, 7, 5, 14, "🥜"), ("Sprouts salad", "1 bowl", 120, 8, 18, 1, "🥗"),
    ("Green salad", "1 bowl", 45, 2, 9, 0.3, "🥗"), ("Oats porridge", "1 bowl", 160, 6, 27, 3, "🥣"), ("Muesli with milk", "1 bowl", 290, 10, 48, 7, "🥣"),
    ("Whey protein shake", "1 scoop", 120, 24, 3, 1.5, "🥤"), ("Peanut butter toast", "1 slice", 190, 7, 17, 11, "🍞"), ("Brown bread", "2 slices", 140, 6, 24, 2, "🍞"),
    ("Samosa", "1 pc", 260, 4, 30, 14, "🥟"), ("Vada", "1 pc", 135, 4, 15, 7, "🍩"), ("Pani puri", "6 pcs", 210, 4, 32, 7, "🥙"),
    ("Pizza slice", "1 slice", 285, 12, 36, 10, "🍕"), ("Burger", "1", 354, 17, 35, 16, "🍔"), ("French fries", "medium", 365, 4, 48, 17, "🍟"),
    ("Gulab jamun", "2 pcs", 300, 4, 44, 12, "🍮"), ("Dark chocolate", "20 g", 110, 1.5, 9, 8, "🍫"), ("Soft drink", "330 ml", 140, 0, 39, 0, "🥤"),
    ("Coconut water", "1 glass", 46, 1.7, 9, 0.5, "🥥"), ("Paneer tikka", "6 pcs", 280, 18, 8, 20, "🧀"), ("Tofu stir fry", "1 bowl", 220, 17, 10, 13, "🥢"),
    ("Quinoa bowl", "1 bowl", 330, 12, 52, 8, "🥗"), ("Lassi (sweet)", "1 glass", 260, 8, 40, 7, "🥛"), ("Rasam", "1 bowl", 60, 2, 9, 2, "🍲"),
]
FOODS = [dict(id=i + 1, name=n, serving=s, kcal=k, protein=p, carbs=c, fat=f, emoji=e) for i, (n, s, k, p, c, f, e) in enumerate(FOODS)]
FOOD_BY_ID = {f["id"]: f for f in FOODS}

# MET values (calories = MET × weight kg × hours)
ACTIVITIES = {"Walking": 3.5, "Brisk walking": 4.5, "Running": 9.8, "Cycling": 7.5, "Yoga": 2.5, "Strength training": 5.0,
              "Swimming": 7.0, "HIIT": 8.0, "Dancing": 5.5, "Cricket": 5.0, "Badminton": 5.5, "Football": 7.0}
