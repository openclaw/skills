# Accounts API

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/accounts` | List accounts |
| `PUT` | `/v1/accounts/{accountId}` | Update account |
| `DELETE` | `/v1/accounts/{accountId}` | Disconnect account |
| `GET` | `/v1/accounts/health` | Check all accounts health |
| `GET` | `/v1/accounts/{accountId}/health` | Check specific account health |
| `GET` | `/v1/accounts/follower-stats` | Get follower statistics |

## Platform-Specific Account Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `PUT` | `/v1/accounts/{accountId}/facebook-page` | Update selected Facebook page |
| `GET` | `/v1/accounts/{accountId}/gmb-reviews` | Get Google Business reviews |
| `GET` | `/v1/accounts/{accountId}/linkedin-organizations` | List LinkedIn organizations |
| `PUT` | `/v1/accounts/{accountId}/linkedin-organization` | Switch personal/organization mode |
| `GET` | `/v1/accounts/{accountId}/linkedin-mentions` | Get LinkedIn mentions |
| `GET` | `/v1/accounts/{accountId}/linkedin-aggregate-analytics` | Get LinkedIn analytics |
| `GET` | `/v1/accounts/{accountId}/linkedin-post-analytics` | Get LinkedIn post analytics |
| `GET` | `/v1/accounts/{accountId}/pinterest-boards` | List Pinterest boards |
| `PUT` | `/v1/accounts/{accountId}/pinterest-boards` | Set default Pinterest board |
| `GET` | `/v1/accounts/{accountId}/reddit-subreddits` | List user's subreddits |
| `PUT` | `/v1/accounts/{accountId}/reddit-subreddits` | Set default subreddit |

## List Accounts

```bash
curl "https://getlate.dev/api/v1/accounts?profileId=PROFILE_ID" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Account Health Check

```bash
curl "https://getlate.dev/api/v1/accounts/health" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Response indicates if tokens are valid or need reconnection.

## Account Groups

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/account-groups` | List account groups |
| `POST` | `/v1/account-groups` | Create account group |
| `PUT` | `/v1/account-groups/{groupId}` | Update account group |
| `DELETE` | `/v1/account-groups/{groupId}` | Delete account group |

Account groups let you organize accounts for bulk posting operations.
