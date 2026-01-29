# apple-media

Discover and control AirPlay / Apple media devices from macOS.

This repo contains the **Clawdbot skill** located in `SKILL.md` plus helper scripts under `scripts/`.

## Author

Parth Maniar — [@officialpm](https://github.com/officialpm)

## What it does

- **Scan** the local network for AirPlay devices (HomePod, Apple TV, AirPlay TVs)
- Provide a **JSON** summary of discovered devices
- Delegate **speaker volume/routing** control to Airfoil (reliable for HomePods)
- Use **pyatv** (`atvremote`) for Apple TV / supported device control

## Install / setup

### pyatv (recommended via pipx)

```bash
brew install pipx
pipx install pyatv || pipx upgrade pyatv

# Pin to Python 3.12 to avoid Python 3.14 asyncio issues
pipx reinstall pyatv --python python3.12
```

Verify:

```bash
atvremote --help | head
```

### Airfoil (optional but recommended for HomePods)

Install Airfoil and grant Accessibility permissions.

- `brew install --cask airfoil`

## Usage

### Scan (text)

```bash
./scripts/scan.sh 5
```

### Scan (JSON)

```bash
node ./scripts/scan-json.js 5
```

### Faster scan (known IPs)

```bash
./scripts/scan-hosts.sh "10.0.0.28,10.0.0.111" 3
```

### Control HomePod volume (Airfoil)

```bash
# Requires Airfoil + the Clawdbot airfoil skill scripts
./scripts/connect.sh "Living Room"
./scripts/volume.sh "Living Room" 35
```

## Privacy / safety

- This repo intentionally avoids committing any personal data (no resume paths, no tokens, no device credentials).
- The scan output includes IP addresses at runtime; **do not commit scan outputs**.
