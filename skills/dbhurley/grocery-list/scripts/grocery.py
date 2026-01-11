#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Grocery List & Meal Planner CLI.

Self-contained grocery lists, recipes, and meal planning with local JSON storage.
No external services required.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Default data directory
DATA_DIR = Path(os.environ.get("GROCERY_DATA_DIR", Path.home() / ".clawdbot" / "grocery-list"))
DATA_FILE = DATA_DIR / "data.json"

# Category auto-detection keywords
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "produce": ["apple", "banana", "orange", "lettuce", "tomato", "onion", "potato", "carrot", "celery", "broccoli", "spinach", "avocado", "pepper", "cucumber", "garlic", "lemon", "lime", "strawberry", "blueberry", "grape", "mango", "pineapple", "watermelon", "mushroom", "corn", "cabbage", "kale", "asparagus", "zucchini", "squash"],
    "dairy": ["milk", "cheese", "yogurt", "butter", "cream", "egg", "eggs", "sour cream", "cottage cheese", "half and half", "creamer", "whipping cream"],
    "meat": ["chicken", "beef", "pork", "turkey", "bacon", "sausage", "ham", "steak", "ground beef", "ground turkey", "lamb", "veal", "brisket", "ribs"],
    "seafood": ["fish", "salmon", "tuna", "shrimp", "crab", "lobster", "tilapia", "cod", "halibut", "scallops", "mussels", "clams"],
    "bakery": ["bread", "rolls", "bagel", "muffin", "croissant", "baguette", "tortilla", "pita", "english muffin", "bun", "buns"],
    "frozen": ["ice cream", "frozen pizza", "frozen vegetables", "frozen fruit", "frozen dinner", "popsicle", "frozen waffles"],
    "pantry": ["pasta", "rice", "beans", "soup", "canned", "cereal", "oatmeal", "flour", "sugar", "olive oil", "vegetable oil", "vinegar", "soy sauce", "peanut butter", "jelly", "honey", "syrup", "salt", "pepper", "spice"],
    "beverages": ["water", "soda", "juice", "coffee", "tea", "wine", "beer", "lemonade", "gatorade", "energy drink", "sparkling water", "kombucha"],
    "snacks": ["chips", "crackers", "cookies", "popcorn", "nuts", "pretzels", "granola bar", "candy", "chocolate"],
    "household": ["paper towel", "toilet paper", "dish soap", "laundry detergent", "trash bags", "aluminum foil", "plastic wrap", "napkins", "sponge", "cleaner"],
    "personal": ["shampoo", "conditioner", "soap", "toothpaste", "deodorant", "lotion", "razor", "medicine", "vitamins", "bandaid"],
}

ALL_CATEGORIES = list(CATEGORY_KEYWORDS.keys()) + ["other"]


@dataclass
class GroceryItem:
    id: str
    name: str
    list_name: str
    category: str = "other"
    quantity: float = 1.0
    unit: str = ""
    assignee: str = ""
    checked: bool = False
    added: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: dict) -> "GroceryItem":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Recipe:
    id: str
    name: str
    ingredients: list[str] = field(default_factory=list)
    instructions: str = ""
    category: str = ""
    servings: int = 4
    prep_time: str = ""
    cook_time: str = ""
    notes: str = ""
    created: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: dict) -> "Recipe":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Meal:
    id: str
    date: str  # YYYY-MM-DD
    type: str  # breakfast, lunch, dinner, snack
    recipe_name: str = ""
    notes: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: dict) -> "Meal":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class DataStore:
    lists: list[str] = field(default_factory=lambda: ["Grocery"])
    items: list[GroceryItem] = field(default_factory=list)
    recipes: list[Recipe] = field(default_factory=list)
    meals: list[Meal] = field(default_factory=list)
    family: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "lists": self.lists,
            "items": [i.to_dict() for i in self.items],
            "recipes": [r.to_dict() for r in self.recipes],
            "meals": [m.to_dict() for m in self.meals],
            "family": self.family,
        }
    
    @classmethod
    def from_dict(cls, d: dict) -> "DataStore":
        return cls(
            lists=d.get("lists", ["Grocery"]),
            items=[GroceryItem.from_dict(i) for i in d.get("items", [])],
            recipes=[Recipe.from_dict(r) for r in d.get("recipes", [])],
            meals=[Meal.from_dict(m) for m in d.get("meals", [])],
            family=d.get("family", []),
        )


