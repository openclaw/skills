# AbuseIPDB API Reference

Base URL: `https://api.abuseipdb.com/api/v2`

## Authentication

```
Key: YOUR_API_KEY
```

Header: `Key: <api-key>`
Accept: `application/json`

## Report an IP

```
POST /report
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| ip | Yes | IP to report |
| categories | Yes | Comma-separated category IDs |
| comment | No | Description of attack |

### Categories (common)

| ID | Category |
|----|----------|
| 18 | Brute-Force |
| 22 | SSH |
| 15 | Hacking |
| 14 | Port Scan |

### Example

```bash
curl -s https://api.abuseipdb.com/api/v2/report \
  -H "Key: $ABUSEIPDB_KEY" \
  -H "Accept: application/json" \
  --data-urlencode "ip=1.2.3.4" \
  -d "categories=18,22" \
  --data-urlencode "comment=SSH brute-force (fail2ban)"
```

## Check an IP

```
GET /check?ipAddress=1.2.3.4
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| ipAddress | Yes | IP to check |
| maxAgeInDays | No | 1-365 (default 30) |

### Example

```bash
curl -s "https://api.abuseipdb.com/api/v2/check?ipAddress=1.2.3.4&maxAgeInDays=90" \
  -H "Key: $ABUSEIPDB_KEY" \
  -H "Accept: application/json"
```

Response includes `abuseConfidenceScore` (0-100), `totalReports`, `countryCode`, `isp`.

## Rate Limits (free tier)

- Check: 1000/day
- Report: 1000/day
- Blacklist: 5/day
