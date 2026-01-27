# Advanced SOQL Patterns

## Semi-Joins and Anti-Joins

```sql
-- Accounts WITH opportunities (semi-join)
SELECT Id, Name FROM Account 
WHERE Id IN (SELECT AccountId FROM Opportunity WHERE Amount > 100000)

-- Accounts WITHOUT opportunities (anti-join)
SELECT Id, Name FROM Account 
WHERE Id NOT IN (SELECT AccountId FROM Opportunity)

-- Contacts with open cases
SELECT Id, Name FROM Contact 
WHERE Id IN (SELECT ContactId FROM Case WHERE IsClosed = false)
```

## Polymorphic Relationships (Who/What)

```sql
-- Tasks with polymorphic WhatId
SELECT Id, Subject, What.Type, What.Name 
FROM Task 
WHERE What.Type IN ('Account', 'Opportunity')

-- Using TYPEOF (complex polymorphism)
SELECT Id, Subject,
  TYPEOF What
    WHEN Account THEN Name, Industry
    WHEN Opportunity THEN Name, Amount
  END
FROM Task
```

## Multi-Level Relationships

```sql
-- 5 levels up
SELECT Id, Name, Account.Owner.Manager.Name FROM Contact

-- Parent + child in same query
SELECT Id, Name, Account.Name,
  (SELECT Id, Subject FROM Tasks WHERE Status != 'Completed')
FROM Opportunity
```

## Dynamic Date Ranges

```sql
-- Rolling 90 days
SELECT Id, Name FROM Opportunity 
WHERE CreatedDate = LAST_N_DAYS:90

-- Specific fiscal period
SELECT Id, Name FROM Opportunity 
WHERE CloseDate = THIS_FISCAL_QUARTER

-- Between two dates
SELECT Id, Name FROM Opportunity 
WHERE CloseDate >= 2024-01-01 AND CloseDate <= 2024-03-31
```

## Aggregate Edge Cases

```sql
-- GROUP BY with HAVING (filter aggregates)
SELECT StageName, SUM(Amount) total 
FROM Opportunity 
GROUP BY StageName 
HAVING SUM(Amount) > 100000

-- COUNT_DISTINCT
SELECT COUNT_DISTINCT(AccountId) unique_accounts FROM Opportunity

-- GROUP BY ROLLUP (subtotals)
SELECT LeadSource, StageName, SUM(Amount) 
FROM Opportunity 
GROUP BY ROLLUP(LeadSource, StageName)
```

## Filtering on Null

```sql
-- Null checks
SELECT Id, Name FROM Opportunity WHERE Amount = null
SELECT Id, Name FROM Opportunity WHERE Amount != null

-- Empty picklists
SELECT Id, Name FROM Opportunity WHERE LeadSource = ''
```

## Text Search

```sql
-- LIKE wildcards
SELECT Id, Name FROM Account WHERE Name LIKE 'Acme%'
SELECT Id, Name FROM Account WHERE Name LIKE '%Corp%'

-- Multiple values
SELECT Id, Name FROM Opportunity 
WHERE StageName IN ('Closed Won', 'Closed Lost')
```

## Record Types

```sql
-- Filter by record type
SELECT Id, Name FROM Opportunity 
WHERE RecordType.DeveloperName = 'Enterprise_Deal'

-- Include record type in results
SELECT Id, Name, RecordType.Name FROM Opportunity
```

## Order and Limit

```sql
-- Top N with NULLS LAST
SELECT Id, Name, Amount FROM Opportunity 
ORDER BY Amount DESC NULLS LAST 
LIMIT 10

-- Offset for pagination
SELECT Id, Name FROM Account 
ORDER BY Name 
LIMIT 100 OFFSET 200
```

## Formula and Calculated Fields

Formula fields are queryable like regular fields:
```sql
SELECT Id, Name, Calculated_ARR__c FROM Opportunity
```

Note: You cannot use formula fields in WHERE for aggregate queries in some contexts.

## Querying Metadata

Use `--use-tooling-api` for metadata:
```bash
sf data query -q "SELECT Id, Name FROM ApexClass WHERE Status = 'Active'" --use-tooling-api
sf data query -q "SELECT Id, DeveloperName FROM CustomObject" --use-tooling-api
sf data query -q "SELECT Id, TableEnumOrId, DeveloperName FROM CustomField" --use-tooling-api
```
