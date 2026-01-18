#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pydexcom", "fire"]
# ///

import json
import os

from pydexcom import Dexcom
import fire


def get_reading():
    """Get current glucose reading."""
    username = os.getenv("DEXCOM_USER")
    password = os.getenv("DEXCOM_PASSWORD")
    region = os.getenv("DEXCOM_REGION", "ous")

    if not username or not password:
        raise SystemExit("Missing DEXCOM_USER or DEXCOM_PASSWORD")

    dexcom = Dexcom(username=username, password=password, region=region)
    reading = dexcom.get_current_glucose_reading()
    return {
        "mg_dl": reading.mg_dl,
        "mmol_l": reading.mmol_l,
        "trend": reading.trend_description,
        "time": str(reading.datetime),
    }


def report():
    """Print formatted glucose report."""
    r = get_reading()
    trend_emoji = {
        "rising quickly": "⬆️⬆️",
        "rising": "⬆️",
        "rising slightly": "↗️",
        "steady": "➡️",
        "falling slightly": "↘️",
        "falling": "⬇️",
        "falling quickly": "⬇️⬇️",
    }.get(r["trend"].lower(), "❓")

    mg = r["mg_dl"]
    if mg < 70:
        status = "🔴 LOW"
    elif mg < 80:
        status = "🟡 Low"
    elif mg <= 140:
        status = "🟢 In range"
    elif mg <= 180:
        status = "🟡 High"
    else:
        status = "🔴 HIGH"

    print(f"🩸 Glucose: {mg} mg/dL ({r['mmol_l']:.1f} mmol/L)")
    print(f"📈 Trend: {r['trend']} {trend_emoji}")
    print(f"🎯 Status: {status}")
    print(f"⏰ {r['time']}")


def json_output():
    """Print raw reading as JSON."""
    print(json.dumps(get_reading(), indent=2, sort_keys=True))


if __name__ == "__main__":
    fire.Fire(
        {
            "now": report,
            "json": json_output,
        }
    )