def load_data() -> DataStore:
    """Load data from JSON file."""
    if not DATA_FILE.exists():
        return DataStore()
    try:
        with open(DATA_FILE) as f:
            return DataStore.from_dict(json.load(f))
    except (json.JSONDecodeError, KeyError):
        return DataStore()


def save_data(data: DataStore) -> None:
    """Save data to JSON file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data.to_dict(), f, indent=2, sort_keys=True)


def detect_category(name: str) -> str:
    """Auto-detect category based on item name."""
    name_lower = name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in name_lower:
                return category
    return "other"


def parse_quantity(qty_str: str) -> tuple[float, str]:
    """Parse '2 gallons' into (2.0, 'gallon')."""
    if not qty_str:
        return (1.0, "")
    parts = qty_str.strip().split(None, 1)
    if len(parts) == 1:
        try:
            return (float(parts[0]), "")
        except ValueError:
            return (1.0, parts[0])
    try:
        num = float(parts[0])
        unit = parts[1].rstrip("s")  # Normalize plural
        return (num, unit)
    except ValueError:
        return (1.0, qty_str)


def now_iso() -> str:
    """Get current ISO timestamp."""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")


def today_str() -> str:
    """Get today's date as YYYY-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")


# ─────────────────────────────────────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────────────────────────────────────

def cmd_lists(args: argparse.Namespace) -> int:
    """List all shopping lists."""
    data = load_data()
    if args.json:
        print(json.dumps({"lists": data.lists}, indent=2))
    else:
        print("📋 Shopping Lists:")
        for lst in data.lists:
            count = sum(1 for i in data.items if i.list_name == lst and not i.checked)
            print(f"  • {lst} ({count} items)")
    return 0


def cmd_list_view(args: argparse.Namespace) -> int:
    """View items in a specific list."""
    data = load_data()
    list_name = args.list_name
    
    if list_name not in data.lists:
        print(f"❌ List '{list_name}' not found. Available: {', '.join(data.lists)}", file=sys.stderr)
        return 1
    
    items = [i for i in data.items if i.list_name == list_name]
    if args.unchecked:
        items = [i for i in items if not i.checked]
    
    if args.json:
        print(json.dumps({"list": list_name, "items": [i.to_dict() for i in items]}, indent=2))
        return 0
    
    # Group by category
    by_category: dict[str, list[GroceryItem]] = {}
    for item in items:
        by_category.setdefault(item.category, []).append(item)
    
    print(f"🛒 {list_name}:")
    if not items:
        print("  (empty)")
        return 0
    
    for cat in ALL_CATEGORIES:
        if cat not in by_category:
            continue
        print(f"\n  [{cat.upper()}]")
        for item in by_category[cat]:
            check = "✓" if item.checked else "○"
            qty = f"{item.quantity:g}" if item.quantity != 1 else ""
            unit = f" {item.unit}" if item.unit else ""
            assignee = f" (@{item.assignee})" if item.assignee else ""
            print(f"    {check} {qty}{unit} {item.name}{assignee}")
    return 0


def cmd_list_create(args: argparse.Namespace) -> int:
    """Create a new list."""
    data = load_data()
    name = args.name
    if name in data.lists:
        print(f"⚠️  List '{name}' already exists.", file=sys.stderr)
        return 1
    data.lists.append(name)
    save_data(data)
    print(f"✅ Created list '{name}'")
    return 0


