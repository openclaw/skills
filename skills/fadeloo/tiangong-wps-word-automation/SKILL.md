---
name: wps-word-automation
description: Automate common Word/WPS document operations on Windows via COM (read text, replace, insert, headings, headers/footers, page breaks, merge, split, export to PDF/TXT, add/replace images). Use for single-document actions (no batch).
---

# WPS/Word Automation (Windows)

Use the bundled Python script to control Word or WPS via COM.

## Requirements

- Windows with **Microsoft Word** or **WPS Writer** installed.
- Python + **pywin32** (`python -m pip install pywin32`).

## Quick start

```bash
python {baseDir}/scripts/wps_word_automation.py read --input "C:\path\file.docx"
python {baseDir}/scripts/wps_word_automation.py replace --input "C:\path\file.docx" --find "旧" --replace "新" --save "C:\path\out.docx"
python {baseDir}/scripts/wps_word_automation.py export --input "C:\path\file.docx" --format pdf --output "C:\path\out.pdf"
```

## Commands

### read
Extract plain text.

```bash
python {baseDir}/scripts/wps_word_automation.py read --input "C:\path\file.docx" --output "C:\path\out.txt"
```

### replace
Find/replace text.

```bash
python {baseDir}/scripts/wps_word_automation.py replace --input "C:\path\file.docx" --find "old" --replace "new" --save "C:\path\out.docx"
```

### insert
Insert text at start/end.

```bash
python {baseDir}/scripts/wps_word_automation.py insert --input "C:\path\file.docx" --text "Hello" --where start --save "C:\path\out.docx"
```

### headings
Apply Heading 1/2/3 to matching lines.

```bash
python {baseDir}/scripts/wps_word_automation.py headings --input "C:\path\file.docx" --level 1 --prefix "# " --save "C:\path\out.docx"
```

### header-footer
Set header/footer text.

```bash
python {baseDir}/scripts/wps_word_automation.py header-footer --input "C:\path\file.docx" --header "标题" --footer "页脚" --save "C:\path\out.docx"
```

### page-break
Insert a page break at the end.

```bash
python {baseDir}/scripts/wps_word_automation.py page-break --input "C:\path\file.docx" --save "C:\path\out.docx"
```

### merge
Merge multiple docs into one.

```bash
python {baseDir}/scripts/wps_word_automation.py merge --inputs "a.docx" "b.docx" --output "merged.docx"
```

### split
Split by page ranges (e.g., "1-3,4-6").

```bash
python {baseDir}/scripts/wps_word_automation.py split --input "C:\path\file.docx" --pages "1-3,4-6" --outdir "C:\out"
```

### export
Export to PDF or TXT.

```bash
python {baseDir}/scripts/wps_word_automation.py export --input "C:\path\file.docx" --format pdf --output "C:\path\out.pdf"
python {baseDir}/scripts/wps_word_automation.py export --input "C:\path\file.docx" --format txt --output "C:\path\out.txt"
```

### image
Add or replace image at the end.

```bash
python {baseDir}/scripts/wps_word_automation.py image --input "C:\path\file.docx" --image "C:\path\img.png" --save "C:\path\out.docx"
```

## Notes

- If WPS is installed, try `--app wps`; otherwise default uses Word.
- Use `--visible true` if you need to watch the UI.
- Avoid batch usage; this skill is for single-document operations.
