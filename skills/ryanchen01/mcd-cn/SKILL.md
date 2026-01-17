---
name: mcd-cn
description: Query McDonald's China MCP server via the mcd-cn CLI for campaign calendars, coupons, and auto-claiming. Use for human-friendly coupon lookup or JSON output for scripts.
homepage: https://github.com/ryanchen01/mcd-cn
metadata: {"clawdbot":{"emoji":"🍟","requires":{"bins":["mcd-cn"],"env":["MCDCN_MCP_TOKEN"]},"primaryEnv":"MCDCN_MCP_TOKEN","install":[{"id":"brew","kind":"brew","formula":"ryanchen01/tap/mcd-cn","bins":["mcd-cn"],"label":"Install mcd-cn (brew)"}]}}

---

# mcd-cn

McDonald's China MCP CLI. Human output by default, `--json` for scripts.

Install

- Homebrew: `brew install ryanchen01/tap/mcd-cn`

Config

- `MCDCN_MCP_TOKEN` required. Get it from the McDonald's China MCP console.
- Optional: `MCDCN_MCP_URL` for custom server URL.

Common commands

- Campaign calendar: `mcd-cn campaign-calender`
- Calendar for date: `mcd-cn campaign-calender --specifiedDate 2025-12-09`
- Available coupons: `mcd-cn available-coupons`
- Auto-claim coupons: `mcd-cn auto-bind-coupons`
- My coupons: `mcd-cn my-coupons`
- Current time: `mcd-cn now-time-info`
- JSON output: `mcd-cn available-coupons --json`

Notes

- Token can be set via `MCDCN_MCP_TOKEN` env var or `.env` file.
- Date format for `--specifiedDate` is `yyyy-MM-dd`.
- Rate limit: 600 requests per minute per token.
