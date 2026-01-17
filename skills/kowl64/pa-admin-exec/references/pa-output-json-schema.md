# references/pa-output-json-schema.md
# PA Output JSON Schema (Human-readable)
The skill must output one JSON object with these top-level keys:

## meta
- timezone (string) — default "Europe/London"
- generated_at (ISO-8601 string)

## triage (array)
Each item:
- id (string)
- title (string)
- category ("urgent"|"important"|"routine"|"blocked")
- why (string)
- next_step (string)
- due (string|null, ISO date if known)

## tasks (array)
Each item:
- id (string)
- priority ("P0"|"P1"|"P2")
- description (string)
- owner (string|null)
- due (string|null)
- dependencies (array of strings)
- status ("todo"|"waiting"|"done")
- next_step (string)

## schedule_proposals (array)
Each item:
- id (string)
- purpose (string)
- participants (array of strings)
- duration_minutes (integer)
- timezone ("Europe/London" unless user specifies otherwise)
- options (array of objects):
  - start (ISO-8601 local datetime string)
  - end (ISO-8601 local datetime string)
  - rationale (string)

## drafts (array)
Each item:
- id (string)
- channel ("email"|"dm")
- to (array of strings)
- subject (string|null)
- body (string)
- alt_short (string|null)
- open_questions (array of strings)

## meetings (array)
Each item:
- id (string)
- name (string)
- agenda (string|null)
- brief (string|null)

## followups (array)
Each item:
- id (string)
- related_to (string)
- action (string)
- owner (string|null)
- due (string|null)

## assumptions (array of strings)
## questions_for_user (array of strings)

Validation rules:
- Do not fabricate dates/times; if uncertain, put the question in questions_for_user.
- Scheduling must obey: Mon–Fri, within 08:00–17:00, and meeting end <= 16:30.
