#!/bin/bash
# format-for-x.sh - Convert markdown to X Articles format
# 
# X Articles uses Draft.js which has specific quirks:
# - Each line break = new paragraph with spacing
# - Sentences in same paragraph must be on ONE line
# - Plain text, not markdown
# - No em dashes

set -e

INPUT="$1"
OUTPUT="${2:-${INPUT%.md}-x-ready.txt}"

if [ -z "$INPUT" ]; then
  echo "Usage: format-for-x.sh <input.md> [output.txt]"
  echo ""
  echo "Converts markdown to X Articles format:"
  echo "  - Removes markdown formatting"
  echo "  - Joins sentences in paragraphs to single lines"
  echo "  - Removes em dashes"
  echo "  - Preserves paragraph breaks"
  exit 1
fi

if [ ! -f "$INPUT" ]; then
  echo "Error: File not found: $INPUT"
  exit 1
fi

# Process the file
cat "$INPUT" | \
  # Remove markdown headers but keep the text
  sed 's/^### \(.*\)/\n\1\n/g' | \
  sed 's/^## \(.*\)/\n\1\n/g' | \
  sed 's/^# \(.*\)/\n\1\n/g' | \
  # Remove markdown bold/italic markers
  sed 's/\*\*\([^*]*\)\*\*/\1/g' | \
  sed 's/\*\([^*]*\)\*/\1/g' | \
  sed 's/__\([^_]*\)__/\1/g' | \
  sed 's/_\([^_]*\)_/\1/g' | \
  # Remove markdown links, keep text
  sed 's/\[\([^]]*\)\]([^)]*)/\1/g' | \
  # Remove markdown code blocks (keep content)
  sed 's/^```[a-z]*$/\n/g' | \
  sed 's/^```$/\n/g' | \
  # Remove inline code markers
  sed 's/`\([^`]*\)`/\1/g' | \
  # Replace em dashes with colons or periods
  sed 's/ — /: /g' | \
  sed 's/—/: /g' | \
  # Replace en dashes with hyphens
  sed 's/–/-/g' | \
  # Remove bullet points but keep content
  sed 's/^- /• /g' | \
  sed 's/^  - /  • /g' | \
  # Join lines within paragraphs
  # Blank lines are preserved as paragraph separators
  awk '
    BEGIN { paragraph = "" }
    /^$/ { 
      if (paragraph != "") {
        print paragraph
        print ""
        paragraph = ""
      }
    }
    /^./ {
      if (paragraph == "") {
        paragraph = $0
      } else {
        paragraph = paragraph " " $0
      }
    }
    END {
      if (paragraph != "") {
        print paragraph
      }
    }
  ' | \
  # Clean up multiple blank lines
  cat -s \
  > "$OUTPUT"

# Count stats
ORIGINAL_LINES=$(wc -l < "$INPUT" | tr -d ' ')
OUTPUT_LINES=$(wc -l < "$OUTPUT" | tr -d ' ')
WORD_COUNT=$(wc -w < "$OUTPUT" | tr -d ' ')

echo "✓ Created: $OUTPUT"
echo "  Original: $ORIGINAL_LINES lines"
echo "  Output: $OUTPUT_LINES lines"
echo "  Words: $WORD_COUNT"
