import unittest
import sys
from pathlib import Path

# Allow importing scripts/tesla.py as a module
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tesla  # noqa: E402


class VehicleSelectTests(unittest.TestCase):
    def setUp(self):
        self.vehicles = [
            {"display_name": "My Model 3"},
            {"display_name": "Road Trip"},
            {"display_name": "Model Y"},
        ]

    def test_select_vehicle_default_first(self):
        v = tesla._select_vehicle(self.vehicles, None)
        self.assertEqual(v["display_name"], "My Model 3")

    def test_select_vehicle_exact_case_insensitive(self):
        v = tesla._select_vehicle(self.vehicles, "model y")
        self.assertEqual(v["display_name"], "Model Y")

    def test_select_vehicle_partial_substring(self):
        v = tesla._select_vehicle(self.vehicles, "road")
        self.assertEqual(v["display_name"], "Road Trip")

    def test_select_vehicle_index_1_based(self):
        v = tesla._select_vehicle(self.vehicles, "2")
        self.assertEqual(v["display_name"], "Road Trip")

    def test_select_vehicle_ambiguous_returns_none(self):
        vehicles = [
            {"display_name": "Alpha"},
            {"display_name": "Alphanumeric"},
        ]
        self.assertIsNone(tesla._select_vehicle(vehicles, "alp"))


if __name__ == "__main__":
    unittest.main()
