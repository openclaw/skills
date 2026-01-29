---
name: wps-ppt-automation
description: Automate common PowerPoint/WPS Presentation operations on Windows via COM (read text/notes/outline, export PDF/images, replace text, insert/delete slides, unify font/size/theme, extract images/media). Use for single-presentation actions (no batch).
---

# WPS/PowerPoint Automation (Windows)

Use the bundled Python script to control PowerPoint or WPS Presentation via COM.

## Requirements

- Windows with **Microsoft PowerPoint** or **WPS Presentation** installed.
- Python + **pywin32** (`python -m pip install pywin32`).

## Quick start

```bash
python {baseDir}/scripts/wps_ppt_automation.py read --input "C:\path\file.pptx"
python {baseDir}/scripts/wps_ppt_automation.py export --input "C:\path\file.pptx" --format pdf --output "C:\path\out.pdf"
```

## Commands

### read
Extract all slide text.

```bash
python {baseDir}/scripts/wps_ppt_automation.py read --input "C:\path\file.pptx" --output "C:\path\out.txt"
```

### notes
Extract speaker notes.

```bash
python {baseDir}/scripts/wps_ppt_automation.py notes --input "C:\path\file.pptx" --output "C:\path\notes.txt"
```

### outline
Export slide titles as outline.

```bash
python {baseDir}/scripts/wps_ppt_automation.py outline --input "C:\path\file.pptx" --output "C:\path\outline.txt"
```

### export
Export to PDF or images (PNG).

```bash
python {baseDir}/scripts/wps_ppt_automation.py export --input "C:\path\file.pptx" --format pdf --output "C:\path\out.pdf"
python {baseDir}/scripts/wps_ppt_automation.py export --input "C:\path\file.pptx" --format images --outdir "C:\out\slides"
```

### replace
Find/replace text across slides.

```bash
python {baseDir}/scripts/wps_ppt_automation.py replace --input "C:\path\file.pptx" --find "old" --replace "new" --save "C:\path\out.pptx"
```

### slides
Insert or delete slides.

```bash
python {baseDir}/scripts/wps_ppt_automation.py insert-slide --input "C:\path\file.pptx" --index 2 --save "C:\path\out.pptx"
python {baseDir}/scripts/wps_ppt_automation.py delete-slide --input "C:\path\file.pptx" --index 3 --save "C:\path\out.pptx"
```

### font
Unify font name/size across slides.

```bash
python {baseDir}/scripts/wps_ppt_automation.py font --input "C:\path\file.pptx" --name "Microsoft YaHei" --size 20 --save "C:\path\out.pptx"
```

### theme
Apply a theme (.thmx).

```bash
python {baseDir}/scripts/wps_ppt_automation.py theme --input "C:\path\file.pptx" --theme "C:\path\theme.thmx" --save "C:\path\out.pptx"
```

### extract-images
Export embedded images.

```bash
python {baseDir}/scripts/wps_ppt_automation.py extract-images --input "C:\path\file.pptx" --outdir "C:\out\images"
```

## Notes

- If WPS is installed, try `--app wps`; otherwise default uses PowerPoint.
- Use `--visible true` if you need to watch the UI.
- Avoid batch usage; this skill is for single-presentation operations.
