---
name: data-reconciliation-exceptions
description: Reconciles data sources using stable identifiers (Pay Number, driving licence, driver card, and driver qualification card numbers), producing exception reports and “no silent failure” checks. Use when you need weekly matching with explicit reasons for non-joins and mismatches.
---

# Data quality & reconciliation with exception reporting and no silent failure

## PURPOSE
Reconciles data sources using stable identifiers (Pay Number, driving licence, driver card, and driver qualification card numbers), producing exception reports and “no silent failure” checks.

## WHEN TO USE
- TRIGGERS:
  - Reconcile these two data sources and produce an exceptions report with reasons.
  - Match names and payroll numbers across files and flag anything that does not join.
  - Build a ‘no silent failure’ check that stops the pipeline if counts do not match.
  - Create a weekly variance report for missing records, duplicates, and date gaps.
  - Design a data quality scorecard with thresholds and red flags.
- DO NOT USE WHEN…
  - You need open-ended fuzzy matching without acceptance criteria.
  - There are no stable identifiers in any source.

## INPUTS
- REQUIRED:
  - At least two datasets (CSV/XLSX) with Pay Number and/or driver document numbers.
  - Which fields must match (e.g., Name, expiry date).
- OPTIONAL:
  - Normalization rules (case, spaces, punctuation).
  - Thresholds for gates/scorecard (max % missing, etc.).
- EXAMPLES:
  - Payroll export + compliance register
  - Two weekly exports from different systems

## OUTPUTS
- Reconciliation plan (matching rules, normalization, join strategy).
- Exceptions report spec (CSV columns + reason codes) and variance checks.
- Optional artifacts: `assets/exceptions-report-template.csv` + `references/matching-rules.md`.
Success = every record is categorized (matched/missing/duplicate/mismatch/invalid) with an explicit reason; pipelines stop on anomalies.


## WORKFLOW
1. Confirm sources and key priority (Pay Number → Driver Card → Driving Licence → DQC).
2. Normalize columns:
   - trim spaces; standardize case; strip common punctuation for document numbers.
3. Validate keys:
   - flag blanks/invalid formats; identify duplicates per source.
4. Join:
   - exact join on Pay Number; then attempt secondary joins only for remaining unmatched items.
5. Produce exception categories with reasons:
   - Missing in A/B, Duplicate key, Field mismatch, Invalid key.
6. “No silent failure” gates:
   - counts within tolerance; unmatched rate below threshold; duplicate spikes flagged.
7. STOP AND ASK THE USER if:
   - columns are not mapped,
   - multiple competing IDs exist with no priority,
   - expected tolerances are unspecified.


## OUTPUT FORMAT
```csv
exception_type,reason,source_a_id,source_b_id,pay_number,name,field,source_a_value,source_b_value
```

Reason codes: `MISSING_IN_A`, `MISSING_IN_B`, `MISMATCH`, `DUPLICATE_KEY`, `INVALID_KEY`.


## SAFETY & EDGE CASES
- Read-only by default; don’t auto-edit source data. Route exceptions to review.
- Deterministic matching rules first; avoid fuzzy matching unless explicitly requested.
- Always produce an exceptions report; never drop unmatched rows.


## EXAMPLES
- Input: “Payroll vs compliance; match by Pay Number; flag name mismatch.”  
  Output: join plan + mismatch reasons + exceptions report schema.

- Input: “Some rows have blank Pay Number.”  
  Output: secondary key matching + invalid-key exceptions for truly unmatchable rows.

