# Pre-Mortem Framework - Detailed Methodology

## The Psychology Behind Pre-Mortems

### Why Pre-Mortems Work

1. **Prospective Hindsight**: Imagining future failure as certain activates different thinking
2. **Permission to Criticize**: "The project failed" removes social pressure to be positive
3. **Specificity Forcing**: Must generate concrete causes, not vague concerns
4. **Ownership Distribution**: Everyone can contribute without being "negative"

Research by Gary Klein shows pre-mortems improve outcome prediction by 30%.

## The Facilitation Process

### For Solo Use (With Claude)
1. State project clearly
2. Set specific failure date and scenario
3. Generate at least 10 causes
4. Rate and prioritize
5. Create action plans

### For Team Use
1. Explain pre-mortem concept (2 min)
2. Set scenario: "It's [date]. This has failed catastrophically."
3. Silent brainstorm - everyone writes (5 min)
4. Round-robin sharing - no discussion yet (10 min)
5. Categorize on whiteboard (5 min)
6. Dot-vote on severity (3 min)
7. Discuss top items and actions (15 min)

## Failure Cause Templates

### The 10 Universal Failure Modes

1. **Scope Creep** - We tried to do too much
2. **Resource Shortage** - We ran out of time/money/people
3. **Key Person Dependency** - Critical person left/unavailable
4. **Communication Breakdown** - Teams/stakeholders misaligned
5. **Technical Debt** - Shortcuts caught up with us
6. **Market Misread** - Customers didn't want this
7. **Competitor Move** - Someone else got there first/better
8. **Integration Failure** - Pieces didn't fit together
9. **Stakeholder Resistance** - Key people blocked progress
10. **External Shock** - Something outside our control happened

### Industry-Specific Additions

**For Childcare/Education:**
- Regulatory compliance issue
- Parent trust incident
- Staff turnover at critical moment
- Enrollment below projections

**For Technology Products:**
- Scaling failure at launch
- Security/privacy breach
- User adoption below threshold
- API/integration dependency fails

**For Sales/Expansion:**
- Decision maker changed
- Budget cycle misalignment
- Competitor undercutting
- Implementation complexity underestimated

## The Warning Signs System

For each failure cause, identify:

### Leading Indicators (Early Warning)
Signals that appear BEFORE failure becomes visible
- Example: "Engineers expressing frustration in standups" → Technical debt risk

### Lagging Indicators (Confirmation)
Signals that confirm failure is happening
- Example: "Bug reports increasing weekly" → Technical debt materializing

### Threshold Triggers
Specific numbers that trigger action
- Example: "More than 5 P1 bugs in a week → Emergency technical review"

## Prevention Hierarchy

### Level 1: Eliminate
Remove the failure mode entirely
"We won't build feature X, eliminating complexity risk"

### Level 2: Substitute
Replace risky element with safer alternative
"Use proven vendor instead of building custom"

### Level 3: Engineering Controls
Build systems to prevent failure
"Automated testing catches bugs before release"

### Level 4: Administrative Controls
Processes and reviews to catch issues
"Weekly risk review meetings"

### Level 5: Response Planning
Plans for when failure happens anyway
"Rollback procedure documented and tested"

## Integration with Other Skills

- **Inversion**: Pre-mortem IS applied inversion for projects
- **Second-Order**: Consider downstream effects of each failure mode
- **First Principles**: Ensure project foundation is solid before pre-mortem
- **Six Hats**: Black hat thinking IS pre-mortem mode

## Post-Project Retroactive Analysis

After project completes, compare:
- What failure modes did we predict?
- What actually went wrong?
- What did we miss?
- How can we improve future pre-mortems?

This feedback loop improves prediction accuracy over time.
