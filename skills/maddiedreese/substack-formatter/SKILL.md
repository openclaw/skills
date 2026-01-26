---
name: substack-formatter
description: Transform plain text into Substack article format with proper HTML formatting for copy-paste into Substack editor.
---

# Substack Article Formatter

## Summary
Transform plain text into professional Substack format. Handles the technical formatting to ensure bold/italic/headers work correctly when pasted into Substack editor.

## What This Skill Does
- ✅ **Formats text for Substack** with proper structure and spacing
- ✅ **Converts to HTML format** that Substack editor recognizes
- ✅ **Preserves your content** - only changes visual presentation
- ✅ **Ensures copy-paste works** with bold, italic, headers, bullets preserved

## Technical Solution
**Problem:** Substack editor treats raw markdown as plain text  
**Solution:** Convert to HTML and copy as `text/html` format

## Usage

### Basic Formatting
```
Format this for Substack:
[Your plain text content here]
```

### With Minimal Formatting
```
Format for Substack (minimal):
[Your plain text content here]
```

## Formatting Options

### **Standard Format**
- Proper paragraph structure
- Clean HTML output
- Preserved content with better readability

### **Minimal Format**  
- Pure spacing improvements
- No emphasis changes
- Exact content preservation

## Formatting Features

### **Structure**
- **Clean paragraphs** for better readability
- **Proper spacing** between sections
- **Clear visual hierarchy**

### **HTML Output**
- **Bold text:** `<strong>` tags
- **Emphasis:** `<em>` tags  
- **Headers:** `<h2>`, `<h3>` for sections
- **Lists:** `<ul><li>` for bullets, `<ol><li>` for numbered
- **Paragraphs:** Proper `<p>` tag structure

## Copy-Paste Process

1. **Run formatter** → Get HTML output
2. **Use included copy script** → Copies as `text/html` format  
3. **Paste into Substack** → Formatting preserved perfectly
4. **No manual formatting needed** → Bold/italic/headers work automatically

## Examples

### Input (Plain Text):
```
I used to think being productive meant doing more things. Last week I tried something different. I did fewer things but focused completely on each one. The result was surprising. I got more done in less time and felt less stressed. Sometimes the answer isn't addition, it's subtraction.
```

### Output (Formatted for Substack):
```html
<p><strong>I used to think being productive meant doing more things.</strong></p>

<p>Last week I tried something different:</p>

<p>I did fewer things.<br>
But focused completely on each one.</p>

<p>The result was surprising.</p>

<p><em>I got more done in less time and felt less stressed.</em></p>

<p><strong>Sometimes the answer isn't addition, it's subtraction.</strong></p>

<p>What's one thing you could subtract from your routine?</p>
```

## Tools Included

- **`formatter.py`** - Main formatting script
- **`copy_to_substack.py`** - Converts to HTML and copies correctly  
- **`test_formatter.py`** - Test with examples
- **Examples and templates** for each structure type

## Philosophy
**Format for readability, preserve your voice.** This tool improves visual presentation while keeping your message and personality intact.