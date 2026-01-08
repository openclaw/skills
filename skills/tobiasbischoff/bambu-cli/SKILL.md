---
name: bambu-cli
description: Operate and troubleshoot BambuLab printers with the bambu-cli (status/watch, print start/pause/resume/stop, files, camera, gcode, AMS, calibration, motion, fans, light, config, doctor). Use when a user asks to control or monitor a BambuLab printer, set up profiles or access codes, or translate a task into safe bambu-cli commands with correct flags, output format, and confirmations.
---

# Bambu CLI

## Overview
Use bambu-cli to configure, monitor, and control BambuLab printers over MQTT/FTPS/camera, producing exact commands and safe defaults.

## Defaults and safety
- Confirm the target printer (profile or IP/serial) and resolve precedence: flags > env > project config > user config.
- Avoid access codes in flags; use `--access-code-file` or `--access-code-stdin` only.
- Require confirmation for destructive actions (stop print, delete files, gcode send, calibrate, reboot); use `--force`/`--confirm` only when the user explicitly agrees.
- Offer `--dry-run` when supported to preview actions.
- Choose output format: human by default, `--json` for structured output, `--plain` for key=value output.

## Quick start
- Configure a profile: `bambu-cli config set --printer <name> --ip <ip> --serial <serial> --access-code-file <path> --default`
- Status: `bambu-cli status`
- Watch: `bambu-cli watch --interval 5`
- Start print: `bambu-cli print start <file.3mf|file.gcode> --plate 1`
- Pause/resume/stop: `bambu-cli print pause|resume|stop`
- Camera snapshot: `bambu-cli camera snapshot --out snapshot.jpg`

## Task guidance
### Setup & config
- Use `config set/list/get/remove` to manage profiles.
- Use env vars to avoid flags in scripts: `BAMBU_PROFILE`, `BAMBU_IP`, `BAMBU_SERIAL`, `BAMBU_ACCESS_CODE_FILE`, `BAMBU_TIMEOUT`, `BAMBU_NO_CAMERA`, `BAMBU_MQTT_PORT`, `BAMBU_FTP_PORT`, `BAMBU_CAMERA_PORT`.
- Note config locations: user `~/.config/bambu/config.json`, project `./.bambu.json`.

### Monitoring
- Use `status` for a one-off snapshot; use `watch` for periodic updates (`--interval`, `--refresh`).
- Use `--json`/`--plain` for scripting.

### Printing
- Use `print start <file>` with `.3mf` or `.gcode`.
- Use `--plate <n|path>` to select a plate number or gcode path inside a 3mf.
- Use `--no-upload` only when the file already exists on the printer; do not use it with `.gcode` input.
- Control AMS: `--no-ams`, `--ams-mapping "0,1"`, `--skip-objects "1,3"`.
- Disable flow calibration with `--flow-calibration=false` if requested.

### Files and camera
- Use `files list [--dir <path>]`, `files upload <local> [--as <remote>]`.
- Use `files download <remote> --out <path|->`; use `--force` to allow writing binary data to a TTY.
- Use `files delete <remote>` only with confirmation.
- Use `camera snapshot --out <path|->`; use `--force` to allow stdout to a TTY.

### Motion, temps, fans, light
- Use `home`, `move z --height <0-256>`.
- Use `temps get|set` (`--bed`, `--nozzle`, `--chamber`; require at least one).
- Use `fans set` with `--part/--aux/--chamber` values `0-255` or `0-1`.
- Use `light on|off|status`.

### Gcode and calibration
- Use `gcode send <line...>` or `gcode send --stdin` (confirmation required; `--no-check` skips validation).
- Avoid combining `--access-code-stdin` with `gcode send --stdin`; use an access code file instead.
- Use `calibrate` with `--no-bed-level`, `--no-motor-noise`, `--no-vibration` when requested.

### Troubleshooting
- Use `doctor` to check TCP connectivity to MQTT/FTPS/camera ports; suggest `--no-camera` if the camera port is unreachable.
- Assume default ports: MQTT 8883, FTPS 990, camera 6000 unless configured.

## Reference
Read `references/commands.md` for the full command and flag reference.
