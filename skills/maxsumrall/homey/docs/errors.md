# Errors and exit codes

When `--json` is set, errors are printed as JSON to stdout:

```json
{ "error": { "code": "AMBIGUOUS", "message": "...", "details": { "candidates": [ ... ] } } }
```

When `--json` is not set, errors go to stderr in a Unix-style format.

## Exit codes

- `0` success
- `2` configuration/auth error (e.g. no token)
- `3` not found
- `4` ambiguous match (use an ID)
- `5` invalid value / capability not supported
- `1` generic/unexpected
