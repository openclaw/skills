#!/usr/bin/env python3
import requests
import sys
import json

BASE_URL = "https://data.bmkg.go.id/DataMKG/TEWS/"

def fetch_data(endpoint):
    try:
        response = requests.get(BASE_URL + endpoint, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def format_gempa(g):
    return (f"Time: {g.get('Tanggal')} {g.get('Jam')}\n"
            f"Magnitude: {g.get('Magnitude')}\n"
            f"Depth: {g.get('Kedalaman')}\n"
            f"Location: {g.get('Wilayah')}\n"
            f"Coords: {g.get('Coordinates')}\n"
            f"Potensi: {g.get('Potensi', 'N/A')}\n"
            f"Felt: {g.get('Dirasakan', 'N/A')}")

def fetch_raw(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "latest"
    
    if mode == "latest":
        data = fetch_data("autogempa.json")
        if "error" in data:
            print(f"Error: {data['error']}")
            return
        g = data.get("Infogempa", {}).get("gempa", {})
        print("--- LATEST SIGNIFICANT EARTHQUAKE (M5.0+) ---")
        print(format_gempa(g))
        
        # Link logic for additional details
        dt = g.get("DateTime", "")
        if dt:
            print("\n[TIP] Check detailed static reports if available:")
            print("- History: https://static.bmkg.go.id/history.<EVENT_ID>.txt")
            print("- Moment Tensor: https://static.bmkg.go.id/mt.<EVENT_ID>.txt")

    elif mode == "detail":
        if len(sys.argv) < 3:
            print("Usage: get_gempa.py detail <EVENT_ID>")
            return
        eid = sys.argv[2]
        history = fetch_raw(f"https://static.bmkg.go.id/history.{eid}.txt")
        mt = fetch_raw(f"https://static.bmkg.go.id/mt.{eid}.txt")
        
        print(f"--- DETAILED DATA FOR EVENT: {eid} ---")
        print("\n[MOMENT TENSOR]")
        print(mt)
        print("\n[HISTORY/PHASES]")
        print(history)

    elif mode == "felt":
        data = fetch_data("gempadirasakan.json")
        if "error" in data:
            print(f"Error: {data['error']}")
            return
        list_g = data.get("Infogempa", {}).get("gempa", [])
        print("--- LATEST FELT EARTHQUAKES ---")
        for g in list_g[:5]:  # Show top 5
            print(format_gempa(g))
            print("-" * 20)
            
    elif mode == "recent":
        data = fetch_data("gempaterkini.json")
        if "error" in data:
            print(f"Error: {data['error']}")
            return
        list_g = data.get("Infogempa", {}).get("gempa", [])
        print("--- RECENT EARTHQUAKES (M5.0+) ---")
        for g in list_g[:5]:
            print(format_gempa(g))
            print("-" * 20)
    else:
        print("Usage: get_gempa.py [latest|felt|recent|detail]")

if __name__ == "__main__":
    main()
