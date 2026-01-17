---
name: tachograph-infringement-triage-root-cause-uk
description: Triages tachograph infringements, identifies common patterns, and outputs “what to check next” prompts and weekly review notes. USE WHEN doing weekly tacho/WTD reviews.
---

# Tachograph Triage & Root-Cause Prompts (UK)

## PURPOSE
Run a weekly review workflow that turns infringement outputs into clear triage notes, root-cause prompts, and “what to check next” steps.

## WHEN TO USE
- “Do a weekly tacho and WTD compliance review for these drivers.”
- “Triage these infringements and tell me what to check next.”
- “Summarise this PDF infringement report into actions and driver follow-ups.”

DO NOT USE WHEN…
- You only need a single driver-facing message (use the infringement coach skill).
- You want general rule explanations without records.

## INPUTS
- REQUIRED:
  - Driver list + date range
  - Infringement summaries (CSV/PDF extract or pasted lines)
- OPTIONAL:
  - Any known operational context (routes, delays, multi-drop, ferry/train, staffing)
  - Prior RAG history
- EXAMPLES:
  - “Drivers A–F, last week’s infringement PDF attached; need weekly pack.”

## OUTPUTS
- `weekly-tacho-wtd-review.md` (manager-facing)
- `triage-actions-by-driver.md`
- Success criteria:
  - Clear “next checks” per infringement type
  - Flags where investigation/discipline thresholds may be approaching (per your policy)

## WORKFLOW
1. Confirm period and driver list.
   - IF missing → **STOP AND ASK THE USER**.
2. Normalise infringements into a per-driver list (facts only).
3. Pattern scan using `references/common-infringement-patterns.md`.
4. For each driver, generate:
   - Likely root-cause prompts (questions to ask, operational checks)
   - “What to check next” steps using `assets/what-to-check-next-playbook.md`
5. Produce weekly pack using `assets/weekly-review-pack-template.md`.
6. If RAG escalation depends on missing history → **STOP AND ASK THE USER** for counts/outcomes.

## OUTPUT FORMAT
```text
# triage-actions-by-driver.md
Period:
Sources:

## Driver [X]
Infringements (facts):
- …

What to check next:
- …

Root-cause prompts:
- …

Proposed follow-up:
- Coaching / monitoring / investigation trigger (per policy)
```

## SAFETY & EDGE CASES
- If records appear incomplete (missing days, download gaps), flag as a risk/gap rather than guessing why.
- Avoid blame language; keep triage neutral.

## EXAMPLES
- Input: “Weekly review for 12 drivers”
  - Output: weekly pack + per-driver triage actions and check-next prompts
