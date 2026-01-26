#!/usr/bin/env python3
"""
Monitor token usage and trigger exports.
Used in heartbeats or cron jobs.
"""

import subprocess
import json
import re
from datetime import datetime

def get_token_usage():
    """Get current session token usage percentage."""
    try:
        # Call session_status via Clawdbot
        # This assumes clawdbot CLI is available
        result = subprocess.run(
            ['clawdbot', 'session-status', '--json'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            usage_percent = data.get('usage_percent', 0)
            return usage_percent
    except Exception as e:
        print(f"Could not fetch token usage: {e}")
    
    return None

def should_export(usage_percent, threshold=95):
    """Check if we should export (at threshold or higher)."""
    return usage_percent is not None and usage_percent >= threshold

def trigger_export():
    """Trigger the export script."""
    try:
        result = subprocess.run(
            ['python', 'skills/remember-all-prompts-daily/scripts/export_prompts.py'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error triggering export: {e}")
        return False

def check_and_export(threshold=95, threshold_low=5):
    """Main checker: monitor usage and export if needed."""
    usage = get_token_usage()
    
    if usage is None:
        print("⚠️  Could not determine token usage")
        return False
    
    print(f"📊 Token Usage: {usage}%")
    
    if usage >= threshold:
        print(f"⚠️  Token usage at {usage}% (threshold: {threshold}%)")
        print("🚀 Triggering prompt export...")
        success = trigger_export()
        if success:
            print("✅ Export successful")
        else:
            print("❌ Export failed")
        return success
    
    elif usage <= threshold_low:
        print(f"✅ Fresh session detected ({usage}%)")
        print("📖 Previous context available for ingestion")
        return True
    
    else:
        print(f"✅ Token usage normal ({usage}%)")
        return False

if __name__ == "__main__":
    import sys
    
    threshold = int(sys.argv[1]) if len(sys.argv) > 1 else 95
    check_and_export(threshold=threshold)
