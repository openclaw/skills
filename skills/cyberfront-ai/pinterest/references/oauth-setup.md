# Pinterest OAuth Setup

## 1. Create Developer App

1. Go to https://developers.pinterest.com/apps/
2. Click "Create app"
3. Fill in app details (name, description)
4. Note your **App ID** and **App Secret**

## 2. Configure Redirect URI

Add a redirect URI for OAuth flow:
- For local testing: `http://localhost:8000/callback`
- For production: your actual callback URL

## 3. Get Access Token

### Option A: OAuth Playground (Quick Testing)

1. Go to https://developers.pinterest.com/tools/access_token/
2. Select scopes: `boards:read`, `pins:read`
3. Click "Generate token"
4. Copy the access token

### Option B: Full OAuth Flow

```python
# Step 1: Redirect user to authorize
AUTH_URL = "https://www.pinterest.com/oauth/"
params = {
    "response_type": "code",
    "client_id": YOUR_APP_ID,
    "redirect_uri": YOUR_REDIRECT_URI,
    "scope": "boards:read,pins:read",
    "state": "random_state_string"
}

# Step 2: Exchange code for token
TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"
data = {
    "grant_type": "authorization_code",
    "code": CODE_FROM_CALLBACK,
    "redirect_uri": YOUR_REDIRECT_URI
}
# POST with Basic Auth (client_id:client_secret)
```

## 4. Set Environment Variable

```bash
export PINTEREST_ACCESS_TOKEN="pina_YOUR_TOKEN_HERE"
```

## Token Scopes

| Scope | Access |
|-------|--------|
| `boards:read` | Read user's boards |
| `pins:read` | Read user's pins |
| `boards:write` | Create/edit boards |
| `pins:write` | Create/edit pins |

## Token Expiration

- Access tokens expire after 30 days
- Refresh tokens can be used to get new access tokens
- Store refresh tokens securely
