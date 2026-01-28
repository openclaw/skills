# Pinterest API v5 Reference

## Base URL
```
https://api.pinterest.com/v5
```

## Authentication
All API requests require Bearer token:
```
Authorization: Bearer {access_token}
```

## Endpoints

### Pins

#### Get Pin
```
GET /pins/{pin_id}
```

#### List User's Pins
```
GET /pins
?page_size=25
&bookmark={bookmark}
```

### Boards

#### List User's Boards
```
GET /boards
?page_size=25
```

#### Get Board
```
GET /boards/{board_id}
```

#### List Board Pins
```
GET /boards/{board_id}/pins
?page_size=25
```

### Search (Limited)

The v5 API does NOT have public pin search. Options:
1. Search user's own content via `/pins` with filtering
2. Use Ads API for broader search (requires ad account)
3. Use web scraping fallback (this skill's approach)

## Rate Limits

| Tier | Requests/Day |
|------|--------------|
| Standard | 1,000 |
| Partner | 10,000 |
| Enterprise | Custom |

## Response Format

```json
{
  "items": [...],
  "bookmark": "cursor_for_next_page"
}
```

## Common Errors

| Code | Meaning |
|------|---------|
| 401 | Invalid/expired token |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 429 | Rate limit exceeded |