def cmd_list_delete(args: argparse.Namespace) -> int:
    """Delete a list and its items."""
    data = load_data()
    name = args.name
    if name not in data.lists:
        print(f"❌ List '{name}' not found.", file=sys.stderr)
        return 1
    data.lists.remove(name)
    data.items = [i for i in data.items if i.list_name != name]
    save_data(data)
    print(f"🗑️  Deleted list '{name}'")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    """Add item(s) to a list."""
    data = load_data()
    list_name = args.list_name
    
    if list_name not in data.lists:
        data.lists.append(list_name)
    
    for item_name in args.items:
        qty, unit = parse_quantity(args.qty) if args.qty else (1.0, "")
        category = args.category or detect_category(item_name)
        
        item = GroceryItem(
            id=str(uuid.uuid4())[:8],
            name=item_name,
            list_name=list_name,
            category=category,
            quantity=qty,
            unit=unit,
            assignee=args.assignee or "",
            checked=False,
            added=now_iso(),
        )
        data.items.append(item)
        print(f"✅ Added '{item_name}' to {list_name}")
    
    save_data(data)
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    """Mark item as checked."""
    data = load_data()
    found = False
    for item in data.items:
        if item.list_name == args.list_name and item.name.lower() == args.item.lower():
            item.checked = True
            found = True
            print(f"✓ Checked off '{item.name}'")
            break
    if not found:
        print(f"❌ Item '{args.item}' not found in '{args.list_name}'", file=sys.stderr)
        return 1
    save_data(data)
    return 0


def cmd_uncheck(args: argparse.Namespace) -> int:
    """Mark item as unchecked."""
    data = load_data()
    found = False
    for item in data.items:
        if item.list_name == args.list_name and item.name.lower() == args.item.lower():
            item.checked = False
            found = True
            print(f"○ Unchecked '{item.name}'")
            break
    if not found:
        print(f"❌ Item '{args.item}' not found in '{args.list_name}'", file=sys.stderr)
        return 1
    save_data(data)
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    """Remove item from list."""
    data = load_data()
    before = len(data.items)
    data.items = [i for i in data.items if not (i.list_name == args.list_name and i.name.lower() == args.item.lower())]
    if len(data.items) == before:
        print(f"❌ Item '{args.item}' not found in '{args.list_name}'", file=sys.stderr)
        return 1
    save_data(data)
    print(f"🗑️  Removed '{args.item}' from {args.list_name}")
    return 0


def cmd_clear(args: argparse.Namespace) -> int:
    """Clear all checked items from a list."""
    data = load_data()
    before = len(data.items)
    data.items = [i for i in data.items if not (i.list_name == args.list_name and i.checked)]
    cleared = before - len(data.items)
    save_data(data)
    print(f"🗑️  Cleared {cleared} checked items from {args.list_name}")
    return 0


# ─── Recipes ─────────────────────────────────────────────────────────────────

def cmd_recipes(args: argparse.Namespace) -> int:
    """List all recipes."""
    data = load_data()
    recipes = data.recipes
    
    if args.category:
        recipes = [r for r in recipes if r.category.lower() == args.category.lower()]
    
    if args.json:
        print(json.dumps({"recipes": [r.to_dict() for r in recipes]}, indent=2))
        return 0
    
    print("📖 Recipes:")
    if not recipes:
        print("  (none saved)")
        return 0
    
    by_cat: dict[str, list[Recipe]] = {}
    for r in recipes:
        by_cat.setdefault(r.category or "Uncategorized", []).append(r)
    
    for cat, rlist in sorted(by_cat.items()):
        print(f"\n  [{cat}]")
        for r in rlist:
            print(f"    • {r.name} ({r.servings} servings)")
    return 0


def cmd_recipe_view(args: argparse.Namespace) -> int:
    """View a specific recipe."""
    data = load_data()
    name = args.name.lower()
    recipe = next((r for r in data.recipes if r.name.lower() == name), None)
    
    if not recipe:
        print(f"❌ Recipe '{args.name}' not found.", file=sys.stderr)
        return 1
    
    if args.json:
        print(json.dumps(recipe.to_dict(), indent=2))
        return 0
    
    if args.ingredients_only:
        print(f"Ingredients for {recipe.name}:")
        for ing in recipe.ingredients:
            print(f"  • {ing}")
        return 0
    
    print(f"📖 {recipe.name}")
    if recipe.category:
        print(f"   Category: {recipe.category}")
    print(f"   Servings: {recipe.servings}")
    if recipe.prep_time or recipe.cook_time:
        print(f"   Time: {recipe.prep_time} prep / {recipe.cook_time} cook")
    print("\n   Ingredients:")
    for ing in recipe.ingredients:
        print(f"     • {ing}")
    if recipe.instructions:
        print(f"\n   Instructions:\n     {recipe.instructions}")
    if recipe.notes:
        print(f"\n   Notes: {recipe.notes}")
    return 0


