---
name: oauth-helper
description: |
  Automate OAuth login flows with user confirmation via Telegram.
  Supports 7 providers: Google, Apple, Microsoft, GitHub, Discord, WeChat, QQ.
  
  Features:
  - Auto-detect available OAuth options on login pages
  - Ask user to choose via Telegram when multiple options exist
  - Confirm before authorizing
  - Handle account selection and consent pages automatically
---

# OAuth Helper

Automate OAuth login with Telegram confirmation. Supports 7 major providers.

## Supported Providers

| Provider | Status | Detection Domain |
|----------|--------|------------------|
| Google | ✅ | accounts.google.com |
| Apple | ✅ | appleid.apple.com |
| Microsoft | ✅ | login.microsoftonline.com, login.live.com |
| GitHub | ✅ | github.com/login/oauth |
| Discord | ✅ | discord.com/oauth2 |
| WeChat | ✅ | open.weixin.qq.com |
| QQ | ✅ | graph.qq.com |

## Prerequisites

1. Clawd browser logged into the OAuth providers (one-time setup)
2. Telegram channel configured

## Core Workflow

### Flow A: Login Page with Multiple OAuth Options

When user requests to login to a website:

```
1. Open website login page
2. Scan page for available OAuth buttons
3. Send Telegram message:
   "🔐 [Site] supports these login methods:
    1️⃣ Google
    2️⃣ Apple  
    3️⃣ GitHub
    Reply with number to choose"
4. Wait for user reply (60s timeout)
5. Click the selected OAuth button
6. Enter Flow B
```

### Flow B: OAuth Authorization Page

When on an OAuth provider's page:

```
1. Detect OAuth page type (by URL)
2. Extract target site info
3. Send Telegram: "🔐 [Site] requests [Provider] login. Confirm? Reply yes"
4. Wait for "yes" (60s timeout)
5. Execute provider-specific click sequence
6. Wait for redirect back to original site
7. Send: "✅ Login successful!"
```

## Detection Patterns

### Google
```
URL patterns:
- accounts.google.com/o/oauth2
- accounts.google.com/signin/oauth
- accounts.google.com/v3/signin
```

### Apple
```
URL patterns:
- appleid.apple.com/auth/authorize
- appleid.apple.com/auth/oauth2
```

### Microsoft
```
URL patterns:
- login.microsoftonline.com/common/oauth2
- login.microsoftonline.com/consumers
- login.live.com/oauth20
```

### GitHub
```
URL patterns:
- github.com/login/oauth/authorize
- github.com/login
- github.com/sessions/two-factor
```

### Discord
```
URL patterns:
- discord.com/oauth2/authorize
- discord.com/login
- discord.com/api/oauth2
```

### WeChat
```
URL patterns:
- open.weixin.qq.com/connect/qrconnect
- open.weixin.qq.com/connect/oauth2
```

### QQ
```
URL patterns:
- graph.qq.com/oauth2.0/authorize
- ssl.xui.ptlogin2.qq.com
- ui.ptlogin2.qq.com
```

## Click Sequences by Provider

### Google
```
Account selector: [data-identifier], .JDAKTe
Auth buttons: button:has-text("Allow"), button:has-text("Continue")
```

### Apple
```
Email input: input[type="email"], #account_name_text_field
Password: input[type="password"], #password_text_field  
Continue: button#sign-in, button:has-text("Continue")
Trust device: button:has-text("Trust")
```

### Microsoft
```
Account selector: .table-row[data-test-id]
Email input: input[name="loginfmt"]
Password: input[name="passwd"]
Next: button#idSIButton9
Accept: button#idBtn_Accept
```

### GitHub
```
Email: input#login_field
Password: input#password
Sign in: input[type="submit"]
Authorize: button[name="authorize"]
2FA: input#app_totp
```

### Discord
```
Email: input[name="email"]
Password: input[name="password"]
Login: button[type="submit"]
Authorize: button:has-text("Authorize")
```

### WeChat
```
Method: QR code scan
- Screenshot QR code to user
- Wait for mobile scan confirmation
- Detect page redirect
```

### QQ
```
Method: QR code or password login
QR: Screenshot to user
Password mode:
  - Switch: a:has-text("密码登录")
  - Username: input#u
  - Password: input#p
  - Login: input#login_button
```

## OAuth Button Detection

Scan login pages for these selectors:

| Provider | Selectors | Common Text |
|----------|-----------|-------------|
| Google | `[data-provider="google"]`, `.google-btn` | "Continue with Google" |
| Apple | `[data-provider="apple"]`, `.apple-btn` | "Sign in with Apple" |
| Microsoft | `[data-provider="microsoft"]` | "Sign in with Microsoft" |
| GitHub | `[data-provider="github"]` | "Continue with GitHub" |
| Discord | `[data-provider="discord"]` | "Login with Discord" |
| WeChat | `.wechat-btn`, `img[src*="wechat"]` | "WeChat Login" |
| QQ | `.qq-btn`, `img[src*="qq"]` | "QQ Login" |

## One-Time Setup

Login to each provider in clawd browser:

```bash
# Google
browser action=navigate profile=clawd url=https://accounts.google.com

# Apple
browser action=navigate profile=clawd url=https://appleid.apple.com

# Microsoft  
browser action=navigate profile=clawd url=https://login.live.com

# GitHub
browser action=navigate profile=clawd url=https://github.com/login

# Discord
browser action=navigate profile=clawd url=https://discord.com/login

# WeChat/QQ - Use QR scan, no pre-login needed
```

## Error Handling

- No "yes" reply → Cancel and notify user
- 2FA required → Prompt user to enter code manually
- QR timeout → Re-screenshot new QR code
- Login failed → Screenshot and send to user for debugging

## Usage Example

```
User: Login to Kaggle for me

Agent:
1. Navigate to kaggle.com/account/login
2. Detect Google/Facebook/Yahoo options
3. Send: "🔐 Kaggle supports:
   1️⃣ Google
   2️⃣ Facebook
   3️⃣ Yahoo
   Reply number to choose"
4. User replies: 1
5. Click Google login
6. Detect Google OAuth page
7. Send: "🔐 Kaggle requests Google login. Confirm? Reply yes"
8. User replies: yes
9. Select account, click Continue
10. Send: "✅ Logged into Kaggle!"
```

## Version History

- v1.0.0 - Initial release with 7 OAuth providers
