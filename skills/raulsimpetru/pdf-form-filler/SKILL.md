---
name: pdf-form-filler
description: Fill PDF forms programmatically with text values and checkboxes. Use when you need to populate fillable PDF forms (government forms, applications, surveys, etc.) with data. Supports setting text fields and checkboxes with proper appearance states for visual rendering.
---

# PDF Form Filler

Programmatically fill PDF forms with text values and checkboxes. Uses pdfrw to set form field values while preserving appearance streams for proper PDF viewer rendering.

## Quick Start

Fill a PDF form with a dictionary of field names and values:

```python
from pdf_form_filler import fill_pdf_form

fill_pdf_form(
    input_pdf="form.pdf",
    output_pdf="form_filled.pdf",
    data={
        "Name": "John Doe",
        "Email": "john@example.com",
        "Herr": True,  # Checkbox
        "Dienstreise": True,
    }
)
```

## Features

- **Text fields**: Set any text value (names, dates, addresses, etc.)
- **Checkboxes**: Set boolean values (True for checked, False/None for unchecked)
- **Appearance states**: Properly sets `/On` and `/Off` states for PDF viewer rendering
- **Preserves structure**: Doesn't strip form functionality—can be further edited
- **No dependencies**: Uses pdfrw (lightweight, pure Python)

## How It Works

1. Opens the PDF template
2. Iterates through form fields
3. Sets values for matching field names
4. Handles checkboxes by setting both `/V` (value) and `/AS` (appearance state)
5. Saves the filled PDF

## Field Name Matching

Field names should match exactly as they appear in the PDF form. Common patterns:

- German forms: `Herr`, `Frau`, `Dienstreise`, `Geschäftsnummer LfF`
- English forms: `Full Name`, `Email`, `Agree`, `Submit`
- Date fields: `Date`, `DOB`, `Start Date`

To discover field names in your PDF, use `list_pdf_fields()`:

```python
from pdf_form_filler import list_pdf_fields

fields = list_pdf_fields("form.pdf")
for field_name, field_type in fields:
    print(f"{field_name}: {field_type}")
```

Field types:
- `text`: Text input field
- `checkbox`: Boolean checkbox
- `radio`: Radio button
- `dropdown`: Dropdown select
- `signature`: Signature field

## Example: Job Application Form

```python
fill_pdf_form(
    input_pdf="job_application.pdf",
    output_pdf="job_application_filled.pdf",
    data={
        "Full Name": "Jane Smith",
        "Email": "jane.smith@example.com",
        "Phone": "555-1234",
        "Position": "Software Engineer",
        "Years Experience": "5",
        
        # Checkboxes
        "Willing to relocate": True,
        "Available immediately": False,
        "Background check consent": True,
    }
)
```

## Advanced Usage

### Partial fills

Only fill specific fields, leave others blank:

```python
data = {"Name": "Jane Doe"}  # Only Name is set
fill_pdf_form("form.pdf", "form_filled.pdf", data)
```

### Dynamic field detection

Get all fields and prompt for values:

```python
from pdf_form_filler import list_pdf_fields

fields = list_pdf_fields("form.pdf")
data = {}
for field_name, field_type in fields:
    if field_type == "text":
        data[field_name] = input(f"Enter {field_name}: ")
    elif field_type == "checkbox":
        data[field_name] = input(f"Check {field_name}? (y/n): ").lower() == 'y'

fill_pdf_form("form.pdf", "form_filled.pdf", data)
```

### Batch fills

Fill multiple PDFs with the same data:

```python
import os
from pdf_form_filler import fill_pdf_form

data = {"Name": "John Doe", "Date": "2026-01-24"}

for filename in os.listdir("forms/"):
    if filename.endswith(".pdf"):
        fill_pdf_form(
            f"forms/{filename}",
            f"forms_filled/{filename}",
            data
        )
```

## Troubleshooting

### Checkboxes not showing visually

Some PDF viewers don't render checkboxes immediately. The value is set correctly (`/On` or `/Off`), but appearance isn't regenerated. Try opening in:
- Adobe Reader (will render automatically)
- Firefox (has better form support)
- evince or okular on Linux (usually works)

### Field names not found

Use `list_pdf_fields()` to confirm exact field names. PDF forms can be tricky:
- Some use unusual names (e.g., `Field_1` instead of descriptive names)
- Some have nested field structures

### Text appears cut off

Some PDFs have narrow text fields. Either:
1. Use shorter values
2. Reduce font size in the PDF template itself
3. Manual editing after filling

## Bundled Script

See `scripts/fill_pdf_form.py` for the full implementation using pdfrw.
