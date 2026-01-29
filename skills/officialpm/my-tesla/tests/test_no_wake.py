import unittest
import sys
from pathlib import Path
from unittest import mock

# Allow importing scripts/tesla.py as a module
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tesla  # noqa: E402


class DummyVehicle(dict):
    def sync_wake_up(self):
        raise AssertionError("sync_wake_up should not be called in this test")


class NoWakeTests(unittest.TestCase):
    def test_wake_vehicle_allow_wake_false_offline_returns_false(self):
        v = DummyVehicle(state="asleep", display_name="Test Car")
        self.assertFalse(tesla.wake_vehicle(v, allow_wake=False))

    def test_wake_vehicle_online_returns_true(self):
        v = DummyVehicle(state="online", display_name="Test Car")
        self.assertTrue(tesla.wake_vehicle(v, allow_wake=False))

    def test_ensure_online_or_exit_exits_3_when_no_wake(self):
        v = DummyVehicle(state="asleep", display_name="Test Car")
        with mock.patch.object(tesla, "wake_vehicle", return_value=False):
            with self.assertRaises(SystemExit) as ctx:
                tesla._ensure_online_or_exit(v, allow_wake=False)
            self.assertEqual(ctx.exception.code, 3)


if __name__ == "__main__":
    unittest.main()
