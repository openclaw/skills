# Changelog

## 0.1.22 — 2026-01-28
- UX: include TPMS tire pressures in `report` output when available.
- Docs/privacy: remove personal default-car example from README/SKILL.

## 0.1.21 — 2026-01-28
- Reliability/privacy: remove accidentally committed Python bytecode (`__pycache__`) and sanitize unit test fixtures.

## 0.1.20 — 2026-01-28
- Improve UX: `--car` now accepts partial name (substring match) or a 1-based index from `list`.
- Add unit tests for vehicle selection.

## 0.1.19 — 2026-01-28
- Add `tires` command to show TPMS tire pressures (read-only; supports `--no-wake`).

## 0.1.18 — 2026-01-28
- Add `sentry` command (status/on/off) with `--yes` safety gate for toggles.
- Show Sentry state in `report` output + add a unit test for it.

## 0.1.17 — 2026-01-28
- Add unit tests for `--no-wake` behavior (wake gating + exit code).

## 0.1.16 — 2026-01-28
- Add `--no-wake` to read-only commands to avoid waking the vehicle (fails if asleep/offline).

## 0.1.15 — 2026-01-28
- Add `charge-port` command (open/close) with `--yes` safety gate.

## 0.1.14 — 2026-01-28
- Safety: require `--yes` for `unlock` and `charge start|stop` to avoid accidental disruptive actions.

## 0.1.13 — 2026-01-28
- Improve UX: clearer validation + errors for `charge limit` and `climate temp`.

## 0.1.12 — 2026-01-28
- Make `location` safer by default: show approximate (rounded) coordinates unless `--yes` is provided for precise.

## 0.1.11 — 2026-01-28
- Remove `--yes` safety gate from `location` (prints coordinates + maps link without confirmation).

## 0.1.10 — 2026-01-28
- Refactor: centralize missing-email handling into a single helper with a clearer example.
- Clarify --yes help text to include scheduled-charging set|off.

## 0.1.9 — 2026-01-28
- Add `scheduled-charging` command (status/set/off) with safety gate; show scheduled charging info in `report`.

## 0.1.8 — 2026-01-28
- Improve UX: clearer error when Tesla email is missing (instead of confusing auth failures).

## 0.1.7 — 2026-01-28
- Add `windows` command to vent/close windows (safety gated with `--yes`).

## 0.1.6 — 2026-01-28
- Add unit tests for status/report formatting helpers.
- Clarify `--yes` help text to cover all safety-gated commands.

## 0.1.5 — 2026-01-28
- Include `VERSION.txt` in published skill artifacts (ClawdHub ignores extensionless files like `VERSION`).

## 0.1.4 — 2026-01-28
- Add `trunk` command (trunk/frunk) with safety gate (`--yes`).
- Make `location` safety gated (`--yes`) to reduce accidental sensitive output.

## 0.1.3 — 2026-01-28
- Add `report` command: a one-screen, chat-friendly status report.
- Fix `climate temp` units: default is °F, with `--celsius` for °C.

## 0.1.2 — 2026-01-28
- Add `default-car` command and local defaults file (`~/.my_tesla.json`) so you can set a default vehicle.
- Reduce sensitive output: stop printing VINs in `auth`/`list` by default.

## 0.1.1 — 2026-01-28
- Add `summary` command for a one-line, chat-friendly status output.

## 0.1.0 — 2026-01-28
- Forked from the base `tesla` skill and enhanced into `my-tesla`.
- Added safety confirmation gate for disruptive actions.
- Added `charge limit` command.
- Added author attribution + versioning for publishing.