def cmd_recipe_add(args: argparse.Namespace) -> int:
    """Add a new recipe."""
    data = load_data()
    
    # Check if exists
    existing = next((r for r in data.recipes if r.name.lower() == args.name.lower()), None)
    if existing:
        print(f"⚠️  Recipe '{args.name}' already exists. Use a different name or delete first.", file=sys.stderr)
        return 1
    
    ingredients = []
    if args.ingredients:
        ingredients = [i.strip() for i in args.ingredients.split(",")]
    
    recipe = Recipe(
        id=str(uuid.uuid4())[:8],
        name=args.name,
        ingredients=ingredients,
        instructions=args.instructions or "",
        category=args.category or "",
        servings=args.servings or 4,
        prep_time=args.prep_time or "",
        cook_time=args.cook_time or "",
        notes=args.notes or "",
        created=now_iso(),
    )
    data.recipes.append(recipe)
    save_data(data)
    print(f"✅ Added recipe '{args.name}' with {len(ingredients)} ingredients")
    return 0


def cmd_recipe_delete(args: argparse.Namespace) -> int:
    """Delete a recipe."""
    data = load_data()
    before = len(data.recipes)
    data.recipes = [r for r in data.recipes if r.name.lower() != args.name.lower()]
    if len(data.recipes) == before:
        print(f"❌ Recipe '{args.name}' not found.", file=sys.stderr)
        return 1
    save_data(data)
    print(f"🗑️  Deleted recipe '{args.name}'")
    return 0


def cmd_recipe_search(args: argparse.Namespace) -> int:
    """Search recipes."""
    data = load_data()
    query = args.query.lower()
    matches = [r for r in data.recipes if query in r.name.lower() or query in " ".join(r.ingredients).lower()]
    
    if args.json:
        print(json.dumps({"results": [r.to_dict() for r in matches]}, indent=2))
        return 0
    
    print(f"🔍 Recipes matching '{args.query}':")
    if not matches:
        print("  (no matches)")
        return 0
    for r in matches:
        print(f"  • {r.name} ({len(r.ingredients)} ingredients)")
    return 0


# ─── Meals ───────────────────────────────────────────────────────────────────

def cmd_meals(args: argparse.Namespace) -> int:
    """Show meal plan."""
    data = load_data()
    
    # Default to this week
    today = datetime.now()
    start = today - timedelta(days=today.weekday())  # Monday
    end = start + timedelta(days=6)  # Sunday
    
    if args.date:
        target = datetime.strptime(args.date, "%Y-%m-%d")
        start = target - timedelta(days=target.weekday())
        end = start + timedelta(days=6)
    
    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")
    
    meals = [m for m in data.meals if start_str <= m.date <= end_str]
    meals.sort(key=lambda m: (m.date, ["breakfast", "lunch", "dinner", "snack"].index(m.type) if m.type in ["breakfast", "lunch", "dinner", "snack"] else 4))
    
    if args.json:
        print(json.dumps({"week_start": start_str, "week_end": end_str, "meals": [m.to_dict() for m in meals]}, indent=2))
        return 0
    
    print(f"📅 Meal Plan ({start_str} to {end_str}):")
    if not meals:
        print("  (no meals planned)")
        return 0
    
    current_date = ""
    for m in meals:
        if m.date != current_date:
            current_date = m.date
            day_name = datetime.strptime(m.date, "%Y-%m-%d").strftime("%A %b %d")
            print(f"\n  {day_name}:")
        print(f"    {m.type.capitalize()}: {m.recipe_name or '(unplanned)'}{' - ' + m.notes if m.notes else ''}")
    return 0


