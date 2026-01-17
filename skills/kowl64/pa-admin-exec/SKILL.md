---
name: core-pa-admin-exec-support
description: Generates exec-support outputs (plan, prioritized tasks, comms drafts, meeting prep/follow-ups). USE WHEN you want a personal assistant to triage requests and produce ready-to-send drafts and schedules.
---

# Core PA Admin and Exec Support

## PURPOSE
Turn pasted messages, calendar availability, task lists, and meeting notes into a clear plan, prioritized tasks, professional-friendly communications drafts, and meeting prep/follow-ups—without ever finalizing actions.

## WHEN TO USE
- You need a daily plan and prioritized tasks from incoming messages and to-dos
- You want email/DM drafts that are friendly but professional
- You need meeting agendas/briefs and action-item extraction from notes
- You want scheduling proposals that respect working hours and constraints
- You want an all-in-one “PA run” that triages, plans, drafts, and follows up

### DO NOT USE WHEN…
- You must send emails or book meetings automatically (this skill only proposes and drafts)
- You have no access to the content (no messages/calendar/tasks/notes available)
- The request is legal/medical/financial advice beyond basic admin coordination

## INPUTS
### REQUIRED (at least one)
- Pasted messages/emails/DMs OR
- A task/backlog list OR
- Calendar availability (free/busy windows) OR
- Meeting notes (raw notes or transcript excerpts)

### OPTIONAL
- Stakeholder list + preferences (tone, titles, signature, response SLAs)
- Priority goals for the day/week
- Known deadlines, travel days, “hard” commitments

### EXAMPLES
- Messages: “Can we meet next week about Q1 planning?” + “Please review the deck by Friday.”
- Calendar: “Mon 10–12 busy; Mon 13–17 free; Tue 08–11 free; Tue 14–16 busy…”
- Tasks: “Finish budget draft (due Wed), follow up vendor invoice, prepare 1:1 agenda”
- Notes: “Decisions: ship v2 on Feb 3. Actions: Alex to update roadmap…”

## OUTPUTS
- A markdown pack containing:
  - Triage summary (what’s urgent, what’s blocked, what needs decisions)
  - Daily plan and/or weekly plan (time-blocked suggestions within constraints)
  - Prioritized task list (with owners, due dates, dependencies)
  - Comms drafts (email/DM) with subject lines and 1–2 variants if helpful
  - Meeting agenda(s), brief(s), and action items
- A JSON block matching the schema in `references/pa-output-json-schema.md`
- Success criteria:
  - All scheduling respects: weekdays only, 08:00–17:00 working hours, latest meeting end 16:30, no meetings Sat/Sun
  - No sending/booking; only drafts and proposals
  - Missing info triggers STOP-and-ASK

## WORKFLOW
1. **Ingest & normalize inputs**
   - Identify which inputs were provided: messages, calendar, tasks, notes.
   - Extract entities: people, orgs, dates, deadlines, meeting requests, deliverables.
   - Convert relative dates (“tomorrow”) into explicit dates *if user provided today’s date*; otherwise flag as missing.

2. **Triage & prioritize**
   - Categorize items into:
     - Urgent/time-sensitive
     - Important (strategic/high impact)
     - Routine/admin
     - Waiting/blocked (needs info or someone else)
   - Assign a priority (P0/P1/P2) using:
     - Deadline proximity
     - Stakeholder seniority/impact
     - Time-to-complete vs value
     - Dependencies and blockers

3. **Plan generation**
   - Build a proposed plan:
     - If calendar availability is provided: place blocks only in free windows.
     - If not provided: propose a plan using default workday blocks 08:00–17:00.
   - Respect scheduling constraints:
     - Meetings only Mon–Fri
     - Work hours 08:00–17:00
     - Latest meeting end 16:30 (do not schedule meetings that end after 16:30)
     - No meetings Sat/Sun
   - Include buffers as assumptions only if user provided or if required; otherwise do not invent.

4. **Comms drafting (friendly but professional)**
   - For each message requiring a response:
     - Draft 1 primary version
     - Draft an optional shorter variant if the message is long/complex
   - Always include:
     - Clear ask/next step
     - Proposed times (if scheduling) as options, not final bookings
     - Polite close and signature placeholder

5. **Meeting support**
   - If meeting requests exist: create:
     - Agenda (purpose, topics, timeboxes, desired outcomes)
     - Brief (context, attendees, decisions needed, pre-reads, risks)
   - If notes exist: extract:
     - Decisions
     - Action items (owner + due date if present)
     - Open questions and follow-ups

6. **Assemble outputs**
   - Produce markdown sections in this order:
     1) Triage summary
     2) Prioritized tasks
     3) Proposed schedule/plan
     4) Draft communications
     5) Meeting agendas/briefs
     6) Action items & follow-ups
   - Output JSON matching schema.

### STOP AND ASK THE USER (MANDATORY) IF…
- No actionable input was provided (no messages/tasks/calendar/notes)
- Any scheduling request lacks at least one of:
  - date range or target week
  - participants/time zones
  - meeting length or purpose
- A message draft requires facts you don’t have (pricing, policy, decision, attachment contents)
- Calendar availability is missing but the user wants specific meeting times
- Conflicting constraints (e.g., only times offered would end after 16:30)

## OUTPUT FORMAT

### MARKDOWN OUTPUT TEMPLATE
```md
## Triage Summary
- Urgent:
- Important:
- Routine:
- Blocked/Waiting:

## Prioritized Tasks (P0/P1/P2)
1. [P0] Task — owner — due — dependency/blocker — next step
2. ...

## Proposed Plan (Mon–Fri, 08:00–17:00; meetings must end by 16:30)
- Today:
  - 08:00–09:00 ...
  - ...
- This Week (if requested):
  - Mon ...
  - Tue ...

## Draft Communications (Friendly, Professional)
### Draft 1: <Recipient/Thread>
**Subject:** ...
**Message:**
...

(Alt short version, if useful)

## Meeting Support
### Agenda: <Meeting Name>
- Purpose:
- Desired outcomes:
- Topics + timeboxes:
- Pre-reads:
- Notes:

### Brief: <Meeting Name>
- Context:
- Attendees:
- Decisions needed:
- Risks/Dependencies:

## Action Items & Follow-ups
- Action: ... | Owner: ... | Due: ... | Status: ...
- Open questions:
