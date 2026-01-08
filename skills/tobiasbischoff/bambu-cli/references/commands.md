# bambu-cli command reference

## Global flags
- `-h, --help`, `--version`
- `-q, --quiet`, `-v, --verbose`
- `--json` | `--plain` (mutually exclusive)
- `--no-color`
- `--no-input`
- `-f, --force`
- `--confirm <token>`
- `-n, --dry-run`
- `--printer <name>`
- `--ip <addr>`
- `--serial <serial>`
- `--access-code-file <path>`
- `--access-code-stdin`
- `--no-camera`
- `--timeout <seconds>`
- `--config <path>`

## Commands
- `status` - show printer status.
- `watch [--interval <seconds>] [--refresh]` - stream status updates.
- `light on|off|status` - control printer light.
- `temps get|set [--bed <C>] [--nozzle <C>] [--chamber <C>]` - set requires at least one value.
- `print start <file> [--plate <n|path>] [--no-upload] [--no-ams] [--ams-mapping <list>] [--skip-objects <list>] [--flow-calibration[=true|false]] [--remote-name <name>]`
- `print pause|resume|stop` - stop requires confirmation.
- `files list [--dir <path>]`
- `files upload <local> [--as <remote>]`
- `files download <remote> --out <path|->` (use `--force` for stdout on TTY)
- `files delete <remote>` - confirmation required.
- `camera snapshot [--out <path|->]` - default `snapshot.jpg` (use `--force` for stdout on TTY).
- `gcode send <line...> | --stdin` - confirmation required; `--no-check` to skip validation.
- `ams status` - show AMS data.
- `calibrate [--no-bed-level] [--no-motor-noise] [--no-vibration]` - confirmation required.
- `home` - home axes.
- `move z --height <0-256>` - move Z.
- `fans set [--part <0-255|0-1>] [--aux <0-255|0-1>] [--chamber <0-255|0-1>]`
- `reboot` - confirmation required.
- `config list|get|set|remove`
- `doctor` - check port reachability.

## Config and env
- User config: `~/.config/bambu/config.json`
- Project config: `./.bambu.json`
- Precedence: flags > env > project config > user config
- Env vars: `BAMBU_PROFILE`, `BAMBU_IP`, `BAMBU_SERIAL`, `BAMBU_ACCESS_CODE_FILE`, `BAMBU_TIMEOUT`, `BAMBU_NO_CAMERA`, `BAMBU_MQTT_PORT`, `BAMBU_FTP_PORT`, `BAMBU_CAMERA_PORT`

## Notes
- Do not pass access codes via flags; use `--access-code-file` or `--access-code-stdin`.
- `--access-code-stdin` cannot be combined with `gcode send --stdin`.
- Default ports: MQTT 8883, FTPS 990, camera 6000.
