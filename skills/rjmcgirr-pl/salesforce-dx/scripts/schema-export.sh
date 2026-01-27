#!/bin/bash
# schema-export.sh — Export object fields to a readable markdown file
# Usage: ./schema-export.sh <ObjectName> [org-alias]
#
# Examples:
#   ./schema-export.sh Opportunity
#   ./schema-export.sh Account my-sandbox

set -e

OBJECT="${1:?Usage: schema-export.sh <ObjectName> [org-alias]}"
ORG="${2:-}"

ORG_FLAG=""
if [ -n "$ORG" ]; then
  ORG_FLAG="--target-org $ORG"
fi

OUTPUT_FILE="${OBJECT}_schema.md"

echo "# $OBJECT Schema" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "Generated: $(date)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "## Fields" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "| API Name | Label | Type | Required |" >> "$OUTPUT_FILE"
echo "|----------|-------|------|----------|" >> "$OUTPUT_FILE"

sf sobject describe --sobject "$OBJECT" $ORG_FLAG --json 2>/dev/null | \
  jq -r '.result.fields[] | "| \(.name) | \(.label) | \(.type) | \(.nillable | not) |"' >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "## Record Types" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

sf sobject describe --sobject "$OBJECT" $ORG_FLAG --json 2>/dev/null | \
  jq -r '.result.recordTypeInfos[] | "- \(.name) (\(.developerName))"' >> "$OUTPUT_FILE" 2>/dev/null || echo "- (none)" >> "$OUTPUT_FILE"

echo "✓ Exported to $OUTPUT_FILE"
