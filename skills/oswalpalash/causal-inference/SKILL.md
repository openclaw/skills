---
name: causal-inference
description: Add causal reasoning to agent actions. Trigger on ANY high-level action with observable outcomes - emails, messages, calendar changes, file operations, API calls, notifications, reminders, purchases, deployments. Use for planning interventions, debugging failures, predicting outcomes, backfilling historical data for analysis, or answering "what happens if I do X?" Also trigger when reviewing past actions to understand what worked/failed and why.
---

# Causal Inference

A lightweight causal layer for predicting action outcomes, not by pattern-matching correlations, but by modeling interventions and counterfactuals.

## Core Invariant

**Every action must be representable as an explicit intervention on a causal model, with predicted effects + uncertainty + a falsifiable audit trail.**

Plans must be *causally valid*, not just plausible.

## When to Trigger

**Trigger this skill on ANY high-level action**, including but not limited to:

| Domain | Actions to Log |
|--------|---------------|
| **Communication** | Send email, send message, reply, follow-up, notification, mention |
| **Calendar** | Create/move/cancel meeting, set reminder, RSVP |
| **Tasks** | Create/complete/defer task, set priority, assign |
| **Files** | Create/edit/share document, commit code, deploy |
| **Social** | Post, react, comment, share, DM |
| **Purchases** | Order, subscribe, cancel, refund |
| **System** | Config change, permission grant, integration setup |

Also trigger when:
- **Reviewing outcomes** — "Did that email get a reply?" → log outcome, update estimates
- **Debugging failures** — "Why didn't this work?" → trace causal graph
- **Backfilling history** — "Analyze my past emails/calendar" → parse logs, reconstruct actions
- **Planning** — "Should I send now or later?" → query causal model

## Backfill: Bootstrap from Historical Data

Don't start from zero. Parse existing logs to reconstruct past actions + outcomes.

### Email Backfill

```bash
# Extract sent emails with reply status
gog gmail list --sent --after 2024-01-01 --format json > /tmp/sent_emails.json

# For each sent email, check if reply exists
python3 scripts/backfill_email.py /tmp/sent_emails.json
```

### Calendar Backfill

```bash
# Extract past events with attendance
gog calendar list --after 2024-01-01 --format json > /tmp/events.json

# Reconstruct: did meeting happen? was it moved? attendee count?
python3 scripts/backfill_calendar.py /tmp/events.json
```

### Message Backfill (WhatsApp/Discord/Slack)

```bash
# Parse message history for send/reply patterns
wacli search --after 2024-01-01 --from me --format json > /tmp/wa_sent.json
python3 scripts/backfill_messages.py /tmp/wa_sent.json
```

### Generic Backfill Pattern

```python
# For any historical data source:
for record in historical_data:
    action_event = {
        "action": infer_action_type(record),
        "context": extract_context(record),
        "time": record["timestamp"],
        "pre_state": reconstruct_pre_state(record),
        "post_state": extract_post_state(record),
        "outcome": determine_outcome(record),
        "backfilled": True  # Mark as reconstructed
    }
    append_to_log(action_event)
```

## Architecture

### A. Action Log (required)

Every executed action emits a structured event:

```json
{
  "action": "send_followup",
  "domain": "email",
  "context": {"recipient_type": "warm_lead", "prior_touches": 2},
  "time": "2025-01-26T10:00:00Z",
  "pre_state": {"days_since_last_contact": 7},
  "post_state": {"reply_received": true, "reply_delay_hours": 4},
  "outcome": "positive_reply",
  "outcome_observed_at": "2025-01-26T14:00:00Z",
  "backfilled": false
}
```

Store in `memory/causal/action_log.jsonl`.

### B. Causal Graphs (per domain)

Start with 10-30 observable variables per domain.

**Email domain:**
```
send_time → reply_prob
subject_style → open_rate
recipient_type → reply_prob
followup_count → reply_prob (diminishing)
time_since_last → reply_prob
```

**Calendar domain:**
```
meeting_time → attendance_rate
attendee_count → slip_risk
conflict_degree → reschedule_prob
buffer_time → focus_quality
```

**Messaging domain:**
```
response_delay → conversation_continuation
message_length → response_length
time_of_day → response_prob
platform → response_delay
```

**Task domain:**
```
due_date_proximity → completion_prob
priority_level → completion_speed
task_size → deferral_risk
context_switches → error_rate
```

Store graph definitions in `memory/causal/graphs/`.

### C. Estimation

For each "knob" (intervention variable), estimate treatment effects:

```python
# Pseudo: effect of morning vs evening sends
effect = mean(reply_prob | send_time=morning) - mean(reply_prob | send_time=evening)
uncertainty = std_error(effect)
```

Use simple regression or propensity matching first. Graduate to do-calculus when graphs are explicit and identification is needed.

### D. Decision Policy

Before executing actions:

1. Identify intervention variable(s)
2. Query causal model for expected outcome distribution
3. Compute expected utility + uncertainty bounds
4. If uncertainty > threshold OR expected harm > threshold → refuse or escalate to user
5. Log prediction for later validation

## Workflow

### On Every Action

```
BEFORE executing:
1. Log pre_state
2. If enough historical data: query model for expected outcome
3. If high uncertainty or risk: confirm with user

AFTER executing:
1. Log action + context + time
2. Set reminder to check outcome (if not immediate)

WHEN outcome observed:
1. Update action log with post_state + outcome
2. Re-estimate treatment effects if enough new data
```

### Planning an Action

```
1. User request → identify candidate actions
2. For each action:
   a. Map to intervention(s) on causal graph
   b. Predict P(outcome | do(action))
   c. Estimate uncertainty
   d. Compute expected utility
3. Rank by expected utility, filter by safety
4. Execute best action, log prediction
5. Observe outcome, update model
```

### Debugging a Failure

```
1. Identify failed outcome
2. Trace back through causal graph
3. For each upstream node:
   a. Was the value as expected?
   b. Did the causal link hold?
4. Identify broken link(s)
5. Compute minimal intervention set that would have prevented failure
6. Log counterfactual for learning
```

## Quick Start: Bootstrap Today

```bash
# 1. Create the infrastructure
mkdir -p memory/causal/graphs memory/causal/estimates

# 2. Initialize config
cat > memory/causal/config.yaml << 'EOF'
domains:
  - email
  - calendar
  - messaging
  - tasks

thresholds:
  max_uncertainty: 0.3
  min_expected_utility: 0.1

protected_actions:
  - delete_email
  - cancel_meeting
  - send_to_new_contact
  - financial_transaction
EOF

# 3. Backfill one domain (start with email)
python3 scripts/backfill_email.py

# 4. Estimate initial effects
python3 scripts/estimate_effect.py --treatment send_time --outcome reply_received --values morning,evening
```

## Safety Constraints

Define "protected variables" that require explicit user approval:

```yaml
protected:
  - delete_email
  - cancel_meeting
  - send_to_new_contact
  - financial_transaction

thresholds:
  max_uncertainty: 0.3  # don't act if P(outcome) uncertainty > 30%
  min_expected_utility: 0.1  # don't act if expected gain < 10%
```

## Files

- `memory/causal/action_log.jsonl` — all logged actions with outcomes
- `memory/causal/graphs/` — domain-specific causal graph definitions
- `memory/causal/estimates/` — learned treatment effects
- `memory/causal/config.yaml` — safety thresholds and protected variables

## References

- See `references/do-calculus.md` for formal intervention semantics
- See `references/estimation.md` for treatment effect estimation methods
