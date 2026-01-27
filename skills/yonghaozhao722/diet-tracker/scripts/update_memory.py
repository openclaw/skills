import datetime

def update_memory(food_item, nutrition_info):
    # Get the current date
    now = datetime.datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    filename = f"memory/{date_string}.md"

    # Format the food item and nutrition information
    food_string = f"• {food_item}: {nutrition_info['calories']} 大卡, 蛋白质 {nutrition_info['protein']}g, 脂肪 {nutrition_info['fat']}g, 碳水 {nutrition_info['carbs']}g\n"

    # Read the file (if it exists)
    try:
        with open(filename, "r") as f:
            content = f.read()
    except FileNotFoundError:
        content = ""

    # Add the food item to the content
    content += food_string

    # Write the updated content back to the file
    try:
        with open(filename, "w") as f:
            f.write(content)
        print(f"Successfully added '{food_item}' to {filename}")
    except Exception as e:
        print(f"Error writing to file: {e}")

if __name__ == '__main__':
    food_item = input("Enter a food item: ")
    nutrition_info = {"calories": 100, "protein": 10, "fat": 5, "carbs": 20}
    update_memory(food_item, nutrition_info)