def cmd_meal_add(args: argparse.Namespace) -> int:
    """Add a meal to the plan."""
    data = load_data()
    
    date = args.date or today_str()
    meal_type = args.type.lower()
    
    if meal_type not in ["breakfast", "lunch", "dinner", "snack"]:
        print(f"❌ Invalid meal type '{meal_type}'. Use: breakfast, lunch, dinner, snack", file=sys.stderr)
        return 1
    
    # Check for existing
    existing = next((m for m in data.meals if m.date == date and m.type == meal_type), None)
    if existing:
        existing.recipe_name = args.recipe or ""
        existing.notes = args.notes or ""
        print(f"✅ Updated {meal_type} for {date}: {args.recipe or '(cleared)'}")
    else:
        meal = Meal(
            id=str(uuid.uuid4())[:8],
            date=date,
            type=meal_type,
            recipe_name=args.recipe or "",
            notes=args.notes or "",
        )
        data.meals.append(meal)
        print(f"✅ Added {meal_type} for {date}: {args.recipe or '(open)'}")
    
    save_data(data)
    return 0


def cmd_meal_remove(args: argparse.Namespace) -> int:
    """Remove a meal from the plan."""
    data = load_data()
    date = args.date or today_str()
    meal_type = args.type.lower()
    
    before = len(data.meals)
    data.meals = [m for m in data.meals if not (m.date == date and m.type == meal_type)]
    if len(data.meals) == before:
        print(f"❌ No {meal_type} found for {date}", file=sys.stderr)
        return 1
    save_data(data)
    print(f"🗑️  Removed {meal_type} for {date}")
    return 0


def cmd_meal_add_to_list(args: argparse.Namespace) -> int:
    """Add meal ingredients to a grocery list."""
    data = load_data()
    date = args.date or today_str()
    list_name = args.list or "Grocery"
    
    # Find meals for this date
    meals_today = [m for m in data.meals if m.date == date and m.recipe_name]
    if not meals_today:
        print(f"❌ No meals with recipes found for {date}", file=sys.stderr)
        return 1
    
    if list_name not in data.lists:
        data.lists.append(list_name)
    
    added = 0
    for meal in meals_today:
        recipe = next((r for r in data.recipes if r.name.lower() == meal.recipe_name.lower()), None)
        if not recipe:
            print(f"⚠️  Recipe '{meal.recipe_name}' not found, skipping")
            continue
        
        for ing in recipe.ingredients:
            # Check if already in list
            exists = any(i.list_name == list_name and i.name.lower() == ing.lower() and not i.checked for i in data.items)
            if exists:
                continue
            
            item = GroceryItem(
                id=str(uuid.uuid4())[:8],
                name=ing,
                list_name=list_name,
                category=detect_category(ing),
                quantity=1.0,
                unit="",
                assignee="",
                checked=False,
                added=now_iso(),
            )
            data.items.append(item)
            added += 1
    
    save_data(data)
    print(f"✅ Added {added} ingredients to {list_name}")
    return 0


# ─── Utility ─────────────────────────────────────────────────────────────────

def cmd_stats(args: argparse.Namespace) -> int:
    """Show quick statistics."""
    data = load_data()
    
    total_items = len([i for i in data.items if not i.checked])
    total_recipes = len(data.recipes)
    
    # This week's meals
    today = datetime.now()
    start = today - timedelta(days=today.weekday())
    start_str = start.strftime("%Y-%m-%d")
    end_str = (start + timedelta(days=6)).strftime("%Y-%m-%d")
    week_meals = len([m for m in data.meals if start_str <= m.date <= end_str])
    
    if args.json:
        print(json.dumps({
            "lists": len(data.lists),
            "unchecked_items": total_items,
            "recipes": total_recipes,
            "meals_this_week": week_meals,
        }, indent=2))
        return 0
    
    print("📊 Grocery Stats:")
    print(f"  Lists: {len(data.lists)}")
    print(f"  Items to buy: {total_items}")
    print(f"  Saved recipes: {total_recipes}")
    print(f"  Meals planned this week: {week_meals}")
    return 0


