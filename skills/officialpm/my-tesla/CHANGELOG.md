# Changelog

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
