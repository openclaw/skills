import json
import requests
import re

def calculate_tdee(height_cm, weight_kg, age, gender, activity_level):
    print(f"calculate_tdee input: height_cm={height_cm}, weight_kg={weight_kg}, age={age}, gender={gender}, activity_level={activity_level}")
    if gender == "male":
        bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    elif gender == "female":
        bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
    else:
        print("Invalid gender")
        return None

    activity_factors = {
        "sedentary": 1.2,
        "lightly active": 1.375,
        "moderately active": 1.55,
        "very active": 1.725,
        "extra active": 1.9
    }

    if activity_level in activity_factors:
        tdee = bmr * activity_factors[activity_level]
        print(f"TDEE is {tdee}")
        return tdee
    else:
        print("Invalid activity level")
        return None


def get_user_info():
    try:
        with open("/home/zhaoyh/clawd/USER.md", "r") as f:
            content = f.read()

        height_match = re.search(r"身高:.*?(\d+\.?\d*)\s*(cm|厘米)", content)
        weight_match = re.search(r"体重:.*?(\d+\.?\d*)\s*(kg|公斤)", content)
        age_match = re.search(r"年龄:.*?(\d+)", content)
        gender_match = re.search(r"性别:.*?([男女])", content)
        activity_level_match = re.search(r"活动水平:.*?(\w+.*)", content)

        height_cm = float(height_match.group(1)) if height_match else None
        weight_kg = float(weight_match.group(1)) if weight_match else None
        age = int(age_match.group(1)) if age_match else None
        gender = "male" if gender_match and "男" in gender_match.group(1) else "female" if gender_match and "女" in gender_match.group(1) else None
        activity_level = activity_level_match.group(1).lower().replace(' ', '') if activity_level_match else None

        if all([height_cm, weight_kg, age, gender, activity_level]):
            print(f"get_user_info: height_cm={height_cm}, weight_kg={weight_kg}, age={age}, gender={gender}, activity_level={activity_level}")
            return height_cm, weight_kg, age, gender, activity_level
        else:
            print("Could not retrieve all required user information from USER.md.")
            return None, None, None, None, None

    except FileNotFoundError:
        print("USER.md not found.")
        return None, None, None, None, None

def get_nutrition(food_item):
    # First, try local database
    try:
        with open("/home/zhaoyh/clawd/skills/diet-tracker/references/food_database.json", "r") as f:
            db = json.load(f)

        # Search for exact match or partial match (case insensitive)
        for key, value in db.items():
            if key.lower() in food_item.lower() or food_item.lower() in key.lower():
                print(f"Found in local database for {food_item}:")
                print(f"Calories: {value['calories']}")
                print(f"Protein: {value['protein']}g")
                print(f"Fat: {value['fat']}g")
                print(f"Carbs: {value['carbs']}g")
                return value

        print(f"Food item '{food_item}' not found in local database.")
    except FileNotFoundError:
        print("Local food database not found.")
    except json.JSONDecodeError as e:
        print(f"Error loading local database: {e}")

    # Fallback to API
    try:
        # Use Nutrition API to get nutrition information
        api_url = f"https://api.nal.usda.gov/fdc/v1/food/search?api_key=DEMO_KEY&query={food_item}"
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        # Extract the nutrition details (customize based on the API response structure)
        if data["foods"]:
            food = data["foods"][0]
            if "foodNutrients" in food:
                nutrients = {}
                for nutrient in food["nutrient"]:
                    nutrients[nutrient["nutrientName"]] = nutrient["value"]

                calories = nutrients.get("Energy", 0)
                protein = nutrients.get("Protein", 0)
                fat = nutrients.get("Total lipid (fat)", 0)
                carbs = nutrients.get("Carbohydrate, by difference", 0)

                print(f"Nutrition information for {food_item} from API:")
                print(f"Calories: {calories}")
                print(f"Protein: {protein}g")
                print(f"Fat: {fat}g")
                print(f"Carbs: {carbs}g")
                return {"calories": calories, "protein": protein, "fat": fat, "carbs": carbs}
            else:
                print(f"No nutrient information found for {food_item}.")
                return None
        else:
            print(f"Food item '{food_item}' not found.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error occurred during API request: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None


if __name__ == '__main__':
    height_cm, weight_kg, age, gender, activity_level = get_user_info()

    if all([height_cm, weight_kg, age, gender, activity_level]):
        tdee = calculate_tdee(height_cm, weight_kg, age, gender, activity_level)

        if tdee:
            print(f"Your TDEE is approximately: {tdee:.2f} calories")
        else:
            print("Invalid input for TDEE calculation.")
    else:
        print("Could not retrieve all required user information.")

    # Example usage for nutrition info:
    food_item = input("Enter a food item: ")
    nutrition_info = get_nutrition(food_item)
    if nutrition_info:
        print(nutrition_info)
