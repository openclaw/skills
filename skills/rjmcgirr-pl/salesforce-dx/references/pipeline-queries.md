# Pipeline & Forecast Queries

Ready-to-use queries for pipeline management. Copy and modify for your org.

## Pipeline Overview

### Current Open Pipeline
```sql
SELECT StageName, COUNT(Id) count, SUM(Amount) total 
FROM Opportunity 
WHERE IsClosed = false 
GROUP BY StageName 
ORDER BY StageName
```

### Pipeline by Owner
```sql
SELECT Owner.Name, COUNT(Id) deals, SUM(Amount) total 
FROM Opportunity 
WHERE IsClosed = false 
GROUP BY Owner.Name 
ORDER BY SUM(Amount) DESC
```

### Pipeline by Account
```sql
SELECT Account.Name, COUNT(Id) deals, SUM(Amount) total 
FROM Opportunity 
WHERE IsClosed = false 
GROUP BY Account.Name 
ORDER BY SUM(Amount) DESC 
LIMIT 20
```

## Forecast Views

### This Quarter Forecast
```sql
SELECT StageName, SUM(Amount) total, SUM(ExpectedRevenue) weighted 
FROM Opportunity 
WHERE CloseDate = THIS_QUARTER AND IsClosed = false 
GROUP BY StageName
```

### Monthly Forecast (This Year)
```sql
SELECT CALENDAR_MONTH(CloseDate) month, SUM(Amount) total 
FROM Opportunity 
WHERE CloseDate = THIS_YEAR AND IsClosed = false 
GROUP BY CALENDAR_MONTH(CloseDate) 
ORDER BY CALENDAR_MONTH(CloseDate)
```

### Commit vs Best Case
```sql
-- Requires ForecastCategory field
SELECT ForecastCategory, SUM(Amount) total 
FROM Opportunity 
WHERE CloseDate = THIS_QUARTER AND IsClosed = false 
GROUP BY ForecastCategory
```

## Win/Loss Analysis

### Win Rate by Quarter
```sql
SELECT CALENDAR_QUARTER(CloseDate) qtr,
  SUM(CASE WHEN IsWon = true THEN 1 ELSE 0 END) wins,
  SUM(CASE WHEN IsWon = false THEN 1 ELSE 0 END) losses
FROM Opportunity 
WHERE IsClosed = true AND CloseDate = THIS_YEAR 
GROUP BY CALENDAR_QUARTER(CloseDate)
```

Note: CASE not supported in SOQL. Alternative approach:
```sql
-- Wins
SELECT CALENDAR_QUARTER(CloseDate) qtr, COUNT(Id) wins 
FROM Opportunity 
WHERE IsWon = true AND CloseDate = THIS_YEAR 
GROUP BY CALENDAR_QUARTER(CloseDate)

-- Losses
SELECT CALENDAR_QUARTER(CloseDate) qtr, COUNT(Id) losses 
FROM Opportunity 
WHERE IsWon = false AND IsClosed = true AND CloseDate = THIS_YEAR 
GROUP BY CALENDAR_QUARTER(CloseDate)
```

### Average Deal Size
```sql
SELECT StageName, AVG(Amount) avg_deal, COUNT(Id) count 
FROM Opportunity 
WHERE IsWon = true AND CloseDate = THIS_YEAR 
GROUP BY StageName
```

### Sales Cycle Length
```sql
SELECT Id, Name, Amount, CreatedDate, CloseDate 
FROM Opportunity 
WHERE IsWon = true AND CloseDate = THIS_YEAR 
ORDER BY CloseDate DESC
```
Calculate days between CreatedDate and CloseDate in your analysis tool.

## Pipeline Health

### Stale Opportunities (No Activity 30+ Days)
```sql
SELECT Id, Name, StageName, Amount, LastActivityDate, Owner.Name 
FROM Opportunity 
WHERE IsClosed = false AND LastActivityDate < LAST_N_DAYS:30 
ORDER BY Amount DESC
```

### Overdue Close Dates
```sql
SELECT Id, Name, StageName, Amount, CloseDate, Owner.Name 
FROM Opportunity 
WHERE IsClosed = false AND CloseDate < TODAY 
ORDER BY CloseDate
```

### Deals Without Next Steps
```sql
SELECT Id, Name, Amount, StageName 
FROM Opportunity 
WHERE IsClosed = false AND NextStep = null 
ORDER BY Amount DESC
```

### Large Deals at Risk
```sql
SELECT Id, Name, Amount, StageName, LastActivityDate 
FROM Opportunity 
WHERE IsClosed = false 
  AND Amount > 100000 
  AND LastActivityDate < LAST_N_DAYS:14 
ORDER BY Amount DESC
```

## Conversion Tracking

### Lead Source Performance
```sql
SELECT LeadSource, COUNT(Id) total, SUM(Amount) pipeline 
FROM Opportunity 
WHERE IsClosed = false 
GROUP BY LeadSource 
ORDER BY SUM(Amount) DESC
```

### Campaign ROI
```sql
SELECT Campaign.Name, COUNT(Id) opps, SUM(Amount) pipeline 
FROM Opportunity 
WHERE CampaignId != null 
GROUP BY Campaign.Name 
ORDER BY SUM(Amount) DESC
```

## Historical Comparisons

### QoQ Closed Won
```sql
-- This quarter
SELECT SUM(Amount) FROM Opportunity WHERE IsWon = true AND CloseDate = THIS_QUARTER

-- Last quarter  
SELECT SUM(Amount) FROM Opportunity WHERE IsWon = true AND CloseDate = LAST_QUARTER
```

### YoY Growth
```sql
-- This year
SELECT SUM(Amount) FROM Opportunity WHERE IsWon = true AND CloseDate = THIS_YEAR

-- Last year
SELECT SUM(Amount) FROM Opportunity WHERE IsWon = true AND CloseDate = LAST_YEAR
```

## Team Performance

### Leaderboard (Closed Won This Quarter)
```sql
SELECT Owner.Name, COUNT(Id) deals, SUM(Amount) total 
FROM Opportunity 
WHERE IsWon = true AND CloseDate = THIS_QUARTER 
GROUP BY Owner.Name 
ORDER BY SUM(Amount) DESC
```

### Activity by Rep
```sql
SELECT Owner.Name, COUNT(Id) tasks 
FROM Task 
WHERE CreatedDate = THIS_MONTH 
GROUP BY Owner.Name 
ORDER BY COUNT(Id) DESC
```

## Export Templates

### Full Pipeline Export
```sql
SELECT Id, Name, Account.Name, StageName, Amount, ExpectedRevenue, 
  CloseDate, Probability, LeadSource, Owner.Name, CreatedDate, 
  LastActivityDate, NextStep, Description 
FROM Opportunity 
WHERE IsClosed = false 
ORDER BY Amount DESC
```

### Closed Won Export
```sql
SELECT Id, Name, Account.Name, Amount, CloseDate, LeadSource, 
  Owner.Name, CreatedDate 
FROM Opportunity 
WHERE IsWon = true AND CloseDate = THIS_YEAR 
ORDER BY CloseDate DESC
```
