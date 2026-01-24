# pdf-form-filler

Fill PDF forms programmatically with text and checkboxes.

A Clawdbot skill for populating fillable PDF forms (government forms, applications, surveys, etc.) with data while preserving proper appearance states for PDF viewer rendering.

## Features

- **Text fields**: Set any text value (names, dates, addresses, etc.)
- **Checkboxes**: Set boolean values (True/False) with proper `/On`/`Off` states
- **Field detection**: Discover all form fields in a PDF
- **Batch processing**: Fill multiple PDFs with the same or different data
- **No dependencies**: Uses pdfrw (lightweight, pure Python)

## Quick Start

```python
from scripts.fill_pdf_form import fill_pdf_form

fill_pdf_form(
    input_pdf="form.pdf",
    output_pdf="form_filled.pdf",
    data={
        "Full Name": "John Doe",
        "Email": "john@example.com",
        "I agree": True,
    }
)
```

## Installation

1. Requires Python 3.7+
2. Install pdfrw:
   ```bash
   pip install pdfrw
   ```

3. Use the skill in Clawdbot or run standalone

## Documentation

- **SKILL.md** - Complete skill documentation with features and examples
- **references/examples.md** - 10+ usage examples and patterns

## Usage Examples

### List PDF fields

```python
from scripts.fill_pdf_form import list_pdf_fields

fields = list_pdf_fields("form.pdf")
for field_name, field_type in fields:
    print(f"{field_name}: {field_type}")
```

### Batch fill

```python
import os
from scripts.fill_pdf_form import fill_pdf_form

data = {"Name": "Jane Doe", "Date": "2026-01-24"}

for filename in os.listdir("forms/"):
    if filename.endswith(".pdf"):
        fill_pdf_form(f"forms/{filename}", f"output/{filename}", data)
```

### Interactive mode

```python
from scripts.fill_pdf_form import list_pdf_fields, fill_pdf_form

pdf_path = "form.pdf"
fields = list_pdf_fields(pdf_path)

data = {}
for field_name, field_type in fields:
    if field_type == "text":
        data[field_name] = input(f"Enter {field_name}: ")
    elif field_type == "checkbox":
        data[field_name] = input(f"Check {field_name}? (y/n): ").lower() == 'y'

fill_pdf_form(pdf_path, "form_filled.pdf", data)
```

## CLI Usage

```bash
python scripts/fill_pdf_form.py input.pdf output.pdf data.json
```

Where `data.json`:
```json
{
  "Full Name": "John Doe",
  "Email": "john@example.com",
  "Approved": true
}
```

## Troubleshooting

### Checkboxes not showing visually

The value is set correctly (`/On` or `/Off`), but some PDF viewers don't regenerate the appearance stream. Try:
- Adobe Reader (renders automatically)
- Firefox
- evince or okular (Linux)

The data is preserved; just the visual appearance differs by viewer.

### Field names not found

Use `list_pdf_fields()` to confirm exact field names:

```python
from scripts.fill_pdf_form import list_pdf_fields

fields = list_pdf_fields("problem_form.pdf")
print("Available fields:")
for name, _ in fields:
    print(f"  '{name}'")
```

## License

MIT

## Contributing

Improvements welcome. Please test with real PDFs before submitting changes.

---

Built with pdfrw. Made for Clawdbot.
