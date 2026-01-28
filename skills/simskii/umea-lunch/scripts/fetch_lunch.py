#!/usr/bin/env python3
"""
Fetch lunch menus from umealunchguide.se
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime


def fetch_lunch_data():
    """Fetch and parse lunch data from umealunchguide.se"""
    url = "https://umealunchguide.se/"
    
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; LunchBot/1.0)'
    })
    
    with urllib.request.urlopen(req, timeout=30) as response:
        html = response.read().decode('utf-8')
    
    # Extract JSON from window.__data__ = decodeURIComponent("...");
    match = re.search(r'window\.__data__\s*=\s*decodeURIComponent\("([^"]+)"\)', html)
    if not match:
        raise ValueError("Could not find lunch data in page")
    
    encoded_json = match.group(1)
    decoded_json = urllib.parse.unquote(encoded_json)
    return json.loads(decoded_json)


def format_courses(courses, menu_type="advanced"):
    """Format course list for output"""
    result = []
    if menu_type == "simple":
        # Simple menus have courses as list of strings
        for course in courses:
            result.append({"title": course, "description": None, "price": None, "tags": []})
    else:
        # Advanced menus have course objects
        for course in courses:
            tags = []
            for tag in course.get("tags", []):
                if isinstance(tag, dict):
                    tags.append(tag.get("displayName", ""))
                else:
                    tags.append(str(tag))
            
            result.append({
                "title": course.get("title", ""),
                "description": course.get("description"),
                "price": course.get("price"),
                "tags": [t for t in tags if t]
            })
    return result


def get_lunches(data, date=None, restaurant_filter=None):
    """Extract lunch menus for a given date"""
    if date is None:
        date = data.get("dates", {}).get("today", datetime.now().strftime("%Y-%m-%d"))
    
    restaurants = []
    
    for restaurant in data.get("restaurants", []):
        meta = restaurant.get("meta", {})
        name = meta.get("name", "Unknown")
        
        # Apply restaurant filter if provided
        if restaurant_filter:
            if restaurant_filter.lower() not in name.lower():
                continue
        
        lunches = restaurant.get("lunches", {})
        day_lunch = lunches.get(date, {})
        
        if not day_lunch:
            continue
        
        courses_raw = day_lunch.get("courses", [])
        if not courses_raw:
            continue
        
        menu_type = day_lunch.get("type", "advanced")
        courses = format_courses(courses_raw, menu_type)
        
        # Filter out empty courses
        courses = [c for c in courses if c["title"]]
        
        if not courses:
            continue
        
        restaurants.append({
            "name": name,
            "slug": meta.get("slug", ""),
            "address": meta.get("address", ""),
            "phone": meta.get("phone", ""),
            "website": meta.get("website", ""),
            "standardPrice": meta.get("standardLunchPrice"),
            "courses": courses
        })
    
    return {
        "date": date,
        "availableDates": data.get("dates", {}).get("availableDates", []),
        "restaurantCount": len(restaurants),
        "restaurants": restaurants
    }


def list_restaurants(data):
    """List all available restaurants"""
    restaurants = []
    for restaurant in data.get("restaurants", []):
        meta = restaurant.get("meta", {})
        restaurants.append({
            "name": meta.get("name", "Unknown"),
            "slug": meta.get("slug", ""),
            "address": meta.get("address", "")
        })
    return sorted(restaurants, key=lambda x: x["name"])


def main():
    parser = argparse.ArgumentParser(description="Fetch Umeå lunch menus")
    parser.add_argument("--date", help="Date in YYYY-MM-DD format (default: today)")
    parser.add_argument("--restaurant", "-r", help="Filter by restaurant name (partial match)")
    parser.add_argument("--list", "-l", action="store_true", help="List all restaurants")
    args = parser.parse_args()
    
    try:
        data = fetch_lunch_data()
        
        if args.list:
            restaurants = list_restaurants(data)
            print(json.dumps({"restaurants": restaurants}, ensure_ascii=False, indent=2))
        else:
            result = get_lunches(data, date=args.date, restaurant_filter=args.restaurant)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
