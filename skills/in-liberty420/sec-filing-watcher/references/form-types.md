# SEC Form Types Reference

Common form types to monitor:

## Financial Reports

| Form | Description | Frequency |
|------|-------------|-----------|
| **10-K** | Annual report | Yearly |
| **10-Q** | Quarterly report | Quarterly |
| **10-K/A** | Amended annual report | As needed |
| **10-Q/A** | Amended quarterly report | As needed |

## Current Events

| Form | Description | When Filed |
|------|-------------|------------|
| **8-K** | Current report (material events) | Within 4 days of event |
| **8-K/A** | Amended current report | As needed |

Common 8-K items:
- 1.01: Entry into material agreement
- 2.01: Acquisition/disposition of assets
- 2.02: Results of operations (earnings)
- 4.01: Change in accountant
- 5.02: Director/officer changes
- 7.01: Regulation FD disclosure
- 8.01: Other events

## Insider Transactions

| Form | Description | When Filed |
|------|-------------|------------|
| **3** | Initial beneficial ownership | Within 10 days of becoming insider |
| **4** | Change in beneficial ownership | Within 2 business days |
| **5** | Annual statement of ownership | Within 45 days of fiscal year end |

## Institutional Holdings

| Form | Description | Frequency |
|------|-------------|-----------|
| **13F** | Institutional holdings (>$100M AUM) | Quarterly |
| **13D** | Beneficial ownership (>5%, active) | Within 10 days |
| **13G** | Beneficial ownership (>5%, passive) | Within 45 days |

## Offerings & Registration

| Form | Description |
|------|-------------|
| **S-1** | IPO registration |
| **S-3** | Shelf registration |
| **424B** | Prospectus |
| **D** | Private placement |

## Recommended Watchlist Configs

**General investor:**
```json
{
  "formTypes": ["10-K", "10-Q", "8-K"]
}
```

**Track insiders:**
```json
{
  "formTypes": ["4", "3", "5"]
}
```

**Comprehensive:**
```json
{
  "formTypes": ["10-K", "10-Q", "8-K", "4", "13F", "S-1"]
}
```