def cmd_notify(args: argparse.Namespace) -> int:
    """Output notification for heartbeat/cron."""
    data = load_data()
    
    alerts = []
    
    # Items to buy
    unchecked = [i for i in data.items if not i.checked]
    if unchecked:
        by_list: dict[str, int] = {}
        for i in unchecked:
            by_list[i.list_name] = by_list.get(i.list_name, 0) + 1
        for lst, count in by_list.items():
            if count >= 5:
                alerts.append(f"🛒 {lst} has {count} items")
    
    # Unplanned meals this week
    today = datetime.now()
    for i in range(7):
        check_date = (today + timedelta(days=i)).strftime("%Y-%m-%d")
        dinner = next((m for m in data.meals if m.date == check_date and m.type == "dinner"), None)
        if not dinner or not dinner.recipe_name:
            day_name = (today + timedelta(days=i)).strftime("%A")
            if i == 0:
                alerts.append(f"🍽️ No dinner planned for tonight!")
            elif i <= 2:
                alerts.append(f"🍽️ No dinner planned for {day_name}")
            break  # Only alert for first unplanned
    
    if args.json:
        print(json.dumps({"alerts": alerts}, indent=2))
        return 0
    
    if not alerts:
        print("HEARTBEAT_OK")
    else:
        for a in alerts:
            print(a)
    return 0


