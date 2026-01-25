# Pre-Mortem Examples - Artem's World

## Example 1: GolfTab Launch at First Course

### Scenario
"It's 4 months from now. GolfTab launched at our first golf course and it's been a disaster. The course is threatening to cancel. What happened?"

### Why It Failed

👥 **PEOPLE:**
• **Kitchen staff refused to use it** - H/H
  Prevention: Staff training BEFORE launch, champion in kitchen
  Warning sign: Kitchen complaints in week 1

• **Pro shop wasn't bought in** - M/H
  Prevention: Include in planning, show their benefits
  Warning sign: Not promoting to golfers

⚙️ **PROCESS:**
• **Orders got lost during busy periods** - H/H
  Prevention: Load testing, backup paper system
  Warning sign: More than 3 lost orders in first week

• **Delivery timing was unreliable** - M/H
  Prevention: GPS integration, buffer times built in
  Warning sign: Complaints about cold food

💻 **TECHNOLOGY:**
• **WiFi dead zones on back 9** - H/H
  Prevention: WiFi survey before launch, offline mode
  Warning sign: Failed orders from holes 10-18

• **App crashed on busy Saturday** - M/H
  Prevention: Stress testing, auto-scaling
  Warning sign: Slow response times under load

🌍 **EXTERNAL:**
• **Weather kept golfers away** - L/M
  Prevention: Nothing (accept risk), launch in good season
  Warning sign: N/A - external

### Top 3 Priorities
1. WiFi coverage survey and offline mode - DO BEFORE LAUNCH
2. Kitchen staff training and champion - DO BEFORE LAUNCH
3. Load testing at 2x expected volume - DO BEFORE LAUNCH

### Monitoring Dashboard
□ Daily: Lost orders count (threshold: 0)
□ Daily: Average delivery time (threshold: <15 min)
□ Weekly: Staff satisfaction pulse (threshold: >7/10)
□ Weekly: Customer complaints (threshold: <5)

---

## Example 2: TISA Eindhoven Year 1

### Scenario
"It's September 2026. TISA Eindhoven opened but only has 15 students instead of target 50. We're burning cash. What happened?"

### Why It Failed

👥 **PEOPLE:**
• **Couldn't find qualified bilingual teachers** - H/H
  Prevention: Start recruiting 12 months early, consider transfers
  Warning sign: <3 candidates per position by month -6

• **Artem too stretched, Leiden suffered** - H/H
  Prevention: Hire Eindhoven director FIRST, full delegation
  Warning sign: Leiden KPIs declining

• **Local director wasn't the right fit** - M/H
  Prevention: 3-month probation, clear success metrics
  Warning sign: Enrollment conversations not converting

⚙️ **PROCESS:**
• **Marketing started too late** - H/H
  Prevention: 12-month marketing runway, build waitlist early
  Warning sign: <30 inquiries by month -6

• **Enrollment process was confusing** - M/M
  Prevention: Mystery shop own process, simplify ruthlessly
  Warning sign: Abandoned applications >20%

• **No local partnerships secured** - H/M
  Prevention: ASML/tech company MOUs before announcing
  Warning sign: No corporate interest by month -9

💻 **TECHNOLOGY:**
• **Systems not ready for remote management** - M/M
  Prevention: Leiden → Eindhoven remote workflow tested
  Warning sign: Communication gaps emerging

🌍 **EXTERNAL:**
• **Competitor opened same year** - M/H
  Prevention: Competitive intel, differentiation clarity
  Warning sign: Same families touring competitor

• **Regulatory delays** - H/H
  Prevention: Submit permits 18 months early, buffer timeline
  Warning sign: Permit status not "approved" by month -6

### Top 3 Priorities
1. Start teacher recruitment NOW (12+ months lead time)
2. Hire Eindhoven director as first key hire
3. Submit regulatory applications immediately

### Monitoring Dashboard
□ Monthly: Inquiries received (target: 10+/month)
□ Monthly: Teacher candidates in pipeline (target: 3+/position)
□ Quarterly: Permit status (must be "approved" 6 months before)
□ Monthly: Artem time on Eindhoven vs Leiden (<30% Eindhoven)

---

## Example 3: TeddySnaps Premium Launch

### Scenario
"It's 6 months after launching TeddySnaps Premium. Only 5% of parents subscribed, and there's negative chatter in parent WhatsApp groups. What happened?"

### Why It Failed

👥 **PEOPLE:**
• **Staff treated premium kids differently** - H/H
  Prevention: Training + policy: photo quantity equal for all
  Warning sign: Parent complaints about inequality

• **Parents felt judged for not subscribing** - M/H
  Prevention: Frame as "extra" not "premium", no visible tiers
  Warning sign: Social media/WhatsApp sentiment

⚙️ **PROCESS:**
• **Free tier became too limited** - H/H
  Prevention: Free tier must still feel valuable
  Warning sign: Free user satisfaction dropping

• **Price point wrong** - M/H
  Prevention: Survey parents, test pricing before launch
  Warning sign: Trial → paid conversion below 20%

💻 **TECHNOLOGY:**
• **Premium features had bugs** - M/M
  Prevention: Extended beta with 10 families
  Warning sign: Bug reports from premium users

🌍 **EXTERNAL:**
• **Competitor launched free alternative** - M/M
  Prevention: Moat = face recognition + integration with TeddyKids
  Warning sign: Parents mentioning competitor

### Top 3 Priorities
1. Parent survey on pricing before launch
2. Clear policy: Photo opportunities equal for all children
3. Beta test with 10 families for 30 days

---

## Quick Pre-Mortem Template

```
PROJECT: [Name]
SCENARIO: "It's [date]. [Project] has failed. [Specific failure description]."

WHY IT FAILED:

👥 PEOPLE:
• 
• 

⚙️ PROCESS:
• 
• 

💻 TECHNOLOGY:
• 

🌍 EXTERNAL:
• 

TOP 3 ACTIONS:
1. 
2. 
3. 

WARNING SIGNS TO MONITOR:
□ 
□ 
□ 
```
