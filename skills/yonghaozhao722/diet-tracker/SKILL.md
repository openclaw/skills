---
name: diet-tracker
description: Tracks daily diet and calculates nutrition information to help achieve weight loss goals. Use when the user provides information about their meals and wants to track calorie and macronutrient intake. Also used to remind the user to log meals. This skill reads user's height, weight, age, gender and activity levels from USER.md to predict TDEE. Then based on daily calorie surplus or deficit, extrapolate weight changes.
---

# Diet Tracker

This skill helps you track your daily diet and achieve your weight loss goals.

## Usage

1.  The skill will read User related info in `USER.md` to get:
    *   Your daily calorie target
    *   Your height, weight, age, gender, and activity level to calculate TDEE.

2.  When you provide information about your meals (e.g., "I had a sandwich for lunch"), this skill will:
    *   Identify the food items in your meal.
    *   Use the `get_food_nutrition.py` script to fetch nutrition information (calories, protein, carbs, fat) from the web.
    *   Add the meal information and nutrition details to the current day's memory file (memory/YYYY-MM-DD.md).
    *   Calculate the total calories and macronutrients for the meal.
    *   Update the total daily intake and remaining calorie budget.
        *   Also predict weight change based on daily calories.

3.  When you ask about your remaining calorie budget, this skill will:
    *   Read the current day’s memory file.
    *   Calculate the total calories consumed so far.
    *   Subtract the consumed calories from your daily calorie goal (found in USER.md).
    *   Report the remaining calories.
        *   Also predict weight change based on accumulated daily calories.

## Scripts

*   `scripts/get_food_nutrition.py`: Fetches nutrition information for a given food item from the web and calculates TDEE.
*   `scripts/update_memory.py`: Updates the current day’s memory file with meal information and nutrition details.

## Data

*   `references/food_database.json`: A database of common food items and their nutrition information (used as a fallback).

## Workflow

1.  Diet-tracker skill read User related info from `USER.md` to get:
    *   Daily calorie target
    *   Height, weight, age, gender, and activity level. Activity levels:
        *   Sedentary (little or no exercise)
        *   Lightly active (light exercise/sports 1-3 days/week)
        *   Moderately active (moderate exercise/sports 3-5 days/week)
        *   Very active (hard exercise/sports 6-7 days a week)
        *   Extra active (very hard exercise/sports & physical job or 2x training)
2.  User provides meal information.
3.  Skill identifies food items.
4.  Skill uses `scripts/get_food_nutrition.py` to fetch nutrition information. If the information is not available online, the skill will use the `references/food_database.json` file.
5.  Skill uses `scripts/update_memory.py` to update the current day’s memory file.
6.  Skill calculates the total calories and macronutrients for the meal and updates the daily intake.
7.  Skill reports the meal information, remaining calorie budget, and predicted weight change range to the user.


Remember to use `exec cat` command to confirm file type.