def cmd_family(args: argparse.Namespace) -> int:
    """Manage family members."""
    data = load_data()
    
    if args.add:
        if args.add not in data.family:
            data.family.append(args.add)
            save_data(data)
            print(f"✅ Added {args.add} to family")
        else:
            print(f"⚠️  {args.add} already in family")
        return 0
    
    if args.remove:
        if args.remove in data.family:
            data.family.remove(args.remove)
            save_data(data)
            print(f"🗑️  Removed {args.remove} from family")
        else:
            print(f"❌ {args.remove} not in family")
            return 1
        return 0
    
    if args.json:
        print(json.dumps({"family": data.family}, indent=2))
    else:
        print("👨‍👩‍👧‍👦 Family Members:")
        if not data.family:
            print("  (none added)")
        for name in data.family:
            print(f"  • {name}")
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# CLI Setup
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Grocery List & Meal Planner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # lists
    p_lists = subparsers.add_parser("lists", help="Show all shopping lists")
    p_lists.add_argument("--json", action="store_true", help="JSON output")
    p_lists.set_defaults(func=cmd_lists)
    
    # list <name>
    p_list = subparsers.add_parser("list", help="View or manage a list")
    p_list.add_argument("list_name", help="List name")
    p_list.add_argument("--unchecked", "-u", action="store_true", help="Only unchecked")
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=cmd_list_view)
    
    # list-create
    p_list_create = subparsers.add_parser("list-create", help="Create a new list")
    p_list_create.add_argument("name", help="List name")
    p_list_create.set_defaults(func=cmd_list_create)
    
    # list-delete
    p_list_delete = subparsers.add_parser("list-delete", help="Delete a list")
    p_list_delete.add_argument("name", help="List name")
    p_list_delete.set_defaults(func=cmd_list_delete)
    
    # add
    p_add = subparsers.add_parser("add", help="Add item(s) to a list")
    p_add.add_argument("list_name", help="List name")
    p_add.add_argument("items", nargs="+", help="Item name(s)")
    p_add.add_argument("--category", "-c", help="Category")
    p_add.add_argument("--qty", "-q", help="Quantity (e.g. '2 gallons')")
    p_add.add_argument("--assignee", "-a", help="Assign to family member")
    p_add.set_defaults(func=cmd_add)
    
    # check
    p_check = subparsers.add_parser("check", help="Mark item as checked")
    p_check.add_argument("list_name")
    p_check.add_argument("item")
    p_check.set_defaults(func=cmd_check)
    
    # uncheck
    p_uncheck = subparsers.add_parser("uncheck", help="Uncheck item")
    p_uncheck.add_argument("list_name")
    p_uncheck.add_argument("item")
    p_uncheck.set_defaults(func=cmd_uncheck)
    
    # remove
    p_remove = subparsers.add_parser("remove", help="Remove item from list")
    p_remove.add_argument("list_name")
    p_remove.add_argument("item")
    p_remove.set_defaults(func=cmd_remove)
    
    # clear
    p_clear = subparsers.add_parser("clear", help="Clear checked items")
    p_clear.add_argument("list_name")
    p_clear.set_defaults(func=cmd_clear)
    
    # recipes
    p_recipes = subparsers.add_parser("recipes", help="List all recipes")
    p_recipes.add_argument("--category", "-c", help="Filter by category")
    p_recipes.add_argument("--json", action="store_true")
    p_recipes.set_defaults(func=cmd_recipes)
    
    # recipe <name>
    p_recipe = subparsers.add_parser("recipe", help="View a recipe")
    p_recipe.add_argument("name", help="Recipe name")
    p_recipe.add_argument("--ingredients-only", "-i", action="store_true")
    p_recipe.add_argument("--json", action="store_true")
    p_recipe.set_defaults(func=cmd_recipe_view)
    
    # recipe-add
    p_recipe_add = subparsers.add_parser("recipe-add", help="Add a recipe")
    p_recipe_add.add_argument("name", help="Recipe name")
    p_recipe_add.add_argument("--ingredients", help="Comma-separated ingredients")
    p_recipe_add.add_argument("--instructions", help="Cooking instructions")
    p_recipe_add.add_argument("--category", help="Category (e.g. Mexican, Italian)")
    p_recipe_add.add_argument("--servings", type=int, default=4)
    p_recipe_add.add_argument("--prep-time", help="Prep time")
    p_recipe_add.add_argument("--cook-time", help="Cook time")
    p_recipe_add.add_argument("--notes", help="Notes")
    p_recipe_add.set_defaults(func=cmd_recipe_add)
    
    # recipe-delete
    p_recipe_del = subparsers.add_parser("recipe-delete", help="Delete a recipe")
    p_recipe_del.add_argument("name")
    p_recipe_del.set_defaults(func=cmd_recipe_delete)
    
    # recipe-search
    p_recipe_search = subparsers.add_parser("recipe-search", help="Search recipes")
    p_recipe_search.add_argument("query")
    p_recipe_search.add_argument("--json", action="store_true")
    p_recipe_search.set_defaults(func=cmd_recipe_search)
    
    # meals
    p_meals = subparsers.add_parser("meals", help="Show meal plan")
    p_meals.add_argument("--date", "-d", help="Week containing date (YYYY-MM-DD)")
    p_meals.add_argument("--json", action="store_true")
    p_meals.set_defaults(func=cmd_meals)
    
    # meal-add
    p_meal_add = subparsers.add_parser("meal-add", help="Add meal to plan")
    p_meal_add.add_argument("--date", "-d", help="Date (YYYY-MM-DD, default: today)")
    p_meal_add.add_argument("--type", "-t", required=True, help="breakfast/lunch/dinner/snack")
    p_meal_add.add_argument("--recipe", "-r", help="Recipe name")
    p_meal_add.add_argument("--notes", "-n", help="Notes")
    p_meal_add.set_defaults(func=cmd_meal_add)
    
    # meal-remove
    p_meal_rm = subparsers.add_parser("meal-remove", help="Remove meal from plan")
    p_meal_rm.add_argument("--date", "-d", help="Date")
    p_meal_rm.add_argument("--type", "-t", required=True)
    p_meal_rm.set_defaults(func=cmd_meal_remove)
    
    # meal-add-to-list
    p_meal_list = subparsers.add_parser("meal-add-to-list", help="Add meal ingredients to grocery list")
    p_meal_list.add_argument("--date", "-d", help="Date")
    p_meal_list.add_argument("--list", "-l", default="Grocery", help="Target list")
    p_meal_list.set_defaults(func=cmd_meal_add_to_list)
    
    # stats
    p_stats = subparsers.add_parser("stats", help="Show statistics")
    p_stats.add_argument("--json", action="store_true")
    p_stats.set_defaults(func=cmd_stats)
    
    # notify
    p_notify = subparsers.add_parser("notify", help="Output alerts for heartbeat/cron")
    p_notify.add_argument("--json", action="store_true")
    p_notify.set_defaults(func=cmd_notify)
    
    # family
    p_family = subparsers.add_parser("family", help="Manage family members")
    p_family.add_argument("--add", help="Add member")
    p_family.add_argument("--remove", help="Remove member")
    p_family.add_argument("--json", action="store_true")
    p_family.set_defaults(func=cmd_family)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
