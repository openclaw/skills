#!/usr/bin/env python3
"""Find My location tracker with street-corner accuracy."""
import subprocess
import json
import re
import os
import sys

CONFIG_PATH = os.path.expanduser("~/.config/findmy-location/config.json")
DEFAULT_CONFIG = {
    "target": None,
    "known_locations": []
}

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG

def get_target_name(config):
    """Get target name from config or USER.md."""
    if config.get("target"):
        return config["target"]
    
    # Try common USER.md locations
    for path in ["~/clawd/USER.md", "~/USER.md", "./USER.md"]:
        user_md = os.path.expanduser(path)
        if os.path.exists(user_md):
            with open(user_md) as f:
                content = f.read()
                m = re.search(r'\*\*(?:Name|What to call them)\*\*:\s*(\w+)', content)
                if m:
                    return m.group(1)
    return None

def find_hsclick():
    """Find hsclick script in common locations."""
    for path in ["~/clawd/scripts/hsclick", "~/.local/bin/hsclick", "/usr/local/bin/hsclick"]:
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded):
            return expanded
    return None

def find_location(config):
    target = get_target_name(config)
    
    # Start Find My
    run('open -a "Find My"')
    run('sleep 0.5')
    run('osascript -e \'tell app "System Events" to set frontmost of process "Find My" to true\'')
    run('sleep 0.3')
    
    # Get window position
    win_json = run('peekaboo list windows --app "Find My" --json 2>/dev/null')
    try:
        win = json.loads(win_json)
        bounds = win.get('data', {}).get('windows', [{}])[0].get('bounds', [[0, 0]])[0]
        wx, wy = bounds[0], bounds[1]
    except:
        wx, wy = 0, 0
    
    # Click on second row (first shared contact)
    hsclick = find_hsclick()
    click_x, click_y = wx + 120, wy + 173
    
    if hsclick:
        run(f'{hsclick} click {click_x} {click_y}')
    else:
        run(f'peekaboo click --coords {click_x},{click_y} --app "Find My" 2>/dev/null')
    run('sleep 1')
    
    # Get accessibility data
    see = run('peekaboo see --app "Find My" --json 2>/dev/null')
    img = f"/tmp/findmy-{os.getpid()}.png"
    run(f'peekaboo image --mode screen --screen-index 0 --path {img} 2>/dev/null')
    
    result = {
        "person": None,
        "address": None,
        "city": None,
        "state": None,
        "status": None,
        "context": "unknown",
        "screenshot": img,
        "needs_vision": False
    }
    
    try:
        data = json.loads(see).get('data', {}) if see else {}
    except:
        data = {}
    
    landmarks = []
    
    def extract(obj):
        if isinstance(obj, dict):
            desc = (obj.get('description', '') or obj.get('label', '')).lower()
            landmarks.append(desc)
            
            # Extract person info
            raw = obj.get('description', '') or ''
            m = re.search(r'([\w.@]+@[\w.]+),\s*([^,]+),\s*(\w{2})\s*[,•]\s*(\w+)', raw)
            if m and not result['person']:
                result['person'] = m.group(1)
                result['city'] = m.group(2).strip()
                result['state'] = m.group(3)
                result['status'] = m.group(4).strip()
            
            for v in obj.values():
                extract(v)
        elif isinstance(obj, list):
            for i in obj:
                extract(i)
    
    extract(data)
    all_text = ' '.join(landmarks)
    
    # Check known locations from config
    for loc in config.get('known_locations', []):
        markers = [m.lower() for m in loc.get('markers', [])]
        if any(m in all_text for m in markers):
            result['address'] = loc.get('address')
            result['context'] = loc.get('name', 'known')
            break
    
    # If no known location matched, flag for vision analysis
    if not result['address']:
        result['needs_vision'] = True
        result['context'] = 'out'
    
    return result

def main():
    config = load_config()
    result = find_location(config)
    
    if '--json' in sys.argv:
        print(json.dumps(result))
    elif result.get('needs_vision'):
        print(f"VISION_NEEDED:{result['screenshot']}")
    else:
        addr = result.get('address') or f"{result['city']}, {result['state']}"
        ctx = result.get('context', 'unknown')
        status = result.get('status', '')
        print(f"{addr} ({ctx}) - {status}")

if __name__ == '__main__':
    main()
