---
name: research-company
description: B2B company research producing professional PDF reports. Use when asked to research a company, analyze a business, create an account profile, or generate market intelligence from a company URL. Outputs a beautifully formatted, downloadable PDF report.
---

# Company Research

Generate comprehensive Account Research Reports as professionally styled PDFs from a company URL.

## Workflow

1. **Research** the company (web fetch + searches)
2. **Build** JSON data structure
3. **Generate** PDF via `scripts/generate_report.py`
4. **Deliver** PDF to user

## Phase 1: Research (Parallel)

Execute these searches concurrently to minimize context usage:

```
WebFetch: [company URL]
WebSearch: "[company name] funding news 2024"
WebSearch: "[company name] competitors market"
WebSearch: "[company name] CEO founder leadership"
```

Extract from website: company name, industry, HQ, founded, leadership, products/services, pricing model, target customers, case studies, testimonials, recent news.

## Phase 2: Build Data Structure

Create JSON matching this schema (see `references/data-schema.md` for full spec):

```json
{
  "company_name": "...",
  "source_url": "...",
  "report_date": "January 20, 2026",
  "executive_summary": "3-5 sentences...",
  "profile": { "name": "...", "industry": "...", ... },
  "products": { "offerings": [...], "differentiators": [...] },
  "target_market": { "segments": "...", "verticals": [...] },
  "use_cases": [{ "title": "...", "description": "..." }],
  "competitors": [{ "name": "...", "strengths": "...", "differentiation": "..." }],
  "industry": { "trends": [...], "opportunities": [...], "challenges": [...] },
  "developments": [{ "date": "...", "title": "...", "description": "..." }],
  "lead_gen": { "keywords": {...}, "outreach_angles": [...] },
  "info_gaps": ["..."]
}
```

## Phase 3: Generate PDF

```bash
# Install if needed
pip install reportlab

# Save JSON to temp file
cat > /tmp/research_data.json << 'EOF'
{...your JSON data...}
EOF

# Generate PDF
python3 scripts/generate_report.py /tmp/research_data.json /path/to/output/report.pdf
```

## Phase 4: Deliver

Save PDF to workspace folder and provide download link:
```
[Download Company Research Report](computer:///sessions/.../report.pdf)
```

## Quality Standards

- **Accuracy**: Base claims on observable evidence; cite sources
- **Specificity**: Include product names, metrics, customer examples
- **Completeness**: Note gaps as "Not publicly available"
- **No fabrication**: Never invent information

## Resources

- `scripts/generate_report.py` - PDF generator (uses reportlab)
- `references/data-schema.md` - Full JSON schema with examples
