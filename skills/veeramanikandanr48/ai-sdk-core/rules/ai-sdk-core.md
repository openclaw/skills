---
paths: "**/*.ts", "**/*.tsx", package.json
---

# AI SDK v5/v6 Corrections

Claude's training may reference AI SDK v4 patterns. This project uses **AI SDK v5+**.

## Critical v4→v5 Breaking Changes

### Parameter Renames
```typescript
/* ❌ v4 (Claude may suggest this) */
maxTokens: 500
providerMetadata: { openai: { user: 'user-123' } }

/* ✅ v5 (use this) */
maxOutputTokens: 500
providerOptions: { openai: { user: 'user-123' } }
```

### Tool Definitions
```typescript
/* ❌ v4 */
tools: {
  weather: {
    parameters: z.object({ location: z.string() }),
    execute: async (args) => { /* args.location */ },
  },
}

/* ✅ v5 */
import { tool } from 'ai'
tools: {
  weather: tool({
    inputSchema: z.object({ location: z.string() }),
    execute: async ({ location }) => { /* input.location */ },
  }),
}
```

### Multi-Step Execution
```typescript
/* ❌ v4 */
maxSteps: 5

/* ✅ v5 */
import { stopWhen, stepCountIs } from 'ai'
stopWhen: stepCountIs(5)
```

### Message Types
```typescript
/* ❌ v4 */
import { CoreMessage } from 'ai'
convertToCoreMessages(messages)

/* ✅ v5 */
import { ModelMessage } from 'ai'
convertToModelMessages(messages)
```

### Package Imports
```typescript
/* ❌ v4 */
import { ... } from 'ai/rsc'
import { ... } from 'ai/react'

/* ✅ v5 */
import { ... } from '@ai-sdk/rsc'
import { ... } from '@ai-sdk/react'
```

## Cloudflare Workers Startup Fix

```typescript
/* ❌ Causes >270ms startup (exceeds 400ms limit) */
import { createWorkersAI } from 'workers-ai-provider'
const workersai = createWorkersAI({ binding: env.AI })

/* ✅ Lazy initialization inside handler */
app.post('/chat', async (c) => {
  const { createWorkersAI } = await import('workers-ai-provider')
  const workersai = createWorkersAI({ binding: c.env.AI })
})
```

## Model Names (2025)

```typescript
/* OpenAI */
openai('gpt-5')         // Latest
openai('gpt-5.1')       // Improved

/* Anthropic */
anthropic('claude-sonnet-4-5-20250929')  // Latest Sonnet
anthropic('claude-opus-4-5-20251101')    // Latest Opus

/* Google */
google('gemini-2.5-pro')
google('gemini-2.5-flash')
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `maxTokens` | `maxOutputTokens` |
| `providerMetadata` | `providerOptions` |
| `parameters` (in tools) | `inputSchema` |
| `args` (in execute) | destructured input `{ location }` |
| `maxSteps: 5` | `stopWhen: stepCountIs(5)` |
| `CoreMessage` | `ModelMessage` |
| `from 'ai/rsc'` | `from '@ai-sdk/rsc'` |
| `ToolExecutionError` | `tool-error` content parts |
