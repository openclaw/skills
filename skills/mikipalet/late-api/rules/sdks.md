# API Usage

Use the Late API directly with HTTP requests:

```typescript
const BASE_URL = 'https://getlate.dev/api/v1';

async function lateApi(endpoint: string, options: RequestInit = {}) {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${process.env.LATE_API_KEY}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'API request failed');
  }

  return response.json();
}

// Usage
const posts = await lateApi('/posts');
const newPost = await lateApi('/posts', {
  method: 'POST',
  body: JSON.stringify({
    content: 'Hello!',
    platforms: [{ platform: 'twitter', accountId: 'acc_123' }],
    publishNow: true
  })
});
```
