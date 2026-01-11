# Changelog

## 1.1.1

- Auth hardening: reject wrong token types early (local triple-part key vs cloud token) and validate token characters to avoid invalid HTTP header errors.

## 1.1.0

- Add **local + cloud** connection modes with `HOMEY_MODE=auto|local|cloud`.
- Add local onboarding:
  - `homeycli auth discover-local` (mDNS)
  - `homeycli auth discover-local --save --pick <n>` / `--homey-id <id>`
  - `homeycli auth set-local` (stores local API key)
- Improve cloud/headless setup (`auth set-token --stdin/--prompt`) and clearer `auth status` output.
- Refactor name/id resolution to be deterministic and shared across devices/flows.
- Docs: updated setup instructions + stable JSON output contract (`docs/output.md`).

## 1.0.1

- LLM-friendly output improvements: IDs always included, multi-sensor friendly `values` map.
- Added `snapshot` command (status + zones + devices; optional flows).
- Added `--match` filtering for `devices` and `flows`.
- Added `auth set-token` and `auth status` helper commands.
- Improved ambiguous name handling (returns candidates, asks for ID).
