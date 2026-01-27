# WHOOP OAuth 2.0 Setup

## Quick Setup

1. **Register your application** at https://developer.whoop.com
   - Sign in with your WHOOP account
   - Create a new application
   - Note your `client_id` and `client_secret`
   - Set redirect URI (e.g., `http://localhost:8080/callback`)

2. **Save credentials locally**:
   ```bash
   mkdir -p ~/.whoop
   cat > ~/.whoop/credentials.json <<EOF
   {
     "client_id": "YOUR_CLIENT_ID",
     "client_secret": "YOUR_CLIENT_SECRET"
   }
   EOF
   chmod 600 ~/.whoop/credentials.json
   ```

## Authorization Flow

### Step 1: Direct user to authorization URL

```
https://api.prod.whoop.com/oauth/oauth2/auth?
  client_id=YOUR_CLIENT_ID
  &redirect_uri=YOUR_REDIRECT_URI
  &response_type=code
  &scope=read:recovery read:sleep read:cycles read:workout read:profile read:body_measurement
```

**Available Scopes:**
- `read:recovery` - Recovery scores, HRV, resting HR
- `read:cycles` - Daily strain data
- `read:workout` - Workout and activity data
- `read:sleep` - Sleep metrics and stages
- `read:profile` - User name and email
- `read:body_measurement` - Height, weight, max HR

### Step 2: User authorizes and is redirected

After authorization, WHOOP redirects to your `redirect_uri` with a code:
```
https://yourapp.com/callback?code=AUTHORIZATION_CODE
```

### Step 3: Exchange code for tokens

```python
from whoop_client import WhoopClient

client = WhoopClient()
client.authenticate("AUTHORIZATION_CODE", "YOUR_REDIRECT_URI")
```

This exchanges the code for:
- **Access token**: Used for API requests (expires after ~1 hour)
- **Refresh token**: Used to get new access tokens

Tokens are automatically saved to `~/.whoop/token.json`.

## Token Management

### Automatic Refresh

The `WhoopClient` automatically refreshes expired access tokens using the refresh token when a 401 response is received.

### Manual Refresh

```python
client._refresh_access_token()
```

### Token Storage

Tokens are stored in `~/.whoop/token.json`:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "updated_at": "2026-01-27T12:00:00"
}
```

## Testing Authorization

After setting up OAuth, test with:

```bash
python3 get_profile.py
```

If successful, you'll see your user profile and body measurements.

## Troubleshooting

### "Credentials not found"
Create `~/.whoop/credentials.json` with your client_id and client_secret.

### "Not authenticated"
Run `client.authenticate(code)` with a valid authorization code first.

### "401 Unauthorized" after token refresh fails
Your refresh token may have expired. Re-authorize from Step 1.

### Rate Limits
WHOOP API has rate limits. If you hit them, the API will return 429 with a `Retry-After` header.

## Security Notes

- Never commit credentials or tokens to version control
- Store credentials with restricted permissions (`chmod 600`)
- Refresh tokens are long-lived but can be revoked by the user
- Access tokens expire after ~1 hour and must be refreshed
