#!/usr/bin/env python3
"""
IBKR Session Keepalive Script
Run via cron every 5 minutes to keep session active.

Crontab entry:
*/5 * * * * cd /path/to/trading && venv/bin/python keepalive.py >> keepalive.log 2>&1
"""

import requests
import urllib3
import subprocess
import os
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = os.getenv("IBEAM_GATEWAY_BASE_URL", "https://localhost:5000")
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "keepalive.log")

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {msg}")

def check_auth_status():
    """Check if session is authenticated."""
    try:
        r = requests.get(
            f"{BASE_URL}/v1/api/iserver/auth/status",
            verify=False,
            timeout=10
        )
        data = r.json()
        return data.get("authenticated", False), data
    except Exception as e:
        return False, {"error": str(e)}

def tickle():
    """Send keepalive ping."""
    try:
        r = requests.post(
            f"{BASE_URL}/v1/api/tickle",
            verify=False,
            timeout=10
        )
        return r.status_code == 200
    except:
        return False

def trigger_reauth():
    """Trigger re-authentication via IBeam."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    auth_script = os.path.join(script_dir, "..", "authenticate.sh")
    
    if os.path.exists(auth_script):
        log("🔄 Session expired - triggering re-authentication...")
        log("📱 Check your phone for IBKR Key notification!")
        subprocess.Popen(["bash", auth_script], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        return True
    return False

def main():
    # Check if gateway is running
    auth_ok, status = check_auth_status()
    
    if "error" in status:
        log(f"❌ Gateway not responding: {status['error']}")
        return
    
    if auth_ok:
        # Session active - just tickle
        if tickle():
            log("✅ Session active - keepalive sent")
        else:
            log("⚠️ Tickle failed but session reports authenticated")
    else:
        # Session expired
        log("⚠️ Session not authenticated")
        if trigger_reauth():
            log("📱 Re-auth triggered - waiting for phone approval...")
        else:
            log("❌ Could not find authenticate.sh script")

if __name__ == "__main__":
    main()
