# GNO Usage Examples

Real-world examples for common tasks.

## Getting Started

### Index a folder of docs

```bash
# Initialize
gno init

# Add your docs folder
gno collection add ~/Documents/work --name work

# Build index
gno index
```

### Index multiple folders

```bash
gno init
gno collection add ~/notes --name notes --pattern "**/*.md"
gno collection add ~/work/contracts --name contracts --pattern "**/*.{pdf,docx}"
gno index
```

## Searching

### Find by keywords

```bash
# Simple search
gno search "quarterly report"

# More results
gno search "budget" -n 20

# Filter to collection
gno search "NDA" -c contracts
```

### Find by meaning (semantic)

```bash
# Semantic search finds related concepts
gno vsearch "how to cancel subscription"

# Even if docs say "terminate agreement"
gno vsearch "end contract early"
```

### Best quality search

```bash
# Hybrid combines keywords + semantics + reranking
gno query "deployment process"

# See how results were found
gno query "deployment" --explain
```

## Getting Answers

### Q&A with citations

```bash
# Just retrieve relevant chunks
gno ask "what are the payment terms"

# Get an AI-generated answer
gno ask "what are the payment terms" --answer
```

### Scoped answers

```bash
# Search only contracts
gno ask "termination clause" -c contracts --answer

# Limit answer length
gno ask "summarize project goals" --answer --max-answer-tokens 200
```

## Reading Documents

### Get full document

```bash
# By URI
gno get gno://work/readme.md

# By document ID
gno get "#a1b2c3d4"

# With line numbers
gno get gno://notes/meeting.md --line-numbers
```

### Get specific lines

```bash
# Start at line 50
gno get gno://work/report.md --from 50

# Get 20 lines starting at 100
gno get gno://work/report.md --from 100 -l 20
```

### List documents

```bash
# All documents
gno ls

# In a collection
gno ls work

# As JSON
gno ls --json
```

## Search & Retrieve Full Content

### Pipeline: Search then get

```bash
# Find documents, get full content of top result
gno search "api design" --files | head -1 | cut -d, -f3 | xargs gno get

# JSON pipeline - get first result's full content
gno query "auth" --json | jq -r '.results[0].uri' | xargs gno get

# Get multiple results
gno search "error handling" --json | jq -r '.results[].uri' | xargs gno multi-get
```

## JSON Output (Scripting)

### Search results to JSON

```bash
# Get URIs of matches
gno search "api endpoint" --json | jq '.[] | .uri'

# Get snippets
gno search "config" --json | jq '.[] | {uri, snippet}'
```

### Check index health

```bash
# Get stats
gno status --json | jq '{docs: .totalDocuments, chunks: .totalChunks}'

# Run diagnostics
gno doctor --json
```

### Batch processing

```bash
# Export all document IDs
gno ls --json | jq -r '.[].docid' > doc-ids.txt

# Search and process results
gno search "error" --json | jq -r '.[] | .uri' | while read uri; do
  echo "Processing: $uri"
  gno get "$uri" > "output/$(basename $uri)"
done
```

## Maintenance

### Update index after changes

```bash
# Sync files from disk
gno update

# Full re-index
gno index
```

### Git integration

```bash
# Pull and re-index
gno index --git-pull

# Useful for docs repos
gno update --git-pull
```

### Model management

```bash
# List models and status
gno models list

# Switch to quality preset
gno models use quality

# Download models
gno models pull
```

## Note Linking

### View outgoing links

```bash
# List all links from a document
gno links gno://notes/readme.md

# Filter by type
gno links gno://notes/readme.md --type wiki
gno links gno://notes/readme.md --type markdown

# Show only broken links
gno links gno://notes/readme.md --broken
```

### Find backlinks

```bash
# Find all documents linking TO this one
gno backlinks gno://notes/api-design.md

# More results
gno backlinks gno://notes/api-design.md -n 50
```

### Find related notes

```bash
# Find semantically similar documents
gno similar gno://notes/auth.md

# Stricter threshold (default: 0.7)
gno similar gno://notes/auth.md --threshold 0.85

# Search across all collections
gno similar gno://notes/auth.md --cross-collection
```

### Wiki link syntax

```markdown
# In your documents:
See [[API Design]] for details.
Check [[work:Project Plan]] for cross-collection link.
Read [[Security#OAuth]] for specific section.
```

## Tagging

### List and manage tags

```bash
# List all tags with counts
gno tags

# Filter by collection
gno tags -c work

# Filter by prefix (hierarchical)
gno tags --prefix project/
```

### Add/remove tags

```bash
# Add tag to document
gno tags add gno://work/readme.md project/api

# Remove tag
gno tags rm gno://work/readme.md draft

# Tags in frontmatter are extracted automatically
cat myfile.md
# ---
# tags: [project/web, status/review]
# ---
```

### Filter search by tags

```bash
# Find docs with ANY of these tags (OR)
gno search "api" --tags-any project,work

# Find docs with ALL of these tags (AND)
gno query "auth" --tags-all security,reviewed

# Combine with other filters
gno ask "deployment steps" -c work --tags-any devops --answer
```

## Tips

### Search Modes

| Command                | Time    | Use When                     |
| ---------------------- | ------- | ---------------------------- |
| `gno search`           | instant | Exact keyword matching       |
| `gno vsearch`          | ~0.5s   | Finding similar concepts     |
| `gno query --fast`     | ~0.7s   | Quick lookups                |
| `gno query`            | ~2-3s   | Default, balanced            |
| `gno query --thorough` | ~5-8s   | Best recall, complex queries |

**Agent retry strategy**: Use default mode first. If no results:

1. Rephrase the query (free, often helps)
2. Try `--thorough` for better recall

### Output formats

```bash
# Human readable (default)
gno search "query"

# JSON (scripting)
gno search "query" --json

# File list (for piping)
gno search "query" --files

# CSV (spreadsheets)
gno search "query" --csv

# Markdown (docs)
gno search "query" --md
```

### Large result sets

```bash
# Increase limit
gno search "common term" -n 50

# Filter by score
gno search "common term" --min-score 0.7

# Get full content
gno search "term" --full
```
