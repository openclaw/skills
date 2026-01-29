import unittest
import sys
from pathlib import Path

# Allow importing scripts/tesla.py as a module
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tesla  # noqa: E402


class FormattingTests(unittest.TestCase):
    def test_c_to_f(self):
        self.assertAlmostEqual(tesla._c_to_f(0), 32)
        self.assertAlmostEqual(tesla._c_to_f(20), 68)

    def test_fmt_temp_pair(self):
        self.assertIsNone(tesla._fmt_temp_pair(None))
        self.assertEqual(tesla._fmt_temp_pair(20), "20°C (68°F)")

    def test_short_status_contains_expected_bits(self):
        vehicle = {"display_name": "Test Car"}
        data = {
            "charge_state": {
                "battery_level": 55,
                "battery_range": 123.4,
                "charging_state": "Stopped",
            },
            "climate_state": {"inside_temp": 20, "is_climate_on": False},
            "vehicle_state": {"locked": True},
        }

        out = tesla._short_status(vehicle, data)
        self.assertIn("🚗 Test Car", out)
        self.assertIn("Locked", out)
        self.assertIn("55%", out)
        self.assertIn("123 mi", out)
        self.assertIn("⚡ Stopped", out)
        self.assertIn("68°F", out)
        self.assertIn("Off", out)

    def test_report_is_one_screen(self):
        vehicle = {"display_name": "Test Car", "state": "online"}
        data = {
            "charge_state": {
                "battery_level": 80,
                "battery_range": 250.2,
                "charging_state": "Charging",
                "charge_limit_soc": 90,
                "time_to_full_charge": 1.5,
                "charge_rate": 30,
            },
            "climate_state": {"inside_temp": 21, "outside_temp": 10, "is_climate_on": True},
            "vehicle_state": {"locked": False, "odometer": 12345.6},
        }

        out = tesla._report(vehicle, data)
        # Basic structure
        self.assertTrue(out.startswith("🚗 Test Car"))
        self.assertIn("State: online", out)
        self.assertIn("Locked: No", out)
        self.assertIn("Battery: 80% (250 mi)", out)
        self.assertIn("Charging: Charging", out)
        self.assertIn("Inside:", out)
        self.assertIn("Outside:", out)
        self.assertIn("Odometer: 12346 mi", out)


if __name__ == "__main__":
    unittest.main()
