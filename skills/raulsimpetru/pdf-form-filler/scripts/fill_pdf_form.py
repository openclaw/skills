#!/usr/bin/env python3
"""
PDF Form Filler - Fill PDF form fields programmatically using pdfrw.

Supports text fields and checkboxes with proper appearance states.
"""

from pdfrw import PdfReader, PdfWriter, PdfName
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def list_pdf_fields(pdf_path: str) -> List[Tuple[str, str]]:
    """
    Extract all form field names and types from a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of (field_name, field_type) tuples
        
    Examples:
        >>> fields = list_pdf_fields("form.pdf")
        >>> for name, type_ in fields:
        ...     print(f"{name}: {type_}")
    """
    pdf = PdfReader(pdf_path)
    fields = []
    
    if pdf.Root.AcroForm:
        for page in pdf.pages:
            if page.Annots:
                for annotation in page.Annots:
                    if annotation.Subtype == '/Widget' and annotation.T:
                        field_name = str(annotation.T)[1:-1]  # Remove parentheses
                        
                        # Determine field type
                        field_type = "text"  # default
                        if annotation.AS:  # Appearance state = checkbox/radio
                            field_type = "checkbox" if "Check" in str(annotation.T) else "radio"
                        
                        fields.append((field_name, field_type))
    
    return fields


def fill_pdf_form(
    input_pdf: str,
    output_pdf: str,
    data: Dict[str, any],
    checkboxes: Optional[List[str]] = None
) -> None:
    """
    Fill a PDF form with provided data.
    
    Args:
        input_pdf: Path to the template PDF
        output_pdf: Path to save the filled PDF
        data: Dictionary of {field_name: value} to fill
        checkboxes: List of field names that are checkboxes (auto-detected if None)
        
    Examples:
        >>> fill_pdf_form(
        ...     "form.pdf",
        ...     "form_filled.pdf",
        ...     {
        ...         "Name": "John Doe",
        ...         "Email": "john@example.com",
        ...         "Agree": True
        ...     }
        ... )
    """
    pdf = PdfReader(input_pdf)
    
    if not pdf.Root.AcroForm:
        raise ValueError(f"PDF '{input_pdf}' has no form fields")
    
    # Auto-detect checkboxes if not provided
    if checkboxes is None:
        checkboxes = [name for name, ftype in list_pdf_fields(input_pdf) if ftype == "checkbox"]
    
    filled_count = 0
    
    for page in pdf.pages:
        if page.Annots:
            for annotation in page.Annots:
                if annotation.Subtype == '/Widget' and annotation.T:
                    field_name = str(annotation.T)[1:-1]  # Remove parentheses
                    
                    if field_name in data:
                        value = data[field_name]
                        
                        # Handle checkboxes
                        if field_name in checkboxes:
                            # Convert boolean to /On or /Off
                            if value is True or value == "Yes" or value == "On":
                                annotation.V = PdfName('On')
                                annotation.AS = PdfName('On')
                            else:
                                annotation.V = PdfName('Off')
                                annotation.AS = PdfName('Off')
                        
                        # Handle text fields
                        else:
                            annotation.V = str(value)
                        
                        filled_count += 1
    
    # Save the filled PDF
    PdfWriter().write(output_pdf, pdf)
    print(f"✓ Filled {filled_count} fields in {output_pdf}")


def main():
    """CLI interface for PDF form filling."""
    import sys
    import json
    
    if len(sys.argv) < 4:
        print("Usage: fill_pdf_form.py <input.pdf> <output.pdf> <data.json>")
        print("")
        print("data.json format:")
        print('{"Name": "John Doe", "Email": "john@example.com", "Agree": true}')
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    data_json = sys.argv[3]
    
    # Load data from JSON
    if data_json.startswith('{'):
        # Inline JSON
        data = json.loads(data_json)
    else:
        # File path
        with open(data_json, 'r') as f:
            data = json.load(f)
    
    # Auto-detect checkboxes by looking for boolean values
    checkboxes = [k for k, v in data.items() if isinstance(v, bool)]
    
    fill_pdf_form(input_pdf, output_pdf, data, checkboxes)


if __name__ == '__main__':
    main()
