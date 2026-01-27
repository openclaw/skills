---
name: pymupdf-pdf
description: Fast local PDF parsing with PyMuPDF (fitz) for Markdown/JSON outputs and optional images/tables. Use when speed matters more than robustness, or as a fallback while heavier parsers are unavailable. Default to single-PDF parsing with per-document output folders.
---

# PyMuPDF PDF

## Overview
Parse PDFs locally using PyMuPDF for fast, lightweight extraction into Markdown by default, with optional JSON and image/table outputs in a per-document directory.

## Prereqs / when to read references
If you hit import errors (PyMuPDF not installed) or Nix `libstdc++` issues, read:
- `references/pymupdf-notes.md`

## Quick start (single PDF)
```bash
# Run from the skill directory
./scripts/pymupdf_parse.py /path/to/file.pdf \
  --format md \
  --outroot ./pymupdf-output
```

## Options
- `--format md|json|both` (default: `md`)
- `--images` to extract images
- `--tables` to extract a simple line-based table JSON (quick/rough)
- `--outroot DIR` to change output root
- `--lang` adds a language hint into JSON output metadata

## Output conventions
- Create `./pymupdf-output/<pdf-basename>/` by default.
- Markdown output: `output.md`
- JSON output: `output.json` (includes `lang`)
- Images: `images/` subdir
- Tables: `tables.json` (rough line-based)

## Notes
- PyMuPDF is fast but less robust on complex PDFs.
- For more robust parsing, use a heavy-duty OCR parser (e.g., MinerU) if installed.
